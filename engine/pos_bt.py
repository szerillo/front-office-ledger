"""Nov 9: hitters only. Does regressing to a POSITION-GROUP mean (instead of the
all-hitter mean) help, and does the Statcast skill adjustment mistreat catchers?
Walk-forward 2016-2026 like proj_bt (5/3/2, K 1800), actual PT, aging on."""
import json, statistics as st
from collections import defaultdict
src = open("/work/proj_bt.py").read().split("res = []")[0]
exec(src)
# primary position per player-season from the MLB API season files
POSN = defaultdict(dict)
for y in range(2013, 2027):
    d = json.load(open(f"/work/mlb_hist/hit_{y}.json"))
    for s in d["stats"][0]["splits"]:
        POSN[s["player"]["id"]][y] = s.get("position", {}).get("abbreviation", "?")
GRP = {"C": "C", "SS": "MI", "2B": "MI", "CF": "CF", "3B": "3B", "LF": "COF", "RF": "COF", "1B": "1B", "DH": "DH"}
def grp(pid, ys):
    c = defaultdict(int)
    for y in ys: c[GRP.get(POSN[pid].get(y, "?"), "OTH")] += ptv(pid, y, "bat")
    return max(c, key=c.get) if c else "OTH"
# group rates per year (WAR per PA), hitters
GP = {}
for y in range(2013, 2027):
    acc = defaultdict(lambda: [0.0, 0.0])
    for pid in PT:
        if y not in PT[pid] or role(pid, [y]) != "bat": continue
        pt = ptv(pid, y, "bat")
        if pt > 0: g = grp(pid, [y]); acc[g][0] += WAR.get(pid, {}).get(y, 0.0); acc[g][1] += pt
    GP[y] = {k: a[0] / a[1] for k, a in acc.items() if a[1] > 2000}
print("2026 group rates per 600 PA:", {k: round(v * 600, 2) for k, v in GP[2026].items()})
K = 1800.0; W = (5, 3, 2)
def pred(pid, T, target):
    num = den = 0.0
    for y, w in zip((T-1, T-2, T-3), W):
        pt = ptv(pid, y, "bat")
        if y not in PT[pid] and y < min(PT[pid]): continue
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    rate = (num + K * target) / (den + K); pt_exp = ptv(pid, T, "bat"); pr = rate * pt_exp
    if pid in AGES: pr += CUR["bat"].get(str(min(max(T - AGES[pid], 20), 41)), -0.3) * (pt_exp / CAP["bat"])
    return pr
DATA = [(T, pid, WAR.get(pid, {}).get(T, 0.0)) for T in range(2016, 2027) for pid, rl in rows(T) if rl == "bat"]
print("hitter rows", len(DATA))
res = defaultdict(lambda: defaultdict(list))
for T, pid, y in DATA:
    g = grp(pid, (T-1, T-2, T-3)); pa = ptv(pid, T, "bat")
    e0 = pred(pid, T, POP[T-1]["bat"]) - y
    tgt = GP[T-1].get(g, POP[T-1]["bat"])
    e1 = pred(pid, T, tgt) - y
    # half-way: blend group and league mean
    e2 = pred(pid, T, 0.5 * tgt + 0.5 * POP[T-1]["bat"]) - y
    res["all"]["league"].append(e0); res["all"]["group"].append(e1); res["all"]["half"].append(e2)
    res[g]["league"].append(e0); res[g]["group"].append(e1); res[g]["half"].append(e2)
    if pa >= 400:
        res["reg_" + g]["league"].append(e0); res["reg_" + g]["group"].append(e1)
def fmt(v): return "rmse %.4f bias %+.3f n %d" % ((st.mean(x * x for x in v)) ** 0.5, st.mean(v), len(v))
for g in sorted(res):
    print("%-8s" % g, " | ".join("%s: %s" % (k, fmt(v)) for k, v in res[g].items()))
