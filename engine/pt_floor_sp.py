import statistics as st
exec(open("/work/pt_pit_bt.py").read().split('for RL in ("SP", "RP"):')[0])
RL = "SP"; CAPR = CAP[RL]
rows_ = [dict(T=T, pid=pid, rl=rl, y=y, pe=pe_cur(pid, rl, T), act=ptv(pid, T, rl), r=R[(T, pid)] * CAPR, age=T - AGES[pid], l=ptv(pid, T-1, rl), p1=ptv(pid, T-2, rl), p2=ptv(pid, T-3, rl)) for T, pid, rl, y in DATA if rl == RL and pid in AGES]
def new(r, floor=None):
    if r["age"] < 27: return r["pe"]
    pe2 = 0.85 * r["pe"] + 0.15 * 0.5 * CAPR
    if r["pe"] >= 0.45 * CAPR: pe2 *= max(0.75, min(1.0, 1 + 0.10 * (r["r"] - 3.0)))
    if floor is not None and r["l"] >= 0.75 * CAPR: pe2 = max(pe2, floor * r["l"])
    return min(CAPR, pe2)
def ev(v, f):
    ep = [f(r) - r["act"] for r in v]; ew = [R[(r["T"], r["pid"])] * f(r) + AG(r["pid"], r["T"], "SP", f(r)) - r["y"] for r in v]
    return "PT %+5.1f (rmse %3.0f, ratio %.2f) WAR %.4f (%+.3f) n %d" % (st.mean(ep), st.mean(x*x for x in ep) ** 0.5, st.mean(r["act"] for r in v) / st.mean(f(r) for r in v), st.mean(x*x for x in ew) ** 0.5, st.mean(ew), len(v))
for g, keep in {"27+ last full": lambda r: r["age"] >= 27 and r["l"] >= 0.75 * CAPR, "27+ last full, both prior < 60%": lambda r: r["age"] >= 27 and r["l"] >= 0.75 * CAPR and r["p1"] < 0.6 * CAPR and r["p2"] < 0.6 * CAPR, "27+ all": lambda r: r["age"] >= 27}.items():
    v = [r for r in rows_ if keep(r)]; print("--", g)
    for nm, f in (("old", lambda r: r["pe"]), ("shipped", lambda r: new(r)), ("floor .70", lambda r: new(r, 0.70)), ("floor .75", lambda r: new(r, 0.75)), ("floor .80", lambda r: new(r, 0.80))):
        print("   %-10s %s" % (nm, ev(v, f)))
