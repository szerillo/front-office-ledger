"""Nov 9: 27+ hitters whose LAST season was full (>= 75% of 680 PA). Does the new PT rule cut them too much,
and does a floor at a share of last season's PA help? Also the subgroup with partial seasons before (the Bauers shape)."""
import statistics as st
exec(open("/work/pt_war_bt.py").read().split("rows_ = []")[0])
rows_ = []
for T, pid, y in HIT:
    pe = pe_cur(pid, T); act = ptv(pid, T, "bat"); r600 = R[(T, pid)] * 600; a = T - AGES[pid]
    l, p1, p2 = ptv(pid, T-1, "bat"), ptv(pid, T-2, "bat"), ptv(pid, T-3, "bat")
    rows_.append(dict(T=T, pid=pid, pe=pe, act=act, r600=r600, age=a, y=y, l=l, p1=p1, p2=p2))
def new(r, floor=None):
    if r["age"] < 27: return r["pe"]
    pe2 = 0.85 * r["pe"] + 52.5
    if r["pe"] >= 300: pe2 *= max(0.7, min(1.0, 1 + 0.12 * (r["r600"] - 3.5)))
    if floor is not None and r["l"] >= 0.75 * 680: pe2 = max(pe2, floor * r["l"])
    return min(680, pe2)
def ev(v, f):
    ep = [f(r) - r["act"] for r in v]; ew = [R[(r["T"], r["pid"])] * f(r) + AG(r["pid"], r["T"], "bat", f(r)) - r["y"] for r in v]
    return "PT %+5.0f (rmse %3.0f, ratio %.2f) WAR %.4f (%+.3f) n %d" % (st.mean(ep), st.mean(x*x for x in ep) ** 0.5, st.mean(r["act"] for r in v) / st.mean(f(r) for r in v), st.mean(x*x for x in ew) ** 0.5, st.mean(ew), len(v))
groups = {"27+ last full": lambda r: r["age"] >= 27 and r["l"] >= 510,
          "27+ last full, both prior < 400 (Bauers shape)": lambda r: r["age"] >= 27 and r["l"] >= 510 and r["p1"] < 400 and r["p2"] < 400,
          "27+ last full, prior full": lambda r: r["age"] >= 27 and r["l"] >= 510 and r["p1"] >= 510,
          "31+ last full": lambda r: r["age"] >= 31 and r["l"] >= 510,
          "27+ all": lambda r: r["age"] >= 27}
for g, keep in groups.items():
    v = [r for r in rows_ if keep(r)]
    print("--", g)
    for nm, f in (("old formula", lambda r: r["pe"]), ("shipped", lambda r: new(r)), ("floor .70 last", lambda r: new(r, 0.70)), ("floor .75 last", lambda r: new(r, 0.75)), ("floor .80 last", lambda r: new(r, 0.80)), ("floor .85 last", lambda r: new(r, 0.85))):
        print("   %-16s %s" % (nm, ev(v, f)))
