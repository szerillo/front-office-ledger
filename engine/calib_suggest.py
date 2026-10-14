"""
Calibration backtest for the Deal Desk term suggester.

For every contract in the book signed in offseasons 2010-2025, reconstruct
what the suggester would have offered AS OF that winter:
  - platform seasons Y, Y-1, Y-2 from the value cache (observed-season
    weighted Marcel base, identical to dkBase)
  - aging-curve walk identical to dkProjSeasons (no haircut, FA accounting)
  - market-comp offer: median years / inflation-adjusted AAV of the 8
    nearest contracts signed STRICTLY EARLIER (same scoring as
    dkCompContracts), dollars in year Y+1 terms via dpwHist
  - model-fair offer: years until projected season value < 0.75,
    dollars = projected WAR x dpwHist(Y+1) (flat; no forward table in-era)
Compare both offers to the actual signed terms.
"""
import json, csv, sys, unicodedata
from collections import defaultdict
from statistics import median, mean

sys.path.insert(0, "/home/claude")
from contracts_recent import RECENT

LVM = {int(k): v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}
AGES = json.load(open("/home/claude/ages.json"))
POS = json.load(open("/home/claude/positions.json"))
PITPOS = {"RHP", "LHP", "SP", "RP", "P"}
PC = json.load(open("/home/claude/proj_curves.json"))
cfg = json.load(open("/home/claude/regimes.json"))

DPWH = {2006:4.2,2007:4.5,2008:4.7,2009:4.7,2010:5.0,2011:5.2,2012:5.5,2013:6.0,
        2014:6.5,2015:7.0,2016:7.7,2017:8.0,2018:8.2,2019:8.0,2020:8.0,2021:8.5,
        2022:8.5,2023:9.0,2024:9.3,2025:9.5,2026:9.7}
POPMEAN = PC["pop_mean"]
CURVES = {0: PC["curves"]["bat"], 1: PC["curves"]["pit"]}

def norm(nm):
    x = unicodedata.normalize("NFKD", nm or "").encode("ascii", "ignore").decode()
    return x.lower().replace(".", "").replace(" jr", "").strip()

BY = {}
for pid, rec in LVM.items():
    d = defaultdict(float)
    for (y, tm, v) in rec["rows"]:
        d[y] += v
    BY[pid] = (dict(d), rec["name"])
NAME2PIDS = defaultdict(list)
for pid, (d, name) in BY.items():
    NAME2PIDS[norm(name)].append(pid)

TEAMNAMES = {r["teamId"]: set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in cfg["regimes"]}
def short_to_tid(short):
    for r in cfg["regimes"]:
        if any(short and short.lower() in nm.lower() for nm in TEAMNAMES[r["teamId"]]):
            return r["teamId"]
    return None
AB2TID = {r["abbr"]: r["teamId"] for r in cfg["regimes"]}

raw = []
with open("/home/claude/repo/data/contracts_espn.csv") as f:
    for row in csv.DictReader(f):
        tid = short_to_tid(row["to_team"])
        if tid: raw.append((int(row["offseason"]), row["player"], int(row["years"]), float(row["total_m"])))
for off, pl, ab, yrs, tot in RECENT:
    raw.append((off, pl, yrs, float(tot)))

# resolve to pids, build full contract rows with 3 platform seasons
rows = []
for (off, pl, yrs, tot) in raw:
    cands = NAME2PIDS.get(norm(pl), [])
    if not cands: continue
    pid = cands[0] if len(cands) == 1 else max(cands, key=lambda p: abs(BY[p][0].get(off, 0)) + abs(BY[p][0].get(off - 1, 0)))
    d = BY[pid][0]
    age = off - AGES.get(str(pid), 0)
    if not (18 < age < 46): continue
    pit = 1 if POS.get(str(pid)) in PITPOS else 0
    rows.append(dict(pl=pl, pid=pid, off=off, yrs=yrs, tot=tot, age=age, pit=pit,
                     p1=d.get(off, 0.0), p2=d.get(off - 1, 0.0), p3=d.get(off - 2, 0.0)))
rows.sort(key=lambda r: r["off"])
print("contracts resolved:", len(rows))

def dk_base(r):
    obs = [(r["p1"], 5), (r["p2"], 4), (r["p3"], 3)]
    obs = [(v, w) for (v, w) in obs if abs(v) > 0.05]
    if not obs: return 0.85 * 0 + 0.15 * POPMEAN
    base = sum(v * w for v, w in obs) / sum(w for _, w in obs)
    return 0.85 * base + 0.15 * POPMEAN

def proj_seasons(r, n):
    curve = CURVES[r["pit"]]
    val = dk_base(r); per = []
    for i in range(1, n + 1):
        a = r["age"] + i
        val += curve.get(str(min(max(a, 20), 41)), -0.3)
        per.append(max(val, 0.0))
    return per

def suggest(r, hist):
    """hist: list of earlier contract rows (with realized terms)."""
    # comp scoring identical to dkCompContracts
    pBlend = r["p1"] * 0.55 + r["p2"] * 0.30 + r["p3"] * 0.15
    pPeak = max(r["p1"], r["p2"], r["p3"])
    scored = []
    for c in hist:
        cBlend = c["p1"] * 0.65 + c["p2"] * 0.35
        cPeak = max(c["p1"], c["p2"])
        s = abs(cBlend - pBlend) * 1.0 + abs(cPeak - pPeak) * 0.5 + abs(c["age"] - r["age"]) * 0.45 + (1.6 if c["pit"] != r["pit"] else 0.0)
        scored.append((s, c))
    scored.sort(key=lambda x: x[0])
    comps = [c for _, c in scored[:8]]
    yr1 = min(r["off"] + 1, 2026)
    if comps:
        adj = [(c["tot"] / c["yrs"]) * (DPWH[yr1] / DPWH[min(c["off"] + 1, 2026)]) for c in comps]
        mktY = int(median(sorted(c["yrs"] for c in comps)))
        mktAAV = median(adj)
    else:
        mktY, mktAAV = 3, DPWH[yr1]
    mktT = mktY * mktAAV
    per = proj_seasons(r, 10)
    fairY = 1
    for i in range(10):
        if per[i] >= 0.75: fairY = i + 1
    fairT = sum(per[:fairY]) * DPWH[yr1]
    return mktY, mktT, fairY, fairT

# walk forward
res = []
for i, r in enumerate(rows):
    if r["off"] < 2010: continue
    hist = [c for c in rows[:i] if c["off"] < r["off"]]
    if len(hist) < 30: continue
    mktY, mktT, fairY, fairT = suggest(r, hist)
    res.append(dict(r=r, mktY=mktY, mktT=mktT, fairY=fairY, fairT=fairT))

print("evaluated:", len(res))

def report(sel, label):
    if not sel: return
    eyM = [x["mktY"] - x["r"]["yrs"] for x in sel]
    etM = [x["mktT"] - x["r"]["tot"] for x in sel]
    eyF = [x["fairY"] - x["r"]["yrs"] for x in sel]
    etF = [x["fairT"] - x["r"]["tot"] for x in sel]
    aavA = [x["r"]["tot"] / x["r"]["yrs"] for x in sel]
    aavM = [x["mktT"] / x["mktY"] for x in sel]
    aavF = [x["fairT"] / x["fairY"] for x in sel]
    eaM = [m - a for m, a in zip(aavM, aavA)]
    eaF = [f - a for f, a in zip(aavF, aavA)]
    print(f"\n[{label}] n={len(sel)}")
    print(f"  market-comp: MAE yrs {mean(map(abs,eyM)):.2f} (bias {mean(eyM):+.2f}) | MAE AAV {mean(map(abs,eaM)):.1f} (bias {mean(eaM):+.1f}) | MAE total {mean(map(abs,etM)):.1f} (bias {mean(etM):+.1f})")
    print(f"  model-fair : MAE yrs {mean(map(abs,eyF)):.2f} (bias {mean(eyF):+.2f}) | MAE AAV {mean(map(abs,eaF)):.1f} (bias {mean(eaF):+.1f}) | MAE total {mean(map(abs,etF)):.1f} (bias {mean(etF):+.1f})")

report(res, "ALL 2010-2025")
report([x for x in res if x["r"]["off"] <= 2016], "2010-2016")
report([x for x in res if x["r"]["off"] >= 2017], "2017-2025")
report([x for x in res if x["r"]["pit"] == 0], "position players")
report([x for x in res if x["r"]["pit"] == 1], "pitchers")
report([x for x in res if x["r"]["age"] <= 29], "age <= 29")
report([x for x in res if 30 <= x["r"]["age"] <= 32], "age 30-32")
report([x for x in res if x["r"]["age"] >= 33], "age >= 33")
report([x for x in res if x["r"]["tot"] >= 100], "mega deals >= $100M")
report([x for x in res if 25 <= x["r"]["tot"] < 100], "mid $25-100M")
report([x for x in res if x["r"]["tot"] < 25], "small < $25M")

json.dump([{**{k: x[k] for k in ("mktY","mktT","fairY","fairT")},
            "pl": x["r"]["pl"], "off": x["r"]["off"], "yrs": x["r"]["yrs"], "tot": x["r"]["tot"],
            "age": x["r"]["age"], "pit": x["r"]["pit"]} for x in res],
          open("/home/claude/calib_results.json", "w"))
print("\nwrote calib_results.json")
