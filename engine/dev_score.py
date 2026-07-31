"""
DEV PILLAR v1: player development graded from the Pipeline top-100 archive.

The archive: MLB Pipeline preseason top-100s, 2011-2026 (2011 was a top-50),
1,548 rank-rows, 823 players, pulled from data-graph.mlb.com. Holding org per
list is derived from minor-league season rosters (statsapi season splits
mapped to parent orgs), NOT from Pipeline, so attribution is ours.

Value scale: V(rank) = expected surplus value of a top-100 prospect, in wins,
log-interpolated between published-surplus-study anchor points. Marks, not
realized wins; DEV grades scouting-and-development skill at inflating marks.

Event rules (documented, v1):
  ENTRY   first list appearance. credit = V(rank) - implied acquisition cost,
          to the org holding the player at that list. Implied cost: the org's
          own draft pick -> D(overall) pick-value curve; own international
          amateur signing -> 0.5; acquired from another org -> 1.0 (you paid
          prospect price; development after acquisition still accrues).
          INHERITED SCREEN: the credit lands on the club's current regime
          only if the player joined the org during that regime; a prospect
          developed to the list under a predecessor is inherited work and
          earns the new regime nothing at entry (later rank moves on their
          watch still count).
  MARK    consecutive lists: credit = V(new rank) - V(old rank) to the org
          holding at the new list. A traded prospect's future rises/falls
          accrue to the acquiring org; the seller's return is already graded
          in the trade channel.
  EXIT    leaves the list. Graduated (MLB debut by the season after the last
          list): neutral, the value handed to the big-league ledger. Fell off
          without debuting: charge -0.6 x V(last rank) to the holding org
          (dampened because some fall-offs still surface later).
  OPEN    still on the 2026 list: open position marked at V(rank); reported
          as current farm value, not yet graded.

Regime attribution: event date is Feb 1 of the list year; credited only if
the club's current regime had started by then. DEV per season -> letter.
"""
import json, math, sqlite3
from collections import defaultdict

V_ANCHOR = [(1,8.0),(3,7.0),(5,6.5),(10,5.5),(15,4.8),(25,4.0),(40,3.2),
            (50,2.8),(75,2.0),(100,1.5)]
D_ANCHOR = [(1,5.0),(5,3.5),(10,2.8),(20,2.0),(30,1.6),(60,1.0),(100,0.7),
            (200,0.45),(400,0.3)]
def interp(anchors, x):
    if x <= anchors[0][0]: return anchors[0][1]
    if x >= anchors[-1][0]: return anchors[-1][1]
    for (x0,y0),(x1,y1) in zip(anchors, anchors[1:]):
        if x0 <= x <= x1:
            f = (math.log(x)-math.log(x0))/(math.log(x1)-math.log(x0))
            return y0 + f*(y1-y0)
def V(rank): return interp(V_ANCHOR, rank)
def D(overall): return interp(D_ANCHOR, overall)

NA_DRAFT = {"USA","Canada","Puerto Rico","Guam","U.S. Virgin Islands",
            "Virgin Islands","American Samoa","Northern Mariana Islands"}

ranks = json.load(open("/home/claude/prospect_ranks.json"))
orgs = json.load(open("/home/claude/prospect_orgs.json"))
cfg = json.load(open("/home/claude/regimes.json"))
REG = {r["teamId"]: r for r in cfg["regimes"]}
con = sqlite3.connect("/home/claude/ledger.sqlite"); con.row_factory = sqlite3.Row

# draft book: pid -> (year, overall, team name)
draft = {}
for r in con.execute("select person_id, year, pick_overall, team from draft_picks where person_id is not null"):
    draft[r["person_id"]] = (int(r["year"]), int(r["pick_overall"] or 999), r["team"])
TEAMNAME2ID = {r["team"]: r["teamId"] for r in cfg["regimes"]}
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
def name2tid(nm):
    if nm in TEAMNAME2ID: return TEAMNAME2ID[nm]
    for tid, names in ALIAS.items():
        if nm in names: return tid
    return None

by_pid = defaultdict(dict)   # pid -> {year: rank}
meta = {}
for r in ranks:
    by_pid[str(r["pid"])][r["year"]] = r["rank"]
    meta[str(r["pid"])] = r

def holder(pid, y):
    """org holding player at the year-y preseason list: last org of season
    y-1, else first org of season y."""
    rec = orgs.get(pid, {})
    o = rec.get("orgs", {})
    prev = o.get(str(y-1))
    if prev: return prev[-1]
    cur = o.get(str(y))
    if cur: return cur[0]
    return None

def first_org(pid):
    rec = orgs.get(pid, {}).get("orgs", {})
    if not rec: return None
    y = min(int(k) for k in rec)
    return rec[str(y)][0]

def debut_year(pid):
    d = orgs.get(pid, {}).get("debut")
    return int(d[:4]) if d else None

events = []  # (teamId, list_year, kind, credit, pid, note)
farm_now = defaultdict(float); farm_now_n = defaultdict(int)
flows = defaultdict(lambda: defaultdict(int))  # teamId -> counters

for pid, ymap in by_pid.items():
    ys = sorted(ymap)
    nm = meta[pid]["name"]
    # ENTRY
    y0 = ys[0]; h0 = holder(pid, y0)
    if h0:
        dr = draft.get(pid)
        if dr and name2tid(dr[2]) == h0 and dr[0] >= y0 - 6:
            implied = D(dr[1]); how = f"own draft pick #{dr[1]} ({dr[0]})"
        elif (meta[pid].get("bc") not in NA_DRAFT) and first_org(pid) == h0 and not dr:
            implied = 0.5; how = "own international signing"
        elif dr and name2tid(dr[2]) != h0:
            implied = 1.0; how = "acquired as prospect"
        elif first_org(pid) != h0:
            implied = 1.0; how = "acquired as prospect"
        else:
            implied = 0.7; how = "originated in org"
        cr = V(ymap[y0]) - implied
        # inherited screen: when did the player join the holding org?
        oyrs = [int(k) for k, v in orgs.get(pid, {}).get("orgs", {}).items() if h0 in v]
        join_y = min(oyrs) if oyrs else y0
        events.append((h0, y0, "entry", cr, pid,
                       f"{nm} enters top 100 at #{ymap[y0]} ({how})", join_y))
        flows[h0]["developed_in"] += 1
    # MARKS
    for ya, yb in zip(ys, ys[1:]):
        hb = holder(pid, yb); ha = holder(pid, ya)
        if hb:
            dv = V(ymap[yb]) - V(ymap[ya])
            events.append((hb, yb, "mark", dv, pid, f"{nm} #{ymap[ya]} -> #{ymap[yb]}", None))
        if ha and hb and ha != hb:
            flows[ha]["traded_out_ranked"] += 1
    # EXIT
    yl = ys[-1]
    if yl < 2026:
        hl = holder(pid, yl + 1) or holder(pid, yl)
        dy = debut_year(pid)
        if dy and dy <= yl + 1:
            if hl: flows[hl]["graduated"] += 1
        else:
            if hl:
                ch = -0.6 * V(ymap[yl])
                events.append((hl, yl + 1, "bust", ch, pid, f"{nm} fell off (last #{ymap[yl]}, no debut)", None))
                flows[hl]["fell_off"] += 1
    else:
        h = holder(pid, 2026)
        if h:
            farm_now[h] += V(ymap[2026]); farm_now_n[h] += 1

# regime attribution
res = json.load(open("/home/claude/sweep_results.json"))
by_id = {r["teamId"]: r for r in res}
def grade(adj):
    # bands sized to the observed league spread of dev rates (wider than the
    # acquisition channels; entry credits are lumpy)
    for thr, g in [(3.8,80),(2.5,75),(1.6,70),(1.0,65),(0.55,60),(0.2,55),
                   (-0.3,50),(-1.0,45),(-1.8,40),(-2.9,35)]:
        if adj >= thr: return g
    return 30

pernet = defaultdict(float); pertops = defaultdict(list); pern = defaultdict(int)
inherited = 0
for tid, y, kind, cr, pid, note, join_y in events:
    reg = REG.get(tid)
    if not reg: continue
    if f"{y}-02-01" < reg["start"]: continue
    if kind == "entry" and join_y is not None and join_y < int(reg["start"][:4]):
        inherited += 1
        continue  # predecessor's development work
    pernet[tid] += cr; pern[tid] += 1
    pertops[tid].append((cr, y, kind, note))
print(f"inherited entries screened out: {inherited}")

# DEV is positive-sum by construction (the league creates prospect value
# every year), so the expectation is the league-average development rate:
# grade the per-season rate RELATIVE to the league mean, over seasons that
# overlap the archive (2011+), not full tenure.
def dev_seasons(tid):
    start = REG[tid]["start"]
    s = int(start[:4]) + (int(start[5:7]) - 1) / 12
    return max(1.0, 2026.6 - max(s, 2011.1))

tot_net = sum(pernet.get(r["teamId"], 0.0) for r in res)
tot_sea = sum(dev_seasons(r["teamId"]) for r in res)
league_rate = tot_net / tot_sea
print(f"league development rate: {league_rate:+.2f} wins of prospect value per club-season\n")

print(f"{'team':<6}{'DEV net':>9}{'/seas':>7}{'vs lg':>7}{'ev':>5}{'farm now':>10}   top dev credit")
for r in res:
    tid = r["teamId"]
    net = pernet.get(tid, 0.0)
    ds = dev_seasons(tid)
    nps = net / ds
    adj = nps - league_rate
    tops = sorted(pertops.get(tid, []), key=lambda t: -abs(t[0]))
    r["dev"] = dict(net=round(net,1), g=grade(adj), n=pern.get(tid,0),
                    seasons=round(ds,1), rate=round(nps,2), lgRate=round(league_rate,2),
                    farmNow=round(farm_now.get(tid,0.0),1), farmN=farm_now_n.get(tid,0),
                    flows=dict(flows.get(tid,{})))
    r["dev_tops"] = [dict(d=f"{y}-02-01", ch="dev", net=round(cr,1), h=note)
                     for cr, y, kind, note in tops[:6]]
    best = f"{tops[0][3][:44]} ({tops[0][0]:+.1f})" if tops else "-"
    print(f"{r['abbr']:<6}{net:>+9.1f}{nps:>+7.2f}{adj:>+7.2f}{pern.get(tid,0):>5}{farm_now.get(tid,0.0):>10.1f}   {best}")

json.dump(res, open("/home/claude/sweep_results.json", "w"), indent=1)
print("\nmerged dev into sweep_results.json")
print("league DEV sum:", round(sum(pernet.values()),1), "| events attributed:", sum(pern.values()), "of", len(events))
