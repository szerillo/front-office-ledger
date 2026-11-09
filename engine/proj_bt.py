"""Nov 9: walk-forward backtest of the projection base's season weights and
regression (the Duran/Cruz question). Target: Ledger WAR in season T, for
2016-2026. Inputs: Ledger WAR and playing time (PA, IP) in T-1..T-3.
Evaluated two ways: rate only (predicted rate x ACTUAL playing time in T,
which isolates the weighting) and full (rate x the page's expected PT)."""
import json, glob, statistics as st, itertools
from collections import defaultdict
H = "/work/pt_hist"
PT = defaultdict(dict)   # pid -> y -> [pa, ip, gs, g]
def ipf(x):
    try: i, f = str(x).split("."); return int(i) + int(f) / 3
    except Exception: return float(x or 0)
for y in range(2013, 2027):
    for g in ("hitting", "pitching"):
        d = json.load(open(f"{H}/{g}_{y}.json"))
        for s in d["stats"][0]["splits"]:
            pid = s["player"]["id"]; t = s["stat"]; r = PT[pid].setdefault(y, [0, 0, 0, 0])
            if g == "hitting": r[0] += t.get("plateAppearances", 0)
            else: r[1] += ipf(t.get("inningsPitched", 0)); r[2] += t.get("gamesStarted", 0); r[3] += t.get("gamesPlayed", 0)
LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
WAR = {}
for pid, rec in LVM.items():
    d = defaultdict(float)
    for y, t, v in rec["rows"]: d[y] += v
    WAR[pid] = d
AGES = {int(k): v for k, v in json.load(open("/work/ages.json")).items()}
PC = json.load(open("/work/proj_curves.json"))
CUR = PC["curves"]
CAP = {"bat": 680.0, "SP": 195.0, "RP": 75.0}
def role(pid, ys):
    ip = sum(PT[pid].get(y, [0, 0, 0, 0])[1] for y in ys); pa = sum(PT[pid].get(y, [0, 0, 0, 0])[0] for y in ys)
    if ip * 3 < pa: return "bat"
    gs = sum(PT[pid].get(y, [0, 0, 0, 0])[2] for y in ys); g = sum(PT[pid].get(y, [0, 0, 0, 0])[3] for y in ys)
    return "SP" if g and gs / g >= 0.5 else "RP"
def ptv(pid, y, rl):
    r = PT[pid].get(y)
    if not r: return 0.0
    return float(r[0] if rl == "bat" else r[1])
# league rates per role per year
POP = {}
for y in range(2013, 2027):
    acc = defaultdict(lambda: [0.0, 0.0])
    for pid in PT:
        if y not in PT[pid]: continue
        rl = role(pid, [y]); pt = ptv(pid, y, rl)
        if pt > 0: acc[rl][0] += WAR.get(pid, {}).get(y, 0.0); acc[rl][1] += pt
    POP[y] = {k: a[0] / a[1] for k, a in acc.items() if a[1]}
def rows(T):
    out = []
    for pid in PT:
        if T not in PT[pid]: continue
        prev = [y for y in (T-1, T-2, T-3) if y in PT[pid]]
        if not prev: continue
        rl = role(pid, prev)
        if rl != role(pid, [T]): continue
        if ptv(pid, T, rl) < (100 if rl == "bat" else 20): continue
        out.append((pid, rl))
    return out
def predict(pid, rl, T, W, K, use_pt_actual=True, age_on=True):
    num = den = 0.0; ptw = ptd = 0.0; pts = []
    for y, w in zip((T-1, T-2, T-3), W):
        pt = ptv(pid, y, rl)
        if y not in PT[pid] and y < min(PT[pid]): continue
        ptw += w * pt; ptd += w; pts.append(pt)
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    pop = POP[T-1].get(rl, 0.0)
    rate = (num + K[rl] * pop) / (den + K[rl])
    if use_pt_actual: pt_exp = ptv(pid, T, rl)
    else:
        top2 = sorted(pts, reverse=True)[:2]; pt_exp = min(0.6 * (sum(top2) / len(top2)) + 0.4 * (ptw / ptd), CAP[rl]) if ptd else 0
    pred = rate * pt_exp
    if age_on and pid in AGES:
        c = CUR["pit" if rl != "bat" else "bat"]; pred += c.get(str(min(max(T - AGES[pid], 20), 41)), -0.3) * (pt_exp / CAP[rl])
    return pred
TEST = range(2016, 2027)
DATA = [(T, pid, rl, WAR.get(pid, {}).get(T, 0.0)) for T in TEST for pid, rl in rows(T)]
print("rows", len(DATA))
def score(W, Kmult, **kw):
    K = {"bat": 1200 * Kmult, "SP": 600 * Kmult, "RP": 450 * Kmult}
    e = [(predict(pid, rl, T, W, K, **kw) - y) for T, pid, rl, y in DATA]
    return (st.mean(x * x for x in e)) ** 0.5, st.mean(abs(x) for x in e)
res = []
for W in [(5, 4, 3), (6, 3, 1), (5, 3, 2), (7, 3, 1), (8, 4, 1), (6, 4, 2), (4, 3, 2), (10, 4, 1), (1, 0, 0)]:
    for Km in (0.5, 0.75, 1.0, 1.5):
        r, m = score(W, Km); res.append((r, m, W, Km))
res.sort()
for r, m, W, Km in res[:8]: print("rate-only RMSE %.4f MAE %.4f" % (r, m), W, Km)
print("current (5,4,3) K1:", [x for x in res if x[2] == (5, 4, 3) and x[3] == 1.0])
best = res[0]
for W, Km in ((5, 4, 3), 1.0), (best[2], best[3]):
    print("full (expected PT)", W, Km, ["%.4f" % v for v in score(W, Km, use_pt_actual=False)])
json.dump(dict(best=dict(W=best[2], Kmult=best[3], rmse=best[0], mae=best[1]), top=[dict(W=x[2], K=x[3], rmse=round(x[0], 4), mae=round(x[1], 4)) for x in res[:12]]), open("/work/proj_bt.json", "w"), indent=1)

# ---- Nov 9: does a recent drop (or jump) deserve more weight on the latest season?
def rate_of(pid, rl, ys, W):
    num = den = 0.0
    for y, w in zip(ys, W):
        pt = ptv(pid, y, rl)
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    return num / den if den else None
def classify(pid, rl, T):
    last = rate_of(pid, rl, [T-1], [1]); prior = rate_of(pid, rl, [T-2, T-3], [1, 1])
    if last is None or prior is None: return "n/a"
    full = CAP[rl]; d = (last - prior) * full
    ptl = ptv(pid, T-1, rl)
    if ptl < 0.5 * full: return "short"
    return "drop" if d <= -2.0 else "jump" if d >= 2.0 else "flat"
from collections import Counter
cls = {(T, pid): classify(pid, rl, T) for T, pid, rl, y in DATA}
print(Counter(cls.values()))
K = {"bat": 1800, "SP": 900, "RP": 675}
for c in ("drop", "jump", "flat"):
    sub = [(T, pid, rl, y) for T, pid, rl, y in DATA if cls[(T, pid)] == c]
    best = []
    for W in [(5, 3, 2), (5, 4, 3), (7, 3, 1), (8, 3, 1), (10, 3, 1), (4, 3, 3), (3, 3, 3), (1, 0, 0)]:
        e = [(predict(pid, rl, T, W, K) - y) for T, pid, rl, y in sub]
        best.append(((st.mean(x * x for x in e)) ** 0.5, st.mean(e), W))
    best.sort(); print(c, len(sub), [(round(r, 3), round(b, 3), W) for r, b, W in best[:4]], "| (5,3,2) bias", round([b for r, b, W in best if W == (5, 3, 2)][0], 3))

# ---- Nov 9: project defense and baserunning apart, regressed harder
import sys; sys.path.insert(0, "/work")
import lvm15
SV = json.load(open("/work/savant_runs.json"))
DEFW = {}
def defw(pid, y):
    k = (pid, y)
    if k not in DEFW:
        try: r, _ = lvm15.def_runs(pid, y)
        except Exception: r = 0.0
        b = (SV.get(str(pid), {}).get(str(y), {}) or {}).get("bsr", 0.0) if y >= 2016 else 0.0
        DEFW[k] = (r + b) / 10.0
    return DEFW[k]
def predict2(pid, rl, T, W, K, Kd, use_pt_actual=True):
    if rl != "bat": return predict(pid, rl, T, W, K, use_pt_actual)
    num = den = 0.0; dn = dd = 0.0; ptw = ptd = 0.0; pts = []
    for y, w in zip((T-1, T-2, T-3), W):
        pt = ptv(pid, y, rl)
        if y not in PT[pid] and y < min(PT[pid]): continue
        ptw += w * pt; ptd += w; pts.append(pt)
        if pt > 0:
            dv = defw(pid, y); num += w * (WAR.get(pid, {}).get(y, 0.0) - dv); den += w * pt
            dn += w * dv; dd += w * pt
    pop = POP[T-1].get(rl, 0.0)
    rate = (num + K[rl] * pop) / (den + K[rl])
    drate = dn / (dd + Kd) if dd + Kd > 0 else 0.0
    pt_exp = ptv(pid, T, rl) if use_pt_actual else (min(0.6 * (sum(sorted(pts, reverse=True)[:2]) / len(sorted(pts, reverse=True)[:2])) + 0.4 * (ptw / ptd), CAP[rl]) if ptd else 0)
    pred = (rate + drate) * pt_exp
    if pid in AGES: pred += CUR["bat"].get(str(min(max(T - AGES[pid], 20), 41)), -0.3) * (pt_exp / CAP[rl])
    return pred
HIT = [(T, pid, rl, y) for T, pid, rl, y in DATA if rl == "bat"]
K15 = {"bat": 1800, "SP": 900, "RP": 675}
def sc(fn):
    e = [fn(pid, rl, T) - y for T, pid, rl, y in HIT]; return round((st.mean(x * x for x in e)) ** 0.5, 4), round(st.mean(abs(x) for x in e), 4)
print("hitters, one rate (5,3,2) K1.5:", sc(lambda pid, rl, T: predict(pid, rl, T, (5, 3, 2), K15)))
for Kd in (0, 1000, 2000, 4000, 8000):
    print("hitters, defense apart Kd", Kd, sc(lambda pid, rl, T: predict2(pid, rl, T, (5, 3, 2), K15, Kd)))
