# Nov 9: aging-curve variants in the walk-forward backtest (FanGraphs community joint-model article check)
import itertools
src = open("/work/proj_bt.py").read().split("res = []")[0]
exec(src)
import statistics as st
BASE = {k: dict(v) for k, v in CUR.items()}
def mk(scale=1.0, shift=0.0, flat_after=None):
    out = {}
    for rl, c in BASE.items():
        d = {}
        for a in range(18, 45):
            x = a + shift; lo = int(x // 1); f = x - lo
            g = lambda z: c.get(str(min(max(z, 20 if rl == "bat" else 21), 41)), -0.3)
            v = (1 - f) * g(lo) + f * g(lo + 1)
            d[str(a)] = v * scale
        out[rl] = d
    return out
K = {"bat": 1800, "SP": 900, "RP": 675}
def sc(cur, pt):
    CUR.clear(); CUR.update(cur)
    e = [(predict(pid, rl, T, (5, 3, 2), K, use_pt_actual=pt) - y) for T, pid, rl, y in DATA]
    # by age band too
    return (st.mean(x * x for x in e)) ** 0.5, st.mean(e)
def band(cur):
    CUR.clear(); CUR.update(cur); b = {}
    for T, pid, rl, y in DATA:
        if pid not in AGES: continue
        a = T - AGES[pid]; k = "<=25" if a <= 25 else "26-29" if a <= 29 else "30-32" if a <= 32 else "33+"
        b.setdefault(k, []).append(predict(pid, rl, T, (5, 3, 2), K, use_pt_actual=True) - y)
    return {k: "%+.3f" % st.mean(v) for k, v in sorted(b.items())}
for nm, cur in [] and [("current", mk()), ("no aging", mk(0)), ("x0.5", mk(0.5)), ("x1.5", mk(1.5)), ("x2", mk(2)),
                ("peak -0.5y", mk(1, 0.5)), ("peak -1y", mk(1, 1.0)), ("peak +1y", mk(1, -1.0)), ("x1.5 peak-0.5", mk(1.5, 0.5))]:
    r1, b1 = sc(cur, True); r2, b2 = sc(cur, False)
    print("%-14s rate-only %.4f (bias %+.3f) | full %.4f (bias %+.3f)" % (nm, r1, b1, r2, b2), band(cur))
print("--- asymmetric: growth side kept, decline side scaled")
def asym(sd, pivot=27):
    out = {}
    for rl, c in BASE.items():
        out[rl] = {k: (v * sd if (int(k) >= pivot and v < 0) else v) for k, v in c.items()}
    return out
for sd in (1.25, 1.5, 1.75, 2.0):
    cur = asym(sd); r1, b1 = sc(cur, True); r2, b2 = sc(cur, False)
    print("decline x%.2f   rate-only %.4f (bias %+.3f) | full %.4f (bias %+.3f)" % (sd, r1, b1, r2, b2), band(cur))
