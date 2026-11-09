"""Nov 9 (2): same question, unconditional population: hitters with 300+ PA in T-1 (age <= 35),
actual PA in T counted even when 0. Fit a multiplicative performance factor on expected PT."""
import statistics as st, numpy as np
exec(open("/work/pt_war_bt.py").read().split("rows_ = []")[0])
rows_ = []
for T in range(2016, 2027):
    for pid in PT:
        if (T-1) not in PT[pid] or pid not in AGES: continue
        if role(pid, [T-1]) != "bat" or ptv(pid, T-1, "bat") < 300 or T - AGES[pid] > 35: continue
        pe = pe_cur(pid, T); act = ptv(pid, T, "bat") if T in PT[pid] else 0.0
        num = den = 0.0
        for y, w in zip((T-1, T-2, T-3), (5, 3, 2)):
            pt = ptv(pid, y, "bat")
            if pt > 0: num += w * WAR[pid].get(y, 0.0); den += w * pt
        r600 = (num + 1800 * POP[T-1]["bat"]) / (den + 1800) * 600
        l = ptv(pid, T-1, "bat"); lrate = WAR[pid].get(T-1, 0.0) / l * 600
        rows_.append(dict(T=T, pid=pid, pe=pe, act=act, r600=r600, lrate=lrate, age=T - AGES[pid], y=WAR[pid].get(T, 0.0) if T in PT[pid] else 0.0, zero=act == 0))
print("rows", len(rows_), "zero-PA next year:", sum(r["zero"] for r in rows_), "| mean PT error %+.1f" % st.mean(r["pe"] - r["act"] for r in rows_))
print("by regressed rate (WAR/600):")
for lo, hi in ((-9, 0.5), (0.5, 1.5), (1.5, 2.5), (2.5, 3.5), (3.5, 9)):
    v = [r for r in rows_ if lo <= r["r600"] < hi]; print("  %4.1f..%3.1f n %4d  pe %3.0f  actual %3.0f  error %+5.1f  ratio %.2f  zero %.0f%%" % (lo, hi, len(v), st.mean(r["pe"] for r in v), st.mean(r["act"] for r in v), st.mean(r["pe"] - r["act"] for r in v), st.mean(r["act"] for r in v) / st.mean(r["pe"] for r in v), 100 * st.mean(r["zero"] for r in v)))
print("by last-year rate (WAR/600):")
for lo, hi in ((-9, 0.0), (0.0, 1.0), (1.0, 2.0), (2.0, 3.5), (3.5, 9)):
    v = [r for r in rows_ if lo <= r["lrate"] < hi]; print("  %4.1f..%3.1f n %4d  pe %3.0f  actual %3.0f  ratio %.2f" % (lo, hi, len(v), st.mean(r["pe"] for r in v), st.mean(r["act"] for r in v), st.mean(r["act"] for r in v) / st.mean(r["pe"] for r in v)))
# multiplicative factor: pe * clip(1 + c * (r600 - m), lo, hi); walk-forward choose c on years < T from a grid
def apply(r, c, m=2.0, lo=0.7, hi=1.1): return min(CAP["bat"], r["pe"] * max(lo, min(hi, 1 + c * (r["r600"] - m))))
def warp(r, pt): return R.get((r["T"], r["pid"]), r["r600"] / 600) * pt + AG(r["pid"], r["T"], "bat", pt)
for pop_name, keep in (("all (0 PA counted)", lambda r: True), ("played 100+ in T", lambda r: r["act"] >= 100)):
    print("--", pop_name)
    for c in (0.0, 0.05, 0.08, 0.10, 0.12, 0.15):
        v = [r for r in rows_ if keep(r)]
        ep = [apply(r, c) - r["act"] for r in v]; ew = [warp(r, apply(r, c)) - r["y"] for r in v]
        print("  c=%.2f  PT rmse %.1f bias %+.1f | WAR rmse %.4f bias %+.3f" % (c, st.mean(x*x for x in ep) ** 0.5, st.mean(ep), st.mean(x*x for x in ew) ** 0.5, st.mean(ew)))
print("== factor never above 1: pe * max(lo, min(1, 1 + c*(r600 - m)))")
best = []
for m in (2.0, 2.5, 3.0, 3.5):
    for c in (0.05, 0.08, 0.10, 0.12, 0.15, 0.2):
        for lo in (0.6, 0.7):
            out = []
            for keep in (lambda r: True, lambda r: r["act"] >= 100):
                v = [r for r in rows_ if keep(r)]
                ep = [apply(r, c, m, lo, 1.0) - r["act"] for r in v]; ew = [warp(r, apply(r, c, m, lo, 1.0)) - r["y"] for r in v]
                out.append((st.mean(x*x for x in ep) ** 0.5, st.mean(ep), st.mean(x*x for x in ew) ** 0.5, st.mean(ew)))
            best.append((out[1][2], m, c, lo, out))
best.sort()
for s, m, c, lo, out in best[:8]:
    print("m=%.1f c=%.2f lo=%.1f | all: PT %.1f (%+.0f) WAR %.4f (%+.3f) | played: PT %.1f (%+.0f) WAR %.4f (%+.3f)" % (m, c, lo, *out[0], *out[1]))
print("baseline                 | all: PT 203.4 (+70) WAR 1.7614 (+0.335) | played: PT 174.3 (+38) WAR 1.8024 (+0.261)")
m, c, lo = best[0][1], best[0][2], best[0][3]
print("by band with best (played 100+):")
for a, b in ((-9, 0.5), (0.5, 1.5), (1.5, 2.5), (2.5, 3.5), (3.5, 9)):
    v = [r for r in rows_ if r["act"] >= 100 and a <= r["r600"] < b]
    e0 = [warp(r, r["pe"]) - r["y"] for r in v]; e1 = [warp(r, apply(r, c, m, lo, 1.0)) - r["y"] for r in v]
    print("  %4.1f..%3.1f n %4d  WAR rmse %.3f -> %.3f  bias %+.3f -> %+.3f | PT pe %.0f -> %.0f, actual %.0f" % (a, b, len(v), st.mean(x*x for x in e0) ** 0.5, st.mean(x*x for x in e1) ** 0.5, st.mean(e0), st.mean(e1), st.mean(r["pe"] for r in v), st.mean(apply(r, c, m, lo, 1.0) for r in v), st.mean(r["act"] for r in v)))
print("== candidates by age group (played 100+ and all)")
def ev(f, keep):
    v = [r for r in rows_ if keep(r)]
    ep = [f(r) - r["act"] for r in v]; ew = [warp(r, f(r)) - r["y"] for r in v]
    return "PT %.0f (%+.0f) WAR %.4f (%+.3f)" % (st.mean(x*x for x in ep) ** 0.5, st.mean(ep), st.mean(x*x for x in ew) ** 0.5, st.mean(ew))
cands = {"baseline": lambda r: r["pe"],
         "m3 c.10 lo.75": lambda r: apply(r, 0.10, 3.0, 0.75, 1.0),
         "m3 c.15 lo.7": lambda r: apply(r, 0.15, 3.0, 0.7, 1.0),
         "m3.5 c.12 lo.7": lambda r: apply(r, 0.12, 3.5, 0.7, 1.0),
         "m3 c.10 lo.75, 27+ only": lambda r: apply(r, 0.10, 3.0, 0.75, 1.0) if r["age"] >= 27 else r["pe"],
         "m3.5 c.12 lo.7, 27+ only": lambda r: apply(r, 0.12, 3.5, 0.7, 1.0) if r["age"] >= 27 else r["pe"]}
for nm, f in cands.items():
    print("%-26s | all %s | played %s | <=26 played %s | 27+ played %s | 27+ all %s" % (nm, ev(f, lambda r: True), ev(f, lambda r: r["act"] >= 100), ev(f, lambda r: r["act"] >= 100 and r["age"] <= 26), ev(f, lambda r: r["act"] >= 100 and r["age"] >= 27), ev(f, lambda r: r["age"] >= 27)))
print("ratio actual/pe by rate band and age, played 100+:")
for ag, keep in (("<=26", lambda r: r["age"] <= 26), ("27-30", lambda r: 27 <= r["age"] <= 30), ("31+", lambda r: r["age"] >= 31)):
    print(" ", ag, ["%.1f-%.1f: %.2f (n%d)" % (a, b, st.mean(r["act"] for r in v) / st.mean(r["pe"] for r in v), len(v)) for a, b in ((-9, 1.0), (1.0, 2.0), (2.0, 3.0), (3.0, 9)) for v in [[r for r in rows_ if keep(r) and r["act"] >= 100 and a <= r["r600"] < b]] if v])
