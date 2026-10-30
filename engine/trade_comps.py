"""
TRADE COMPS: every graded trade on a card gets the three most comparable
deals from the full 1998-2023 league-wide archive, so a verdict can be read
against the market for deals of that shape rather than in a vacuum.

A deal's shape (v2) = season phase (deadline / offseason / in-season)
x control bucket of the headline acquired piece (rental, +1, +2, 3+ yrs)
x buyer posture that season (contender >= 85 wins pace, mid, rebuilder < 75)
x magnitude (control-window wins the buyer eventually received). Comps are
the nearest deals by received magnitude in the same phase, with penalties
for control-bucket and posture mismatches and 0.15 wins per year of era
distance, from other clubs. Outcome shown is the buyer's seat: received vs
paid (what the surrendered players became for the seller).

Writes comps onto every trade decision in sweep_results.json and
hist_results.json (fields the regen passes through to the page), plus
deal_archive.json for the repo.
"""
import json, sqlite3
from collections import defaultdict

LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
cfg = json.load(open("/work/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
ABBR = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
con = sqlite3.connect("/work/ledger.sqlite"); con.row_factory = sqlite3.Row

# buyer win totals by (tid, yr) for posture
import time, urllib.request
def get(u, tries=3):
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=40))
        except Exception: time.sleep(2 + 2*a)
    return {}
WL = {}
for yr in range(1998, 2027):
    d = get(f"https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season={yr}&standingsTypes=regularSeason")
    for g in d.get("records", []):
        for t in g.get("teamRecords", []):
            w, l = t.get("wins", 0), t.get("losses", 0)
            if w + l >= 100:
                WL[(t["team"]["id"], yr)] = w * 162 / (w + l)
def posture(tid, yr):
    w = WL.get((tid, yr))
    if w is None: return "mid"
    return "contend" if w >= 85 else ("rebuild" if w < 75 else "mid")

fa_dates = defaultdict(list)
for r in con.execute("select person_id, date from sweep_tx where type_desc='Declared Free Agency' and person_id is not null"):
    fa_dates[str(r["person_id"])].append(r["date"])
for k in fa_dates: fa_dates[k].sort()

def control_years(pid, deal_date):
    for d in fa_dates.get(str(pid), []):
        if d > deal_date:
            return min(6, max(1, int(d[:4]) - int(deal_date[:4]) + 1))
    return 6  # censored or pre-FA career: treat as full control

def bucket(c): return "rental" if c <= 1 else "+1" if c == 2 else "+2" if c == 3 else "3+"
def phase(date):
    m = int(date[5:7])
    return "deadline" if 6 <= m <= 8 else ("offseason" if (m >= 10 or m <= 3) else "inseason")

def val_control(pid, teams, y0, cap=6):
    rec = LVM.get(int(pid)) if pid else None
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

# ---- league-wide deal archive, buyer seats ----
deals = []
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    rows = [dict(r) for r in con.execute(
        "select * from sweep_tx where team_id=? and date>='1998-01-01' and date<='2023-12-31' and type_desc='Trade'", (tid,))]
    trades = defaultdict(list)
    for r in rows: trades[(r["date"], r["description"])].append(r)
    for (d, desc), rs in trades.items():
        yr = int(d[:4])
        acq = [x for x in rs if x["to_team"] in names and x["person_id"]]
        if not acq: continue
        outs = {x["person_id"]: x["to_team"] for x in rs
                if x["from_team"] in names and x["person_id"] and x["to_team"]}
        received = sum(val_control(int(x["person_id"]), names, yr) for x in acq)
        paid = sum(val_control(int(p), {dest}, yr) for p, dest in outs.items())
        best = max(acq, key=lambda x: val_control(int(x["person_id"]), names, yr))
        ctrl = max(control_years(x["person_id"], d) for x in acq)
        deals.append(dict(d=d, yr=yr, tid=tid, ab=ABBR[tid], ph=phase(d), ck=bucket(ctrl),
                          po=posture(tid, yr), recv=round(received, 1), paid=round(paid, 1),
                          who=(best["person_name"] or "?")))
print(f"deal archive: {len(deals)} buyer-seat deals 1998-2023")

# index by phase
IDX = defaultdict(list)
for x in deals: IDX[x["ph"]].append(x)

def deal_shape(tid, date):
    """control bucket + posture of a decision's own deal, from the feed."""
    names = ALIAS.get(tid, set())
    rows = [dict(r) for r in con.execute(
        "select person_id, to_team from sweep_tx where team_id=? and date=? and type_desc='Trade'", (tid, date))]
    acq = [r["person_id"] for r in rows if r["to_team"] in names and r["person_id"]]
    ck = bucket(max((control_years(p, date) for p in acq), default=6))
    return ck, posture(tid, int(date[:4]))

def find_comps(date, tid, vin, k=3):
    yr = int(date[:4])
    ck0, po0 = deal_shape(tid, date)
    cands = []
    for x in IDX.get(phase(date), []):
        if x["d"] == date and x["tid"] == tid: continue
        score = (abs(x["recv"] - vin) + 0.15 * abs(x["yr"] - yr)
                 + (0.0 if x["ck"] == ck0 else 2.5)
                 + (0.0 if x["po"] == po0 else 1.2))
        cands.append((score, x))
    cands.sort(key=lambda t: t[0])
    out, seen = [], set()
    for _, x in cands:
        key = (x["d"], x["tid"])
        if key in seen: continue
        seen.add(key)
        out.append(dict(yr=x["yr"], ab=x["ab"], who=x["who"][:26], ck=x["ck"], po=x["po"],
                        recv=x["recv"], paid=x["paid"]))
        if len(out) >= k: break
    return out

def attach(path, tid_key="teamId"):
    res = json.load(open(path))
    n = 0
    for r in res:
        tid = r[tid_key]
        pools = [r.get("top", [])]
        led = r.get("led", {})
        if led.get("trade"):
            pools += [led["trade"].get("best", []), led["trade"].get("worst", [])]
        seen = set()
        for pool in pools:
            for dcs in pool:
                if dcs.get("ch") != "trade": continue
                key = id(dcs)
                if key in seen: continue
                seen.add(key)
                vin = dcs.get("vin", abs(dcs.get("net", 0)))
                dcs["comps"] = find_comps(dcs["d"], tid, vin)
                n += 1
    json.dump(res, open(path, "w"), indent=1)
    print(f"{path}: comps attached to {n} trade decisions")

attach("/work/sweep_results.json")
attach("/work/hist_results.json")
json.dump(deals, open("/work/deal_archive.json", "w"))
print("wrote deal_archive.json")
