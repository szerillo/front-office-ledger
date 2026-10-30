"""
RETENTION v2: expectation-conditioned retention grading, so the channel can
join the FOR composite without punishing clubs for employing stars.

v1 problem: raw leakage (wins produced elsewhere by departed free agents)
scales with how many stars a club employs; the Dodgers bleed ~90 wins simply
because they had the most talent to lose. That is a payroll fact, not a
decision grade, so v1 stayed display-only.

v2 fix: condition on who left. From every "Declared Free Agency" event
league-wide 1998-2023 (3 full future seasons observable), build the empirical
curve E[next-3yr LVM elsewhere | last-3yr LVM here]. A regime is then graded
only on the GAP between what its departures went on to do and what the market
expected departures of that caliber to do, plus a +1.0 win credit per
qualifying-offer departure (the compensation pick; mirrors the QO_CHARGE on
the signing club's FA ledger). Letting a 6-win player walk is not a mistake;
letting the one who still had 12 wins left walk, repeatedly, is.

Merges chan.ret v2 fields into sweep_results.json and (distribution
permitting) adds ret net to the FOR composite.
"""
import json, sqlite3, unicodedata
from collections import defaultdict
from contracts_ext import QO

def norm(nm):
    s = unicodedata.normalize("NFKD", nm or "").encode("ascii", "ignore").decode()
    return s.lower().replace(".", "").replace(" jr", "").strip()

QOn = {(norm(n), y) for (n, y) in QO}

_raw = json.load(open("/work/lvm_cache.json"))
LVM = {int(k): v for k, v in _raw.items() if not k.startswith("__")}

cfg = json.load(open("/work/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
TEAMS = {r["teamId"]: ALIAS.get(r["teamId"], {r["team"]}) for r in cfg["regimes"]}

def val(pid, teams, y0, y1, inside=True):
    rec = LVM.get(int(pid)) if pid else None
    if not rec: return 0.0
    return sum(v for yr, tm, v in rec["rows"]
               if y0 <= yr <= y1 and ((tm in teams) == inside))

con = sqlite3.connect("/work/ledger.sqlite"); con.row_factory = sqlite3.Row

# ---- league expectation curve, all departures 1998-2023 ----
events = [dict(r) for r in con.execute(
    "select * from sweep_tx where type_desc='Declared Free Agency' and date<='2023-12-31'")]
seen = set(); pairs = []
for r in events:
    pid, tid = r["person_id"], r["team_id"]
    if not pid or tid not in TEAMS: continue
    yr = int(r["date"][:4])
    k = (pid, yr)
    if k in seen: continue
    seen.add(k)
    names = TEAMS[tid]
    prior = val(pid, names, yr - 2, yr, inside=True)
    if prior <= 0.0: continue
    fut = val(pid, names, yr + 1, yr + 3, inside=False)
    pairs.append((prior, fut))

EDGES = [0.0, 0.5, 1.0, 2.0, 3.0, 4.5, 6.5, 9.0, 13.0, 99.0]
bins = defaultdict(list)
for p, f in pairs:
    for i in range(len(EDGES) - 1):
        if EDGES[i] <= p < EDGES[i+1]:
            bins[i].append((p, f)); break
CURVE = []   # (bin center by mean prior, mean future, n)
for i in range(len(EDGES) - 1):
    rows = bins.get(i, [])
    if len(rows) < 8: continue
    mp = sum(p for p, _ in rows) / len(rows)
    mf = sum(f for _, f in rows) / len(rows)
    CURVE.append((mp, mf, len(rows)))
print("retention expectation curve (prior 3yr -> expected next-3yr elsewhere):")
for mp, mf, n in CURVE:
    print(f"  prior {mp:5.1f} -> {mf:5.2f}   (n={n})")

def expect(prior):
    c = CURVE
    if prior <= c[0][0]: return c[0][1]
    if prior >= c[-1][0]: return c[-1][1] * (prior / c[-1][0])  # extrapolate ratio
    for (x0, y0, _), (x1, y1, _) in zip(c, c[1:]):
        if x0 <= prior <= x1:
            f = (prior - x0) / (x1 - x0)
            return y0 + f * (y1 - y0)
    return 0.0

# ---- per-regime grading ----
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

res = json.load(open("/work/sweep_results.json"))
REG = {r["teamId"]: r for r in cfg["regimes"]}
nets = []
for r in res:
    tid = r["teamId"]
    start = max(REG[tid]["start"], "1998-01-01")
    names = TEAMS[tid]
    rows = [dict(x) for x in con.execute(
        "select * from sweep_tx where team_id=? and date>=? and type_desc='Declared Free Agency' and date<='2023-12-31'",
        (tid, start))]
    seen2 = set(); net2 = 0.0; n2 = 0; qo_n = 0; worst = []
    for x in rows:
        pid = x["person_id"]
        if not pid: continue
        yr = int(x["date"][:4])
        if (pid, yr) in seen2: continue
        seen2.add((pid, yr))
        prior = val(pid, names, yr - 2, yr, inside=True)
        if prior <= 0.5: continue
        fut = val(pid, names, yr + 1, yr + 3, inside=False)
        exp = expect(prior)
        gap = exp - fut            # positive: departed player did LESS than market expected: good call
        if (norm(x["person_name"]), yr) in QOn:
            gap += 1.0; qo_n += 1
        net2 += gap; n2 += 1
        if fut - exp > 1.5:
            worst.append((x["person_name"], yr, round(prior,1), round(fut,1), round(exp,1)))
    worst.sort(key=lambda t: -(t[3] - t[4]))
    ret = r["chan"].get("ret") or {}
    ret.update(net2=round(net2, 1), n2=n2, qo=qo_n, g2=grade(net2 / r["seasons"]),
               worst2=[dict(nm=w[0], y=w[1], prior=w[2], fut=w[3], exp=w[4]) for w in worst[:3]])
    r["chan"]["ret"] = ret
    nets.append((r["abbr"], round(net2,1), n2, r["seasons"]))

nets.sort(key=lambda t: -t[1])
print("\nret v2 nets (expectation-conditioned):")
for ab, n, k, s in nets:
    print(f"  {ab:<5} {n:+6.1f} over {k} departures ({s} yrs, {n/s:+.2f}/yr)")

vals = [n for _, n, _, _ in nets]
import statistics
print(f"\nmean {statistics.mean(vals):+.1f} | median {statistics.median(vals):+.1f} | sd {statistics.pstdev(vals):.1f}")

# join composite: v2 is centered by construction; add to FOR total
for r in res:
    net2 = r["chan"]["ret"]["net2"]
    r["total"] = round(r["total"] + net2, 1)
    r["forGrade"] = grade_comp(r["total"] / r["seasons"])

json.dump(res, open("/work/sweep_results.json", "w"), indent=1)
print("\nmerged ret v2 into sweep_results.json (composite updated)")
