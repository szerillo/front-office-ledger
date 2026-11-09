import json, statistics as st, sys
src = open("/work/proj_bt.py").read()
pre = src.split("res = []")[0]; tail = src.split("# ---- Nov 9: project defense and baserunning apart, regressed harder")[1]
exec(pre); exec("import sys; sys.path.insert(0, '/work')\n" + tail.split("HIT = ")[0])
HIT = [(T, pid, rl, y) for T, pid, rl, y in DATA if rl == "bat"]
K15 = {"bat": 1800, "SP": 900, "RP": 675}
def sc(fn, sub=HIT):
    e = [fn(pid, rl, T) - y for T, pid, rl, y in sub]; return round((st.mean(x * x for x in e)) ** 0.5, 4), round(st.mean(e), 4)
print("hitters, one rate:", sc(lambda pid, rl, T: predict(pid, rl, T, (5, 3, 2), K15)))
for Kd in (0, 500, 1000, 2000, 4000, 8000):
    print("defense+bsr apart Kd", Kd, sc(lambda pid, rl, T: predict2(pid, rl, T, (5, 3, 2), K15, Kd)))
# subgroup: big defensive totals (|L3 def+bsr| >= 1.5 WAR)
big = [(T, pid, rl, y) for T, pid, rl, y in HIT if abs(sum(defw(pid, yy) for yy in (T-1, T-2, T-3))) >= 1.5]
print("big-defense subgroup n", len(big))
print("  one rate:", sc(lambda pid, rl, T: predict(pid, rl, T, (5, 3, 2), K15), big))
for Kd in (0, 1000, 2000, 4000):
    print("  apart Kd", Kd, sc(lambda pid, rl, T: predict2(pid, rl, T, (5, 3, 2), K15, Kd), big))
# persistence: year-to-year r of def+bsr per 600 vs offense per 600 (400+ PA both years)
D1 = []; O1 = []
for T, pid, rl, y in HIT:
    if ptv(pid, T, rl) >= 400 and ptv(pid, T-1, rl) >= 400:
        d0, d1 = defw(pid, T-1) / ptv(pid, T-1, rl) * 600, defw(pid, T) / ptv(pid, T, rl) * 600
        o0 = (WAR[pid].get(T-1, 0) - defw(pid, T-1)) / ptv(pid, T-1, rl) * 600; o1 = (WAR[pid].get(T, 0) - defw(pid, T)) / ptv(pid, T, rl) * 600
        D1.append((d0, d1)); O1.append((o0, o1))
print("y/y r: def+bsr", round(st.correlation([a for a, b in D1], [b for a, b in D1]), 3), "| offense+pos", round(st.correlation([a for a, b in O1], [b for a, b in O1]), 3), "n", len(D1))
import numpy as np
for nm, X in (("def", D1), ("off", O1)):
    a = np.array(X); s = np.polyfit(a[:, 0], a[:, 1], 1); print(nm, "slope next on last %.3f intercept %.3f" % (s[0], s[1]))
