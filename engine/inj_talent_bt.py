"""Nov 9: are talented but injury-prone hitters under-projected?
Walk-forward 2018-2026 on the pt_model rows. Projection = 5/3/2 regressed rate (K 1800) x ridge PA + aging.
Splits the miss into rate (WAR per 600 when he played) and playing time."""
import io, contextlib, statistics as st, numpy as np
src = open("/work/pt_model.py").read().split("EVAL = [r for r")[0]
with contextlib.redirect_stdout(io.StringIO()): exec(src)
def peak600(pid, T, yrs=4, minpa=250):
    xs = [WAR.get(pid, {}).get(y, 0.0) * SC(y) / pa(pid, y) * 600 for y in range(T - yrs, T) if pa(pid, y) >= minpa]
    return max(xs) if xs else None
def r1(pid, T):
    p_ = pa(pid, T - 1); return WAR.get(pid, {}).get(T - 1, 0.0) * SC(T - 1) / p_ * 600 if p_ >= 150 else None
def ag(r, p_): return CUR["bat"].get(str(min(max(r["age"], 20), 41)), -0.3) * p_ / 680
EV = [r for r in TR if r["T"] >= 2018]
for r in EV:
    r["C"] = predC[(r["T"], r["pid"])]; r["pk"] = peak600(r["pid"], r["T"]); r["l600"] = r1(r["pid"], r["T"])
    r["proj"] = r["r600"] / 600 * r["C"] + ag(r, r["C"])
    r["ilp"] = sum(r["il" + k] >= 0.15 for k in "123") >= 2 or r["il1"] >= 0.25
    r["act600"] = r["y"] / r["act"] * 600 if r["act"] >= 100 else None
def show(nm, rs):
    if not rs: return
    m = [r["proj"] - r["y"] for r in rs]
    pt = [r["C"] - r["act"] for r in rs]
    rr = [r for r in rs if r["act600"] is not None]
    rate = st.mean(r["r600"] + ag(r, 600) - r["act600"] for r in rr) if rr else float("nan")
    print("%-52s n %4d | WAR proj %.2f actual %.2f bias %+.2f | PA bias %+5.0f | rate per 600 bias %+.2f (n %d)" % (
        nm, len(rs), st.mean(r["proj"] for r in rs), st.mean(r["y"] for r in rs), st.mean(m), st.mean(pt), rate, len(rr)))
show("all", EV)
show("IL-prone", [r for r in EV if r["ilp"]])
for lo, hi in ((3.5, 4.5), (4.5, 6), (6, 99)):
    show(f"peak 600-rate {lo}-{hi} (last 4 yrs)", [r for r in EV if r["pk"] and lo <= r["pk"] < hi])
    show(f"  ... and IL-prone", [r for r in EV if r["pk"] and lo <= r["pk"] < hi and r["ilp"]])
    show(f"  ... and last season < 2.5 per 600", [r for r in EV if r["pk"] and lo <= r["pk"] < hi and r["l600"] is not None and r["l600"] < 2.5])
    show(f"  ... IL-prone and down last season", [r for r in EV if r["pk"] and lo <= r["pk"] < hi and r["ilp"] and r["l600"] is not None and r["l600"] < 2.5])
show("rate-gap: peak minus 5/3/2 rate >= 2.0", [r for r in EV if r["pk"] and r["pk"] - r["r600"] >= 2.0])
show("rate-gap >= 2.0 and IL-prone", [r for r in EV if r["pk"] and r["pk"] - r["r600"] >= 2.0 and r["ilp"]])
show("rate-gap >= 3.0", [r for r in EV if r["pk"] and r["pk"] - r["r600"] >= 3.0])
import pickle; pickle.dump(EV, open("/work/inj_rows.pkl", "wb"))
