"""
REGIME DNA v2: development effects, retention channel, head-to-head records,
injury profiles, draft-room fingerprints, buy-low tendencies.

Everything computed from data already in the ledger:
  devDef / devPit / devBat   mover deltas by receiving org (see v1 notes;
                             devBat = hitter Ledger WAR after vs before)
  RETENTION CHANNEL (chan.ret)  passive losses graded: for each regime,
      wins lost to walked free agents (players with real recent value who
      declared FA and produced elsewhere in the next 3 seasons), per season,
      graded RELATIVE to the league's leakage rate, DISPLAY ONLY: the
      letter shows the tendency but contributes nothing to the composite,
      because raw leakage scales with how many stars you employ (the
      Dodgers lead the league in walked value because they lead the league
      in stars). It joins the composite only when the p(retain)-weighted
      version with compensation picks lands (methodology v0.2 machinery).
  h2h        head-to-head trade records: for every regime pair with
             overlapping windows, deals between them and net from each seat
             (unweighted control-window value, symmetric measure).
  injury     IL placements per club-season from Status Change rows,
             pitcher share separately. League-relative rates.
  draftRoom  bonus-vs-slot fingerprint from the draft table: overslot share,
             mean slot usage, prep share of top-10-round picks.
  buyLow     share of veteran trade acquisitions bought after a down year
             (prior-season value under half of the season before, which had
             real value). The league buys the dip ~a third of the time.

Merges into sweep_results.json: chan.ret, dna.*, h2h; writes h2h_matrix.json.
"""
import json, sqlite3
from collections import defaultdict

SV = json.load(open("/home/claude/savant_runs.json"))
SDI = json.load(open("/home/claude/sdi_runs.json"))
LVM = {k: v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}
POS = json.load(open("/home/claude/positions.json"))
PITPOS = {"RHP", "LHP", "SP", "RP"}
cfg = json.load(open("/home/claude/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
con = sqlite3.connect("/home/claude/ledger.sqlite"); con.row_factory = sqlite3.Row

NAME2AB = {}
NAME2TID = {}
for r in cfg["regimes"]:
    NAME2AB[r["team"]] = r["abbr"]; NAME2TID[r["team"]] = r["teamId"]
    for al in cfg["aliases"].get(str(r["teamId"]), []):
        NAME2AB[al] = r["abbr"]; NAME2TID[al] = r["teamId"]

def org_of(tm):
    if tm in NAME2AB: return NAME2AB[tm]
    for nm, ab in NAME2AB.items():
        if nm in tm: return ab
    return None

def is_pit(pid): return POS.get(str(pid)) in PITPOS

def def_runs(pid, y):
    s = SDI.get(str(pid), {}).get(str(y))
    if s is not None: return s
    sv = SV.get(str(pid), {}).get(str(y), {})
    if "def" in sv or "frame" in sv:
        return sv.get("def", 0.0) + sv.get("frame", 0.0)
    return None

def season_wins(pid, y):
    rec = LVM.get(str(pid))
    if not rec: return None
    vals = [v for (yy, tm, v) in rec["rows"] if yy == y]
    return sum(vals) if vals else None

# ---------- mover deltas ----------
dd, dp, db = defaultdict(list), defaultdict(list), defaultdict(list)
for pid, rec in LVM.items():
    rows = rec.get("rows") or []
    seq = {}
    for (y, tm, v) in rows:
        ab = org_of(tm)
        if ab: seq.setdefault(y, ab)
    years = sorted(seq)
    if len(years) < 3: continue
    for i in range(1, len(years)):
        y = years[i]
        if seq[y] == seq[years[i-1]]: continue
        new_org = seq[y]
        before_y = [yy for yy in years[:i] if seq[yy] != new_org][-2:]
        after_y = [yy for yy in years[i:] if seq[yy] == new_org][:2]
        if not before_y or not after_y: continue
        if is_pit(pid):
            b = [season_wins(pid, yy) for yy in before_y]; a = [season_wins(pid, yy) for yy in after_y]
            b = [x for x in b if x is not None]; a = [x for x in a if x is not None]
            if b and a: dp[new_org].append(sum(a)/len(a) - sum(b)/len(b))
        else:
            b = [def_runs(pid, yy) for yy in before_y]; a = [def_runs(pid, yy) for yy in after_y]
            b = [x for x in b if x is not None]; a = [x for x in a if x is not None]
            if b and a: dd[new_org].append(sum(a)/len(a) - sum(b)/len(b))
            b2 = [season_wins(pid, yy) for yy in before_y]; a2 = [season_wins(pid, yy) for yy in after_y]
            b2 = [x for x in b2 if x is not None]; a2 = [x for x in a2 if x is not None]
            if b2 and a2: db[new_org].append(sum(a2)/len(a2) - sum(b2)/len(b2))
        break

# ---------- retention channel ----------
def val_on(pid, names, y0, y1, inside=True):
    rec = LVM.get(str(pid))
    if not rec: return 0.0
    return sum(v for (y, tm, v) in rec["rows"] if y0 <= y <= y1 and ((tm in names) == inside))

ret = {}
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    start = max(reg["start"], "2005-01-01")
    lost = 0.0; n = 0
    for r in con.execute("select date, person_id from sweep_tx where team_id=? and date>=? and type_desc='Declared Free Agency' and person_id is not null", (tid, start)):
        yr = int(r["date"][:4])
        if val_on(r["person_id"], names, yr - 2, yr) > 0.5:
            l = val_on(r["person_id"], names, yr + 1, yr + 3, inside=False)
            if l > 0: lost += l; n += 1
    ret[tid] = dict(lost=lost, n=n)

res = json.load(open("/home/claude/sweep_results.json"))
tot_lost = sum(v["lost"] for v in ret.values())
tot_sea = sum(r["seasons"] for r in res)
lg_rate = tot_lost / tot_sea
print(f"league walk-away leakage: {lg_rate:.2f} wins per club-season")

def grade(nps):
    for thr, g in [(2.6,80),(1.8,75),(1.2,70),(0.8,65),(0.5,60),(0.2,55),
                   (-0.2,50),(-0.6,45),(-1.0,40),(-1.6,35)]:
        if nps >= thr: return g
    return 30
def grade_comp(nps):
    for thr, g in [(8.0,80),(5.5,75),(3.5,70),(2.2,65),(1.2,60),(0.4,55),
                   (-0.4,50),(-1.2,45),(-2.2,40),(-3.5,35)]:
        if nps >= thr: return g
    return 30

# ---------- head-to-head ----------
def val_control(pid, teams, y0, cap=6):
    rec = LVM.get(str(pid))
    if not rec: return 0.0
    byyear = defaultdict(list)
    for y, tm, v in rec["rows"]: byyear[y].append((tm, v))
    tot = 0.0
    for y in range(y0, y0 + cap):
        rows = byyear.get(y, [])
        here = [v for (tm, v) in rows if tm in teams]
        if rows and not here and y > y0: break
        tot += sum(here)
    return tot

h2h = defaultdict(lambda: dict(n=0, net=0.0))   # (tidA, tidB) from A's seat
seen = set()
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    start = max(reg["start"], "2005-01-01")
    trades = defaultdict(list)
    for r in con.execute("select * from sweep_tx where team_id=? and date>=? and type_desc='Trade'", (tid, start)):
        trades[(r["date"], r["description"])].append(dict(r))
    for (d, desc), rs in trades.items():
        yr = int(d[:4])
        opps = {NAME2TID.get(x["to_team"]) for x in rs if x["from_team"] in names and x["to_team"]} | \
               {NAME2TID.get(x["from_team"]) for x in rs if x["to_team"] in names and x["from_team"]}
        opps = {o for o in opps if o and o != tid}
        for opp in opps:
            if d < REG[opp]["start"]: continue           # both regimes in office
            key = (tid, opp, d, desc)
            if key in seen: continue
            seen.add(key)
            vin = sum(val_control(x["person_id"], names, yr) for x in rs
                      if x["to_team"] in names and x["person_id"] and NAME2TID.get(x["from_team"]) == opp)
            vout = sum(val_control(x["person_id"], {x["to_team"]}, yr) for x in rs
                       if x["from_team"] in names and x["person_id"] and NAME2TID.get(x["to_team"]) == opp)
            h2h[(tid, opp)]["n"] += 1
            h2h[(tid, opp)]["net"] += vin - vout

# ---------- injury + draft room + buy-low ----------
inj = {}
for reg in cfg["regimes"]:
    tid = reg["teamId"]
    start = max(reg["start"], "2005-01-01")
    npit = nbat = 0
    for r in con.execute("select person_id from sweep_tx where team_id=? and date>=? and type_desc='Status Change' and lower(description) like '%injured list%'", (tid, start)):
        if is_pit(r["person_id"]): npit += 1
        else: nbat += 1
    inj[tid] = dict(pit=npit, bat=nbat)

draftroom = {}
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    y0 = max(int(reg["start"][:4]) + (0 if reg["start"][5:7] < "07" else 1), 2005)
    q = "select bonus, pick_value, school, round from draft_picks where cast(year as int)>=? and cast(round as int)<=10 and signed='1' and team in (%s)" % ",".join("?"*len(names))
    over = tot = prep = n = 0
    for r in con.execute(q, (y0, *names)):
        try: b, pv = float(r["bonus"] or 0), float(r["pick_value"] or 0)
        except ValueError: continue
        if b <= 0 or pv <= 0: continue
        n += 1
        if b > pv * 1.05: over += 1
        tot += b / pv
        if "HS" in (r["school"] or "") or "High School" in (r["school"] or ""): prep += 1
    draftroom[tid] = dict(n=n, overslot=round(over / n, 2) if n else None,
                          slotUse=round(tot / n, 2) if n else None,
                          prep=round(prep / n, 2) if n else None)

buylow = {}
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    start = max(reg["start"], "2005-01-01")
    dips = vets = 0
    seen_p = set()
    for r in con.execute("select date, person_id, to_team from sweep_tx where team_id=? and date>=? and type_desc='Trade' and person_id is not null", (tid, start)):
        if r["to_team"] not in names: continue
        k = (r["person_id"], r["date"][:4])
        if k in seen_p: continue
        seen_p.add(k)
        yr = int(r["date"][:4])
        v1 = season_wins(r["person_id"], yr - 1); v2 = season_wins(r["person_id"], yr - 2)
        if v2 is not None and v2 >= 1.5:
            vets += 1
            if (v1 or 0) < 0.5 * v2: dips += 1
    buylow[tid] = dict(vets=vets, rate=round(dips / vets, 2) if vets >= 8 else None)

# ---------- merge ----------
by_tid = {r["teamId"]: r for r in res}
print(f"\n{'team':<5}{'ret':>7}{'lost':>7}{'devBat':>8}{'IL/yr':>7}{'over%':>7}{'dip%':>6}")
for r in res:
    tid = r["teamId"]
    rr = ret[tid]
    rel = -(rr["lost"] / r["seasons"] - lg_rate)          # + = leaks less than league
    r["chan"]["ret"] = dict(net=0, g=grade(rel), n=rr["n"],
                            lost=round(rr["lost"], 1), rel=round(rel, 2), display_only=True)
    d = r.setdefault("dna", {})
    ab = r["abbr"]
    dl = dd.get(ab, []); pl = dp.get(ab, []); bl = db.get(ab, [])
    d["devDef"] = dict(v=round(sum(dl)/len(dl), 2), n=len(dl)) if len(dl) >= 6 else dict(v=None, n=len(dl))
    d["devPit"] = dict(v=round(sum(pl)/len(pl), 2), n=len(pl)) if len(pl) >= 6 else dict(v=None, n=len(pl))
    d["devBat"] = dict(v=round(sum(bl)/len(bl), 2), n=len(bl)) if len(bl) >= 6 else dict(v=None, n=len(bl))
    d["inj"] = dict(pit=round(inj[tid]["pit"] / r["seasons"], 1), bat=round(inj[tid]["bat"] / r["seasons"], 1))
    d["draftRoom"] = draftroom[tid]
    d["buyLow"] = buylow[tid]
    partners = []
    for (a, b), v in h2h.items():
        if a == tid and v["n"] >= 2:
            partners.append(dict(opp=REG[b]["abbr"], exec=REG[b]["exec"], n=v["n"], net=round(v["net"], 1)))
    partners.sort(key=lambda x: -abs(x["net"]))
    r["h2h"] = partners
    print(f"{ab:<5}{rel:>+7.2f}{rr['lost']:>7.1f}{(sum(bl)/len(bl) if bl else 0):>+8.2f}{(inj[tid]['pit']+inj[tid]['bat'])/r['seasons']:>7.1f}{(draftroom[tid]['overslot'] or 0):>7.2f}{(buylow[tid]['rate'] or 0):>6.2f}")

json.dump(res, open("/home/claude/sweep_results.json", "w"), indent=1)
matrix = {f"{REG[a]['abbr']}|{REG[b]['abbr']}": dict(n=v["n"], net=round(v["net"], 1))
          for (a, b), v in h2h.items() if v["n"] >= 1}
json.dump(matrix, open("/home/claude/h2h_matrix.json", "w"))
print(f"\nmerged: ret channel, dna v2, h2h ({len(matrix)} directed pairs)")
