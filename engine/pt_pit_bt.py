"""Nov 9: pitchers. Does expected IP for 27+ run high, does it depend on recent WAR rate, which fix tests best?
proj_bt population (SP 20+ IP in T), expected PT from the page formula (0.2/0.8 at 27+, injury 0.4, 0.6 young)."""
import statistics as st
exec(open("/work/pt_bt.py").read().split("for a, wts in")[0])
def pe_cur(pid, rl, T):
    l = ptv(pid, T-1, rl); p2 = max(ptv(pid, T-2, rl), ptv(pid, T-3, rl)); age = T - 1 - AGES[pid]
    inj = l < 0.5 * CAP[rl] and p2 >= 0.8 * CAP[rl]
    a = 0.6 if age <= 26 else 0.4 if inj else 0.2
    pe = ptexp(pid, rl, T, a, (5, 3, 2))
    if age <= 26 and l >= 0.6 * CAP[rl]: pe = min(max(pe, 0.85 * l), CAP[rl])
    return pe
for RL in ("SP", "RP"):
    rows_ = [dict(T=T, pid=pid, rl=rl, y=y, pe=pe_cur(pid, rl, T), act=ptv(pid, T, rl), r=R[(T, pid)] * CAP[rl], age=T - AGES[pid]) for T, pid, rl, y in DATA if rl == RL and pid in AGES]
    print("==", RL, "rows", len(rows_), "(rate = WAR per full season %d)" % CAP[RL])
    for ag, keep in (("<=26", lambda r: r["age"] <= 26), ("27-30", lambda r: 27 <= r["age"] <= 30), ("31+", lambda r: r["age"] >= 31)):
        v = [r for r in rows_ if keep(r)]
        print("  %-5s n %4d PT bias %+5.1f | by pe band:" % (ag, len(v), st.mean(r["pe"] - r["act"] for r in v)),
              " ".join("[%s: %+.0f n%d]" % (b, st.mean(r["pe"] - r["act"] for r in w), len(w)) for b, w in (("<40%", [r for r in v if r["pe"] < 0.4 * CAP[RL]]), ("40-75%", [r for r in v if 0.4 * CAP[RL] <= r["pe"] < 0.75 * CAP[RL]]), ("75%+", [r for r in v if r["pe"] >= 0.75 * CAP[RL]])) if w),
              "| by rate:", " ".join("[%s: ratio %.2f n%d]" % (b, st.mean(r["act"] for r in w) / st.mean(r["pe"] for r in w), len(w)) for b, w in (("low", [r for r in v if r["r"] < 1.0 and r["pe"] >= 0.5 * CAP[RL]]), ("mid", [r for r in v if 1.0 <= r["r"] < 2.5 and r["pe"] >= 0.5 * CAP[RL]]), ("high", [r for r in v if r["r"] >= 2.5 and r["pe"] >= 0.5 * CAP[RL]])) if w))
    def ev(f, keep=lambda r: True):
        v = [r for r in rows_ if keep(r)]
        ep = [f(r) - r["act"] for r in v]; ew = [R[(r["T"], r["pid"])] * f(r) + AG(r["pid"], r["T"], r["rl"], f(r)) - r["y"] for r in v]
        return "PT %+5.1f (rmse %.1f) WAR %.4f (%+.3f)" % (st.mean(ep), st.mean(x*x for x in ep) ** 0.5, st.mean(x*x for x in ew) ** 0.5, st.mean(ew))
    M = 0.5 * CAP[RL]
    def mk(a, c, m, lo, thr):
        def f(r):
            if r["age"] < 27: return r["pe"]
            pe2 = a * r["pe"] + (1 - a) * M
            if c and r["pe"] >= thr * CAP[RL]: pe2 *= max(lo, min(1.0, 1 + c * (r["r"] - m)))
            return pe2
        return f
    cands = [("baseline", mk(1.0, 0, 0, 1, 1)), ("revert .85", mk(0.85, 0, 0, 1, 1)), ("revert .85 + rate", mk(0.85, 0.12, 3.5, 0.7, 0.45)), ("rate only", mk(1.0, 0.12, 3.5, 0.7, 0.45)), ("revert .85 + rate m3 c.10", mk(0.85, 0.10, 3.0, 0.75, 0.45)), ("revert .8", mk(0.8, 0, 0, 1, 1))]
    for nm, f in cands:
        print("  %-26s all %s | 27+ %s | 27+ 75%%+ %s" % (nm, ev(f), ev(f, lambda r: r["age"] >= 27), ev(f, lambda r: r["age"] >= 27 and r["pe"] >= 0.75 * CAP[RL])))
