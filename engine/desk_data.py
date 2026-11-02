"""
DEAL DESK data pack: everything the in-page evaluator needs, compact.
Writes desk_data.json:
  players: [name, pid, team abbr (2026 club or prospect org), isPit,
            age2026, w2024, w2025, w2026, ctrlDefault, rank2026]
  curves:  aging curves + pop mean (proj_curves.json)
  market:  dollars-per-win table, control-bucket price ratios + bust rates,
           star-rental rate, unranked prospect EV
  slot:    draft pick slot-expectation anchors
  teams:   {abbr: 2026 win total}
  deals:   compact 1998-2023 archive [yr, ab, ph, ck, po, recv, paid, who]
"""
import json, sqlite3
from collections import defaultdict

LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
AGES = json.load(open("/work/ages.json"))
POS = json.load(open("/work/positions.json"))
POS.update(json.load(open("/work/positions2.json")))  # canonical primaryPosition refetch (v4.4)
PITPOS = {"RHP", "LHP", "SP", "RP", "P"}
PC = json.load(open("/work/proj_curves.json"))
RM = json.load(open("/work/rental_market.json"))
cfg = json.load(open("/work/regimes.json"))
ABBR_BY_NAME = {}
for r in cfg["regimes"]:
    ABBR_BY_NAME[r["team"]] = r["abbr"]
    for al in cfg["aliases"].get(str(r["teamId"]), []):
        ABBR_BY_NAME[al] = r["abbr"]

RANKS = {}
ORGS = {}
for rr in json.load(open("/work/prospect_ranks.json")):
    if rr["year"] in (2025, 2026):
        RANKS[str(rr["pid"])] = rr["rank"]
        ORGS[str(rr["pid"])] = rr.get("name")
try:
    porgs = json.load(open("/work/prospect_orgs.json"))
except Exception:
    porgs = {}

BY = {}
for pid, rec in LVM.items():
    d = defaultdict(float)
    last_team = None; last_y = 0
    for (y, tm, v) in rec["rows"]:
        d[y] += v
        if y >= last_y: last_y, last_team = y, tm
    BY[pid] = (dict(d), last_team, rec["name"])

players = []
for pid, (d, last_team, name) in BY.items():
    recent = any(y in d for y in (2024, 2025, 2026))
    ranked = str(pid) in RANKS
    if not (recent or ranked): continue
    mlb_seasons = sum(1 for v in d.values() if abs(v) > 0.05)
    ctrl = max(1, min(6, 6 - mlb_seasons))
    age = 2026 - AGES.get(str(pid), 2000)
    ab = ABBR_BY_NAME.get(last_team or "", "")
    players.append([name, pid, ab, 1 if POS.get(str(pid)) in PITPOS else 0,
                    age if 16 < age < 50 else 27,
                    round(d.get(2024, 0), 1), round(d.get(2025, 0), 1), round(d.get(2026, 0), 1),
                    ctrl, RANKS.get(str(pid), 0), mlb_seasons])  # mlb_seasons moved to idx 11 below
players.sort(key=lambda p: -(abs(p[5]) + abs(p[6]) + abs(p[7])))
# reorder tail fields: durability at index 10 (from pt_fetch.py; 1.0 default),
# true MLB seasons (service proxy, unclamped) at index 11
try:
    DUR = json.load(open("/work/durability.json"))
except Exception:
    DUR = {}
try:
    PT_RAW = json.load(open("/work/playtime.json"))
except Exception:
    PT_RAW = {}
for p in players:
    svc = p.pop(10)                      # mlb_seasons appended during build
    p.append(DUR.get(str(p[1]), 1.0))    # idx 10: durability
    p.append(svc)                        # idx 11: MLB seasons played
    pp = POS.get(str(p[1]))
    p.append("C" if pp == "C" else "IF" if pp in ("1B","2B","3B","SS") else
             "OF" if pp in ("LF","CF","RF","OF","DH") else "SP" if pp == "SP" else
             "RP" if pp == "RP" else "P")   # idx 12: position group
    # idx 13: depth-chart position. RHP/LHP/P resolved SP vs RP by most
    # recent observed workload (IP/G >= 3 = starter); no record -> RP
    raw = pp or ("P" if p[3] else "OF")
    if raw in ("RHP", "LHP", "P", "TWP"):
        rec = PT_RAW.get(str(p[1]), {})
        role = "RP"
        for season in ("2026", "2025", "2024"):
            ip, g = (rec.get(season) or [0, 0, 0])[1], (rec.get(season) or [0, 0, 0])[2]
            if ip > 0 and g > 0: role = "SP" if ip / g >= 3.0 else "RP"; break
        raw = role
    p.append(raw)
    # idx 14: pedigree (v4.4) - best season of the last five, decayed 0.88/yr,
    # so a star coming off a down platform year still reads as a star
    dd = BY[p[1]][0]
    p.append(round(max(dd.get(2026 - k, 0.0) * (0.88 ** k) for k in range(5)), 2))
print("desk players:", len(players), "| with durability:", sum(1 for p in players if p[10] != 1.0))

# resolve org for ranked prospects with no MLB track (no value rows -> no team abbr)
import urllib.request as _ur, time as _t
TID2AB_ALL = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
need = [p for p in players if not p[2] and p[9]]
for i in range(0, len(need), 50):
    chunk = need[i:i+50]
    ids = ",".join(str(p[1]) for p in chunk)
    try:
        d = json.load(_ur.urlopen(f"https://statsapi.mlb.com/api/v1/people?personIds={ids}&hydrate=currentTeam", timeout=40))
        bypid = {pp["id"]: pp.get("currentTeam", {}) for pp in d.get("people", [])}
        for p in chunk:
            ct = bypid.get(p[1], {})
            org = ct.get("parentOrgId") or (ct.get("id") if ct.get("id") in TID2AB_ALL else None)
            if org in TID2AB_ALL: p[2] = TID2AB_ALL[org]
    except Exception as e:
        print("prospect org fetch failed:", e)
    _t.sleep(0.5)
print("prospect orgs resolved:", sum(1 for p in need if p[2]), "of", len(need))

# team 2026 win totals
import urllib.request, time
def get(u, tries=3):
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=40))
        except Exception: time.sleep(2+2*a)
    return {}
TID2AB = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
teams = {}
d = get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason")
for g in d.get("records", []):
    for t in g.get("teamRecords", []):
        ab = TID2AB.get(t["team"]["id"])
        if ab: teams[ab] = t.get("wins", 81)

# ---- contract book with platform context and realized outcomes ----
import csv, unicodedata, sys
sys.path.insert(0, "/work")
from contracts_recent import RECENT
def norm(nm):
    x = unicodedata.normalize("NFKD", nm or "").encode("ascii", "ignore").decode()
    return x.lower().replace(".", "").replace(" jr", "").strip()
NAME2PIDS = defaultdict(list)
for pid, (d, lt, name) in BY.items():
    NAME2PIDS[norm(name)].append(pid)
TID2AB2 = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
TEAMNAMES = {r["teamId"]: set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in cfg["regimes"]}
def short_to_tid(short):
    for r in cfg["regimes"]:
        names = TEAMNAMES[r["teamId"]]
        if any(short and short.lower() in nm.lower() for nm in names):
            return r["teamId"]
    return None
raw_contracts = []
with open("/work/repo/data/contracts_espn.csv") as f:
    for row in csv.DictReader(f):
        tid = short_to_tid(row["to_team"])
        if tid: raw_contracts.append((int(row["offseason"]), row["player"], tid, int(row["years"]), float(row["total_m"]), 0))
AB2TID = {r["abbr"]: r["teamId"] for r in cfg["regimes"]}
for off, pl, ab, yrs, tot in RECENT:
    raw_contracts.append((off, pl, AB2TID[ab], yrs, float(tot), 0))
# extensions (contracts_ext.EXT): big guaranteed money the FA book never sees.
# A spring signing (month <= 3) covers that season (off = year-1); later
# signings start the next season. CBT value used where it diverges (deferrals).
from contracts_ext import EXT
for (dt, pl, ab, yrs, tot, cbt) in EXT:
    y, m = int(dt[:4]), int(dt[5:7])
    off = y - 1 if m <= 3 else y
    if ab in AB2TID:
        raw_contracts.append((off, pl, AB2TID[ab], yrs, float(cbt if cbt else tot), 1))
book = []
for (off, pl, tid, yrs, tot, typ) in raw_contracts:
    cands = NAME2PIDS.get(norm(pl), [])
    pid = None
    if len(cands) == 1: pid = cands[0]
    elif len(cands) > 1:
        pid = max(cands, key=lambda p: abs(BY[p][0].get(off, 0)) + abs(BY[p][0].get(off - 1, 0)))
    if pid is None: continue
    d = BY[pid][0]
    plat1 = round(d.get(off, 0), 1)             # platform season
    plat2 = round(d.get(off - 1, 0), 1)         # season before
    age = off - AGES.get(str(pid), 0)
    if not (18 < age < 46): continue
    names = TEAMNAMES.get(tid, set())
    elapsed = min(yrs, 2026 - off)
    realized = round(sum(v for (y, tm, v) in LVM[pid]["rows"]
                         if off + 1 <= y <= off + elapsed and tm in names), 1) if elapsed > 0 else None
    pit = 1 if POS.get(str(pid)) in PITPOS else 0
    pgroup = (lambda p: "C" if p == "C" else "IF" if p in ("1B","2B","3B","SS") else
              "OF" if p in ("LF","CF","RF","OF","DH") else "SP" if p == "SP" else
              "RP" if p == "RP" else "P")(POS.get(str(pid)))
    book.append([pl, off, TID2AB2.get(tid, ""), yrs, round(tot, 1), age, pit, plat1, plat2,
                 realized if realized is not None else "", elapsed, pid, typ, pgroup])
print("contract book rows matched:", len(book), "of", len(raw_contracts))

# ---- 2026-27 winter reality pass (curated, Nov 2026) ----
# Opt-outs and declined options void remaining coverage: these players ARE in
# the 2026-27 class although a book row runs past 2026. Rows keep their
# original terms (comps stay honest); the page excludes these pids from
# forward coverage and this script excludes their 2027+ money from payroll.
FA27_NAMES = {"Michael King", "Clay Holmes", "Shota Imanaga"}
fa27 = sorted({row[11] for row in book if row[0] in FA27_NAMES})

# Service time (v5.1): real MLB service reconstructed from each player's
# transaction history (svc_fetch.py -> service.json, years.days as a float),
# replacing the seasons-with-an-appearance proxy that counted a September
# call-up as a full year. idx 11 = service through 2026; idx 8 = seasons of
# control left; idx 15 = arbitration awards already received before 2026's
# winter (Super Two included), so the page knows which arb year comes next.
SVC = json.load(open("/work/service.json")) if __import__("os").path.exists("/work/service.json") else {}
# free by contract expiry rather than six-year service (NPB signees whose
# original deals ran out): encoded as FA-eligible
CONTRACT_FA = {"Seiya Suzuki", "Shota Imanaga"}
import math as _m
n_svc = 0
for p in players:
    sv = SVC.get(str(p[1]))
    if p[0] in CONTRACT_FA:
        p[11] = 6.0
    elif sv:
        p[11] = sv["svc"]; n_svc += 1
    p[8] = max(1, min(6, 6 - int(_m.floor(p[11] + 1e-9))))
    p.append(len([w for w in (sv or {}).get("arb_winters", []) if w < 2026]))   # idx 15
print("service from transactions:", n_svc, "| contract-expiry FAs:", len(CONTRACT_FA))

# ---- v5.2: the winter as it actually happened (winter_2026.py) ----
import winter_2026 as W
PBYNAME = {}
for p in players: PBYNAME.setdefault(norm(p[0]), p)
def P_(nm):
    p = PBYNAME.get(norm(nm))
    if p is None: print("  winter: no desk row for", nm)
    return p
def proj27(p):
    """mirror of the page's dkBase + one aging step (dkProjSeasons per[0])"""
    obs = [(v, w) for v, w in ((p[7], 5), (p[6], 4), (p[5], 3)) if abs(v) > 0.05]
    base = (0.85 * sum(v * w for v, w in obs) / sum(w for _, w in obs) + 0.15 * PC["pop_mean"]) if obs else PC["pop_mean"]
    cv = PC["curves"]["pit" if p[3] else "bat"]
    return max(base + cv.get(str(min(max(p[4] + 1, 20), 41)), -0.3), 0) * (p[10] or 1)
STATUS = {}
# 1. posted players: a translated line (posted_build.py) on a normal row
POSTED = json.load(open("/work/posted.json"))
for spid, z in POSTED.items():
    pid = int(spid)
    if any(p[1] == pid for p in players): continue
    t = z["translated"]
    pos = z["pos"]; grp = "SP" if pos == "SP" else "RP" if pos == "RP" else "C" if pos == "C" else \
        "IF" if pos in ("1B", "2B", "3B", "SS") else "OF"
    row = [z["name"], pid, "", z["pit"], z["age"], t.get("2024", 0), t.get("2025", 0), t.get("2026", 0),
           6, 0, 1.0, 0.0, grp, pos, round(max(t.get(str(2026 - k), 0) * (0.88 ** k) for k in range(3)), 2), 0]
    players.append(row)
    club, lg, dl = W.POSTED[pid]
    STATUS[pid] = ["posted", f"posted by the {club} ({lg}); sign by {dl}"]
# 1b. prospects, Phase II (prospects_peak.py): minor-league translations plus
# 100 nearest 2012-2019 comparables on age, level, translated rates,
# position and pedigree. Every prospect carries a peak projection; org
# prospects beyond the Top 100 are VALUED by their comps' six-season WAR
# (Top 100 value stays on the rank curve, which the backtest still favors)
PK = json.load(open("/work/pros_peak.json"))
PROS = json.load(open("/work/pros.json"))     # rookie table, Top 100 levels (v5.2)
PROS_OUT, PEAK = {}, {}
have = {p[1]: p for p in players}
ranked_now = {p[1] for p in players if p[9]}
byorg = defaultdict(list)
for spid, z in PK["players"].items():
    pid = int(spid)
    if z["rank"] or pid in ranked_now or not z["org"] or z["age"] > 26: continue
    p = have.get(pid)
    if p is not None and (abs(p[5]) + abs(p[6]) + abs(p[7]) >= 0.6): continue
    byorg[z["org"]].append((z["ev6d"], spid))
n_new = 0
for ab, xs in byorg.items():
    # each club: its 25 best by value, plus its 10 highest ceilings not already
    # in (teenagers in the complex leagues price low on six discounted years
    # but are exactly who gets asked for in trades)
    top = [sp for _, sp in sorted(xs, reverse=True)[:25]]
    ceil = [sp for sp in sorted((sp for _, sp in xs), key=lambda sp: -PK["players"][sp]["peak"]) if sp not in top][:10]
    xs_sorted = sorted(((PK["players"][sp]["ev6d"], sp) for sp in top + ceil), reverse=True)
    for k, (_, spid) in enumerate(xs_sorted):
        z = PK["players"][spid]; pid = int(spid)
        pos = z["pos"]
        if pid not in have:
            grp = "SP" if pos == "SP" else "RP" if pos == "RP" else "C" if pos == "C" else \
                "IF" if pos in ("1B", "2B", "3B", "SS") else "OF"
            dpos = pos if pos in ("C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "SP", "RP") else "OF"
            row = [z["name"], pid, ab, 1 if z["kind"] == "P" else 0, z["age"], 0, 0, 0, 6, 0, 1.0, 0.0, grp, dpos, 0, 0]
            players.append(row); have[pid] = row; n_new += 1
        elif not have[pid][2]: have[pid][2] = ab
        PROS_OUT[spid] = [z["lvl"], z["ev6d"], z["y1"], z["line"], k + 1, None]
for spid, z in PK["players"].items():
    if int(spid) in have:
        PEAK[spid] = [z["peak"], z["p2"], z["p4"], z["up"], z["y1"], z["lvl"], z["line"],
                      [[c[0], c[1], c[4]] for c in z["comps"][:6]]]
print("prospects: org tier", len(PROS_OUT), "| new desk rows:", n_new, "| peak projections on desk rows:", len(PEAK))
# 2. filed for free agency: every filing in the league feed since Oct 1
DECL = {}
fd = get("https://statsapi.mlb.com/api/v1/transactions?startDate=2026-10-01&endDate=2026-11-30")
for t in fd.get("transactions", []):
    if t.get("typeDesc") == "Declared Free Agency" and (t.get("person") or {}).get("id"):
        DECL[t["person"]["id"]] = t.get("date")
if not DECL:      # feed unreachable: fall back to the Nov 1 snapshot
    DECL = {int(k): "2026-10-29" for k in json.load(open("/work/fa_declared_2026.json"))}
json.dump({str(k): v for k, v in DECL.items()}, open("/work/fa_declared_2026.json.tmp", "w"))
byid = {p[1]: p for p in players}
for pid, d in DECL.items():
    if pid in byid: STATUS[pid] = ["fa", f"filed for free agency {d}"]
for nm, why in W.FA.items():
    p = P_(nm)
    if p: STATUS[p[1]] = ["fa", why]
for nm in W.CONTROLLED_AFTER_DECLINE:
    p = P_(nm)
    if p: STATUS[p[1]] = ["ctr", "club option declined; still under club control through arbitration"]
# 3. contracts the base book lacks (typ 2: on file, never a pricing comp)
def add_contract(p, ab, y0, y1, aav, label):
    yrs = y1 - y0 + 1
    book.append([p[0], y0 - 1, ab, yrs, round(aav * yrs, 2), y0 - 1 - AGES.get(str(p[1]), 2000), p[3],
                 p[7], p[6], "", 0, p[1], 2, p[12], label])
for nm, ab, y0, y1, aav, label in W.CONTRACTS:
    p = P_(nm)
    if p:
        add_contract(p, ab, y0, y1, aav, label)
        STATUS[p[1]] = ["ctr", label]
# 4. open decisions (due Nov 2), modeled by each side's own arithmetic
for nm, kind, amt, buy in W.PENDING:
    p = P_(nm)
    if not p: continue
    vet = p[11] >= 6
    if kind == "club":
        val = proj27(p) * 10.0
        keep = val >= amt - buy
        has_row = any(r[11] == p[1] and r[1] + r[3] >= 2027 for r in book)
        txt = f"${amt:g}M club option, decision due Nov 2; the Ledger models it {'exercised' if keep else 'declined'} (projected 2027 value ${val:.1f}M vs ${amt - buy:g}M net of the buyout)"
        if keep:
            if not has_row: add_contract(p, p[2], 2027, 2027, amt, f"${amt:g}M club option (modeled exercised)")
            STATUS[p[1]] = ["pendin", txt]
        else:
            # declined: a veteran is a free agent; a younger player stays under control at an arbitration salary
            if has_row: fa27.append(p[1])
            STATUS[p[1]] = ["pendfa" if vet else "pendin", txt + ("" if vet else "; he stays under club control")]
    elif kind == "mutual":
        STATUS[p[1]] = ["pendfa" if vet else "pendin",
                        f"mutual option open (decision due Nov 2); mutual options are almost never exercised by both sides" +
                        ("" if vet else "; he is under club control either way")]
    else:
        STATUS[p[1]] = ["pendin", "opt-out decision due Nov 2; modeled as staying (the money left beats his projected market)"]
for nm, why in W.OUT.items():
    p = P_(nm)
    if p: STATUS[p[1]] = ["out", why]
# any free agent whose book row runs past 2026 is voided from 2027 on
cover27 = {r[11] for r in book if r[1] + r[3] >= 2027 and r[12] != 2}
for pid, (code, _) in STATUS.items():
    if code in ("fa", "pendfa") and pid in cover27 and pid not in fa27: fa27.append(pid)
fa27 = sorted(set(fa27))
for k in list(PROS_OUT):
    if STATUS.get(int(k), [None])[0] in ("fa", "out", "pendfa"): del PROS_OUT[k]
# QO eligibility: a player who changed clubs after Opening Day (trade, waiver
# claim, in-season signing) cannot receive a qualifying offer
_con = sqlite3.connect("/work/ledger.sqlite")
QO_INELIG = sorted({int(r[0]) for r in _con.execute(
    "select distinct person_id from sweep_tx where date>='2026-03-26' and date<='2026-10-31' "
    "and person_id is not null and (type_desc in ('Trade','Claimed Off Waivers') "
    "or (type_desc='Signed as Free Agent' and description not like '%minor league%'))")})
for nm in W.PRIOR_QO:
    p = P_(nm)
    if p and p[1] not in QO_INELIG: QO_INELIG.append(p[1])
QO_INELIG = sorted(set(QO_INELIG) & {p[1] for p in players})
print("QO-ineligible (moved in season):", len(QO_INELIG))
import collections as _c
print("winter status:", dict(_c.Counter(v[0] for v in STATUS.values())), "| on-file contracts:", sum(1 for r in book if r[12] == 2))
print("winter reality: fa27 pids", fa27)

# ---- committed payroll per club per season (book contracts, AAV spread) ----
# v5.1: money follows the PLAYER (a traded star's deal sits on his current
# club, not the club that signed him), and a newer contract supersedes an
# older one for the seasons both cover (an extension replaces the deal it
# tore up; a player who signed elsewhere is not on two payrolls). Cash sent
# in trades is not modeled.
CUR = {p[1]: p[2] for p in players}
FA27SET = set(fa27)
OUTSET = {pid for pid, v in STATUS.items() if v[0] == "out"}
by_pid = {}
for row in book:
    by_pid.setdefault(row[11], []).append(row)
payroll = {}
for pid, rows in by_pid.items():
    if pid in OUTSET: continue
    rows = sorted(rows, key=lambda r: (r[1], r[12] == 2))
    for season in range(2026, 2032):
        cover = [r for r in rows if max(2026, r[1] + 1) <= season <= r[1] + r[3]]
        if not cover: continue
        r = cover[-1]                       # the most recent contract governs the season
        if pid in FA27SET and season >= 2027: continue   # opted out / declined / free agent
        ab = CUR.get(pid) or r[2]
        if not ab: continue
        aav = r[4] / r[3]
        payroll.setdefault(ab, {}).setdefault(str(season), [0.0, 0])
        payroll[ab][str(season)][0] += aav
        payroll[ab][str(season)][1] += 1
payroll = {ab: {s: [round(v, 1), n] for s, (v, n) in yrsmap.items()} for ab, yrsmap in payroll.items()}
print("payroll clubs:", len(payroll), "| NYM 2027:", payroll.get("NYM", {}).get("2027"))

deals = json.load(open("/work/deal_archive.json"))
compact = [[x["yr"], x["ab"], x["ph"][0], x["ck"], x.get("po", "mid")[0], x["recv"], x["paid"], x["who"][:24]] for x in deals]

out = dict(
    players=players,
    curves=dict(bat=PC["curves"]["bat"], pit=PC["curves"]["pit"], pop=PC["pop_mean"],
                unrankedEV=PC["unranked_ev"], backtest=PC["backtest"]),
    market=dict(dpw={str(k): v for k, v in
                     {2026: 9.7, 2027: 10.0, 2028: 10.3, 2029: 10.6, 2030: 10.9, 2031: 11.2, 2032: 11.5}.items()},
                dpwHist={str(k): v for k, v in {2006:4.2,2007:4.5,2008:4.7,2009:4.7,2010:5.0,2011:5.2,2012:5.5,2013:6.0,
                     2014:6.5,2015:7.0,2016:7.7,2017:8.0,2018:8.2,2019:8.0,2020:8.0,2021:8.5,
                     2022:8.5,2023:9.0,2024:9.3,2025:9.5,2026:9.7}.items()},
                buckets={"rental": dict(ratio=0.8, bust=0.55), "+1": dict(ratio=0.99, bust=0.48),
                         "+2": dict(ratio=0.86, bust=0.39), "3+": dict(ratio=0.37, bust=0.71)},
                extDiscount={"predebut": 0.35, "early": 0.45, "arb": 0.60, "vet": 0.90}),
    slot=[[1, 9.9], [2, 7.5], [3, 6.7], [5, 5.5], [8, 4.6], [12, 3.6], [17, 3.0], [22, 2.6],
          [30, 2.1], [45, 1.5], [65, 1.1], [90, 0.85], [120, 0.6], [200, 0.35], [400, 0.18], [620, 0.10]],
    vrank=[[1, 8.0], [3, 7.0], [5, 6.5], [10, 5.5], [15, 4.8], [25, 4.0], [40, 3.2], [50, 2.8], [75, 2.0], [100, 1.5]],
    teams=teams,
    deals=compact,
    book=book,
    payroll=payroll,
    fa27=fa27,
    status={str(k): v for k, v in STATUS.items()},
    posted=POSTED,
    qoIneligible=QO_INELIG,
    pros=PROS_OUT,
    peak=PEAK,
    peakBacktest=PK["backtest"],
    rookie=PROS["rookie"],
    t100lvl=PROS["top100Level"],
    cbt={"2026": 244, "2027": None},  # 2027+ awaits the next CBA
)
json.dump(out, open("/work/desk_data.json", "w"), separators=(",", ":"))
import os
print("desk_data.json:", round(os.path.getsize("/work/desk_data.json") / 1e6, 2), "MB")
