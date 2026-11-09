"""Nov 9 (3): the performance factor on the full proj_bt population (hitters, 100+ PA in T), by prior-PT band."""
import statistics as st
exec(open("/work/pt_war_bt.py").read().split("rows_ = []")[0])
rows_ = []
for T, pid, y in HIT:
    pe = pe_cur(pid, T); act = ptv(pid, T, "bat"); r600 = R[(T, pid)] * 600
    rows_.append(dict(T=T, pid=pid, pe=pe, act=act, r600=r600, age=T - AGES[pid], y=y, l=ptv(pid, T-1, "bat")))
def fac(r, c=0.12, m=3.5, lo=0.7, amin=27, scale=False):
    if r["age"] < amin: return 1.0
    f = max(lo, min(1.0, 1 + c * (r["r600"] - m)))
    if scale: f = 1 - (1 - f) * min(1.0, r["pe"] / 450.0)   # smaller cut for part-timers
    return f
def ev(v, f):
    ep = [r["pe"] * f(r) - r["act"] for r in v]; ew = [R[(r["T"], r["pid"])] * r["pe"] * f(r) + AG(r["pid"], r["T"], "bat", r["pe"] * f(r)) - r["y"] for r in v]
    return "PT %+5.0f (rmse %.0f) WAR %.4f (%+.3f)" % (st.mean(ep), st.mean(x*x for x in ep) ** 0.5, st.mean(x*x for x in ew) ** 0.5, st.mean(ew))
for nm, f in (("baseline", lambda r: 1.0), ("factor 27+", lambda r: fac(r)), ("factor 27+, scaled by pe/450", lambda r: fac(r, scale=True)), ("factor 27+, only pe>=300", lambda r: fac(r) if r["pe"] >= 300 else 1.0)):
    print("%-30s all: %s" % (nm, ev(rows_, f)))
    for lo, hi in ((0, 200), (200, 400), (400, 560), (560, 800)):
        v = [r for r in rows_ if lo <= r["pe"] < hi and r["age"] >= 27]
        print("      27+ pe %3d-%3d n %4d: %s" % (lo, hi, len(v), ev(v, f)))
print("== mean reversion for 27+: pe' = a*pe + (1-a)*M, then the rate factor when pe >= 300")
def comb(a, M, usef):
    def f(r):
        if r["age"] < 27: return 1.0
        pe2 = a * r["pe"] + (1 - a) * M
        if usef and r["pe"] >= 300: pe2 *= max(0.7, min(1.0, 1 + 0.12 * (r["r600"] - 3.5)))
        return pe2 / r["pe"] if r["pe"] else 1.0
    return f
for a, M in ((1.0, 0), (0.9, 350), (0.85, 350), (0.8, 350), (0.85, 300), (0.85, 400)):
    for usef in (False, True):
        f = comb(a, M, usef)
        print("a=%.2f M=%3d factor=%s | all: %s | " % (a, M, usef, ev(rows_, f)) + " ".join("[%d-%d: %s]" % (lo, hi, ev([r for r in rows_ if lo <= r["pe"] < hi and r["age"] >= 27], f)) for lo, hi in ((0, 200), (400, 560), (560, 800))))
