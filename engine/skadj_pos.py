"""Nov 9: does the Statcast skill adjustment (xwOBA gap, sprint, sprint change) help or hurt by position group?"""
import csv, json, statistics as st
from collections import defaultdict
exec(open("/work/pos_bt.py").read().split("K = 1800.0")[0])
F = json.load(open("/work/skill_adj.json"))["fit"]["H"]; cf = F["coef"]; mu = F["mu"]
def rd(path):
    try: return list(csv.DictReader(open(path, encoding="utf-8-sig")))
    except Exception: return []
XW = defaultdict(dict); SPD = defaultdict(dict)
for y in range(2016, 2027):
    for r in rd(f"/work/savant_hist/xb_{y}.csv"):
        if r.get("pa") and float(r["pa"]) >= 150: XW[int(r["player_id"])][y] = float(r["est_woba"]) - float(r["woba"])
    for r in rd(f"/work/savant_hist/spd_{y}.csv"):
        if r.get("sprint_speed"): SPD[int(r["player_id"])][y] = float(r["sprint_speed"])
def adj(pid, y, parts=("xg", "spd", "dspd")):
    if y not in XW[pid]: return 0.0
    sp = SPD[pid]; r = dict(xg=XW[pid][y], spd=sp.get(y, mu["spd"]), dspd=(sp[y] - sp[y-1]) if (y in sp and y-1 in sp) else 0.0)
    a = sum(c * (r[x] - mu[x]) for c, x in zip(cf, ("xg", "spd", "dspd")) if x in parts)
    a = max(-0.8, min(0.8, a)); return a if abs(a) >= 0.02 else 0.0
K = 1800.0; W = (5, 3, 2)
def pred(pid, T):
    num = den = 0.0
    for y, w in zip((T-1, T-2, T-3), W):
        pt = ptv(pid, y, "bat")
        if y not in PT[pid] and y < min(PT[pid]): continue
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    rate = (num + K * POP[T-1]["bat"]) / (den + K); pt_exp = ptv(pid, T, "bat"); pr = rate * pt_exp
    if pid in AGES: pr += CUR["bat"].get(str(min(max(T - AGES[pid], 20), 41)), -0.3) * (pt_exp / CAP["bat"])
    return pr, pt_exp
res = defaultdict(lambda: defaultdict(list))
for T in range(2017, 2027):
    for pid, rl in rows(T):
        if rl != "bat" or (T-1) not in XW[pid]: continue
        y = WAR.get(pid, {}).get(T, 0.0); p0, pe = pred(pid, T); g = grp(pid, (T-1, T-2, T-3))
        # the page scales nothing: adj is added as WAR on the full projection (built for a full season); scale by PT share here
        sh = pe / CAP["bat"]
        for nm, parts in (("none", ()), ("full", ("xg", "spd", "dspd")), ("xg only", ("xg",)), ("spd only", ("spd",)), ("xg+dspd", ("xg", "dspd"))):
            e = p0 + adj(pid, T-1, parts) * sh - y
            res["all"][nm].append(e); res[g][nm].append(e)
def fmt(v): return "%.4f (%+.3f)" % ((st.mean(x * x for x in v)) ** 0.5, st.mean(v))
print("rmse (bias), hitters with a Statcast line the year before, PT share scaled")
for g in sorted(res, key=lambda g: -len(res[g]["none"])):
    print("%-5s n %4d | " % (g, len(res[g]["none"])) + " | ".join("%-8s %s" % (k, fmt(v)) for k, v in res[g].items()))
