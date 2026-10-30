"""
LEDGER PROJECTION v1: self-built future-WAR projections, used as a DISCLOSED
OVERLAY on open deals. Grades stay realized-only (the ledger's identity);
the projection answers "where is this deal heading."

No external projection system is consulted (ZiPS and friends live on
licensed sites this project does not scrape). Components, all from our own
data:

  AGING CURVE   delta method over the 28k-player cache: for every player
                with consecutive seasons, the WAR change bucketed by age,
                smoothed (3-age window), hitters and pitchers separately.
                Survivorship bias is the known weakness of the delta
                method; disclosed, and the backtest below is the arbiter.
  BASE SKILL    Marcel-style: weighted recent seasons (5/4/3 on t, t-1,
                t-2), regressed 20% toward the population mean.
  FORECAST      base walked forward on the aging curve, floored at zero,
                with a 10%/yr roster-uncertainty haircut beyond the first
                projected season.
  PROSPECTS     no meaningful MLB track record: ranked prospects carry the
                Pipeline rank-to-surplus expectation (the same curve the
                marks use); unranked traded prospects carry the empirical
                mean outcome of unranked traded pieces (computed below).
  BACKTEST      project 2023 from data through 2022 for every player who
                then appeared in 2023; report r and MAE. Same for 2025.

Attaches proj = {in, out, net, final} to every OPEN trade decision in
sweep_results.json and hist_results.json, plus __proj_meta__ for the page.
Writes proj_curves.json for the repo.
"""
import json, sqlite3
from collections import defaultdict

LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
AGES = json.load(open("/work/ages.json"))
POS = json.load(open("/work/positions.json"))
PITPOS = {"RHP", "LHP", "SP", "RP", "P"}
cfg = json.load(open("/work/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
TEAMNAMES = {r["teamId"]: ALIAS.get(r["teamId"], set()) | {r["team"]} for r in cfg["regimes"]}
con = sqlite3.connect("/work/ledger.sqlite"); con.row_factory = sqlite3.Row

def is_pit(pid): return POS.get(str(pid)) in PITPOS

# per-player season totals
BY = {}
for pid, rec in LVM.items():
    d = defaultdict(float)
    for (y, tm, v) in rec["rows"]: d[y] += v
    BY[pid] = dict(d)

# ---- aging curves (delta method) ----
def build_curve(pit):
    deltas = defaultdict(list)
    for pid, d in BY.items():
        if is_pit(pid) != pit: continue
        by = AGES.get(str(pid))
        if not by: continue
        for y in sorted(d):
            if (y + 1) in d and 1998 <= y <= 2025:
                age = y + 1 - by
                if 19 <= age <= 42:
                    deltas[age].append(d[y + 1] - d[y])
    curve = {}
    for age in range(20, 42):
        pool = deltas.get(age - 1, []) + deltas.get(age, []) + deltas.get(age + 1, [])
        if len(pool) >= 30:
            curve[age] = sum(pool) / len(pool)
    return curve
CURVE = {"bat": build_curve(False), "pit": build_curve(True)}
print("aging curve (bat):", {a: round(v, 2) for a, v in sorted(CURVE["bat"].items()) if a % 2 == 0})
print("aging curve (pit):", {a: round(v, 2) for a, v in sorted(CURVE["pit"].items()) if a % 2 == 0})

pop = [v for d in BY.values() for y, v in d.items() if y >= 2019]
POP_MEAN = sum(pop) / len(pop)

def base_skill(pid, asof):
    """weighted recent performance through season `asof`, regressed."""
    d = BY.get(pid, {})
    w = [(asof, 5), (asof - 1, 4), (asof - 2, 3)]
    num = sum(d.get(y, 0.0) * wt for y, wt in w)
    base = num / 12.0
    return 0.8 * base + 0.2 * POP_MEAN

def project(pid, season, asof=2026):
    """projected WAR for a future season (season > asof)."""
    by = AGES.get(str(pid))
    key = "pit" if is_pit(pid) else "bat"
    val = base_skill(pid, asof)
    if by:
        for yy in range(asof + 1, season + 1):
            age = yy - by
            val += CURVE[key].get(min(max(age, 20), 41), -0.3)
    else:
        val -= 0.25 * (season - asof)
    val = max(val, 0.0)
    return val * (0.9 ** max(0, season - asof - 1))

def career_war(pid): return sum(BY.get(pid, {}).values())
def mlb_seasons(pid): return sum(1 for v in BY.get(pid, {}).values() if abs(v) > 0.05)

# prospect remaining value: Pipeline rank curve (same anchors as the marks)
import math
_V = [(1,8.0),(3,7.0),(5,6.5),(10,5.5),(15,4.8),(25,4.0),(40,3.2),(50,2.8),(75,2.0),(100,1.5)]
def vrank(rank):
    if rank <= _V[0][0]: return _V[0][1]
    if rank >= _V[-1][0]: return _V[-1][1]
    for (x0,y0),(x1,y1) in zip(_V,_V[1:]):
        if x0 <= rank <= x1:
            f = (math.log(rank)-math.log(x0))/(math.log(x1)-math.log(x0))
            return y0 + f*(y1-y0)
RANKS = defaultdict(dict)
for rr in json.load(open("/work/prospect_ranks.json")):
    RANKS[str(rr["pid"])][rr["year"]] = rr["rank"]
def current_rank(pid):
    rk = RANKS.get(str(pid), {})
    return rk.get(2026) or rk.get(2025)

# unranked-prospect constant: mean realized control value of traded pieces
# 2012-2019 that had no top-100 rank and no MLB time before the deal
def val_control(pid, teams, y0, cap=6):
    rec = LVM.get(int(pid))
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
unr = []
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = TEAMNAMES[tid]
    for r in con.execute("select person_id, date from sweep_tx where team_id=? and type_desc='Trade' "
                         "and to_team in (%s) and date>='2012-01-01' and date<='2019-12-31'"
                         % ",".join("?"*len(names)), (tid, *names)):
        pid = r["person_id"]
        if not pid: continue
        y0 = int(r["date"][:4])
        if RANKS.get(str(pid)): continue
        pre = sum(v for y, v in BY.get(int(pid), {}).items() if y < y0)
        if abs(pre) > 0.1: continue
        unr.append(val_control(pid, names, y0))
UNRANKED_EV = round(sum(unr) / max(1, len(unr)), 2)
print(f"unranked traded prospect EV: {UNRANKED_EV} wins over the control window (n={len(unr)})")

# ---- backtest ----
def backtest(target):
    xs, ys = [], []
    for pid, d in BY.items():
        if target not in d: continue
        hist = [y for y in d if y < target]
        if not hist or max(hist) < target - 1: continue
        xs.append(project(pid, target, asof=target - 1))
        ys.append(d[target])
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    cov = sum((a-mx)*(b-my) for a, b in zip(xs, ys))/n
    vx = sum((a-mx)**2 for a in xs)/n; vy = sum((b-my)**2 for b in ys)/n
    r = cov/(vx*vy)**0.5
    mae = sum(abs(a-b) for a, b in zip(xs, ys))/n
    return dict(year=target, n=n, r=round(r, 3), mae=round(mae, 2))
bt = [backtest(2023), backtest(2025)]
print("backtest:", bt)

# ---- remaining-window projection per piece ----
def fa_after(pid, date):
    r = con.execute("select min(date) d from sweep_tx where person_id=? and type_desc='Declared Free Agency' and date>?",
                    (str(pid), date)).fetchone()
    return r["d"]

def remaining_proj(pid, teams, deal_date):
    """projected WAR over the rest of the control window (2027 on)."""
    pid = int(pid)
    y0 = int(deal_date[:4])
    last = y0 + 5
    # window already closed? left the org or declared FA
    d2026 = [tm for (y, tm, v) in LVM.get(pid, {}).get("rows", []) if y == 2026]
    if d2026 and not any(tm in teams for tm in d2026): return 0.0, "left"
    fa = fa_after(pid, deal_date)
    if fa and fa <= "2026-12-31": return 0.0, "fa"
    if fa: last = min(last, int(fa[:4]) - 1 if fa[5:7] < "04" else int(fa[:4]))
    if last < 2027: return 0.0, "window closed"
    if mlb_seasons(pid) < 2 and career_war(pid) < 1.5:
        rk = current_rank(pid)
        ev = vrank(rk) if rk else UNRANKED_EV
        return round(ev, 1), (f"rank #{rk}" if rk else "unranked prospect EV")
    tot = sum(project(pid, s) for s in range(2027, last + 1))
    return round(tot, 1), f"proj {2027}-{last}"

def attach(path):
    res = json.load(open(path))
    n = 0
    for r in res:
        tid = r["teamId"]; names = TEAMNAMES.get(tid, set())
        pools = [r.get("top", [])]
        led = r.get("led", {})
        if led.get("trade"):
            pools += [led["trade"].get("best", []), led["trade"].get("worst", [])]
        seen = set()
        for pool in pools:
            for d in pool:
                if d.get("ch") != "trade" or int(d["d"][:4]) < 2022: continue
                if id(d) in seen: continue
                seen.add(id(d))
                rows = [dict(x) for x in con.execute(
                    "select person_id, from_team, to_team from sweep_tx where team_id=? and date=? and type_desc='Trade'",
                    (tid, d["d"]))]
                pin = {x["person_id"] for x in rows if x["to_team"] in names and x["person_id"]}
                pout = {x["person_id"]: x["to_team"] for x in rows
                        if x["from_team"] in names and x["person_id"] and x["to_team"]}
                if not pin and not pout: continue
                rin = [remaining_proj(p, names, d["d"]) for p in pin]
                rout = [remaining_proj(p, {dest}, d["d"]) for p, dest in pout.items()]
                pi = sum(x[0] for x in rin)
                po = sum(x[0] for x in rout)
                # settled = every window closed or empty of remaining value AND
                # no piece still inside an open window (reason says proj/rank)
                live = [x for x in rin + rout if x[0] > 0 or x[1].startswith(("proj", "rank", "unranked"))]
                d["unsettled"] = bool(live)
                net = round(pi - po, 1)
                d["proj"] = dict(inn=round(pi, 1), out=round(po, 1), net=net,
                                 final=round(d["net"] + net, 1))
                n += 1
    json.dump(res, open(path, "w"), indent=1)
    print(f"{path}: projections on {n} open trades")

attach("/work/sweep_results.json")
attach("/work/hist_results.json")

json.dump(dict(curves=CURVE, pop_mean=round(POP_MEAN, 3), unranked_ev=UNRANKED_EV,
               backtest=bt, method="Marcel-style 5/4/3, 20% regression, delta-method aging, 10%/yr haircut, zero floor"),
          open("/work/proj_curves.json", "w"), indent=1)
print("wrote proj_curves.json")
