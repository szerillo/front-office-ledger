exec(open("/work/proj_bt.py").read().split("TEST = range")[0])
import statistics as st
TEST = range(2016, 2027)
DATA = [(T, pid, rl, WAR.get(pid, {}).get(T, 0.0)) for T in TEST for pid, rl in rows(T)]
K = {"bat": 1800, "SP": 900, "RP": 675}; W = (5, 3, 2)
def ptexp(pid, rl, T, a, wts):
    pts = []; ptw = ptd = 0.0
    for y, w in zip((T-1, T-2, T-3), wts):
        if y not in PT[pid] and y < min(PT[pid]): continue
        pt = ptv(pid, y, rl); pts.append(pt); ptw += w * pt; ptd += w
    if not ptd: return 0.0
    top2 = sorted(pts, reverse=True)[:2]
    return min(a * (sum(top2) / len(top2)) + (1 - a) * (ptw / ptd), CAP[rl])
def rate(pid, rl, T):
    num = den = 0.0
    for y, w in zip((T-1, T-2, T-3), W):
        pt = ptv(pid, y, rl)
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    pop = POP[T-1].get(rl, 0.0); return (num + K[rl] * pop) / (den + K[rl])
R = {(T, pid): rate(pid, rl, T) for T, pid, rl, y in DATA}
AG = lambda pid, T, rl, pt: (CUR["pit" if rl != "bat" else "bat"].get(str(min(max(T - AGES[pid], 20), 41)), -0.3) * pt / CAP[rl]) if pid in AGES else 0
for a, wts in ((0.6, (5, 4, 3)), (0.6, (5, 3, 2)), (0.4, (5, 3, 2)), (0.2, (5, 3, 2)), (0.0, (5, 3, 2)), (0.0, (6, 3, 1)), (0.3, (6, 3, 1))):
    out = {}
    for grp, f in (("all", lambda pid, T: True), ("28+", lambda pid, T: pid in AGES and T - AGES[pid] >= 28), ("<=27", lambda pid, T: pid in AGES and T - AGES[pid] <= 27)):
        e = []; ept = []
        for T, pid, rl, y in DATA:
            if not f(pid, T): continue
            pt = ptexp(pid, rl, T, a, wts); pred = R[(T, pid)] * pt + AG(pid, T, rl, pt)
            e.append(pred - y); ept.append((pt - ptv(pid, T, rl)) / CAP[rl])
        out[grp] = (round((st.mean(x*x for x in e))**0.5, 4), round(st.mean(ept), 3))
    print("PT a=%.1f" % a, wts, out)
print("--- subgroups, 28+")
def grp(pid, rl, T):
    l = ptv(pid, T-1, rl) / CAP[rl]; p2 = max(ptv(pid, T-2, rl), ptv(pid, T-3, rl)) / CAP[rl]
    return "injury year" if l < 0.5 and p2 >= 0.8 else "bench turn" if l < 0.5 and p2 >= 0.5 else "steady" if l >= 0.5 else "part-time"
for a in (0.6, 0.4, 0.2, 0.0):
    out = {}
    for T, pid, rl, y in DATA:
        if not (pid in AGES and T - AGES[pid] >= 28): continue
        g = grp(pid, rl, T); pt = ptexp(pid, rl, T, a, (5, 3, 2)); pred = R[(T, pid)] * pt + AG(pid, T, rl, pt)
        out.setdefault(g, []).append(pred - y)
    print(a, {g: (len(e), round((st.mean(x*x for x in e))**0.5, 3), round(st.mean(e), 3)) for g, e in sorted(out.items())})
