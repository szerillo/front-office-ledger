"""Nov 9: should recent performance feed expected playing time? Hitters, walk-forward 2016-2026.
Rows: hitters with 100+ PA in T (the proj_bt population). PT error vs prior WAR rate, then a fit."""
import statistics as st, numpy as np
exec(open("/work/pt_bt.py").read().split("for a, wts in")[0])
HIT = [(T, pid, y) for T, pid, rl, y in DATA if rl == "bat" and pid in AGES]
def pe_cur(pid, T):
    l = ptv(pid, T-1, "bat"); p2 = max(ptv(pid, T-2, "bat"), ptv(pid, T-3, "bat")); age = T - 1 - AGES[pid]
    inj = l < 0.5 * CAP["bat"] and p2 >= 0.8 * CAP["bat"]
    a = 0.6 if age <= 26 else 0.4 if inj else 0.2
    pe = ptexp(pid, "bat", T, a, (5, 3, 2))
    if age <= 26 and l >= 0.6 * CAP["bat"]: pe = min(max(pe, 0.85 * l), CAP["bat"])
    return pe
rows_ = []
for T, pid, y in HIT:
    pe = pe_cur(pid, T); act = ptv(pid, T, "bat"); r600 = R[(T, pid)] * 600
    w26 = WAR[pid].get(T-1, 0.0); l = ptv(pid, T-1, "bat")
    rows_.append(dict(T=T, pid=pid, pe=pe, act=act, err=pe - act, r600=r600, wl=w26, lpa=l, age=T - AGES[pid], y=y, lrate=(w26 / l * 600) if l >= 100 else None))
print("hitter rows", len(rows_), "mean PT error %+.1f PA, rmse %.1f" % (st.mean(r["err"] for r in rows_), st.mean(r["err"] ** 2 for r in rows_) ** 0.5))
print("r(PT error, regressed rate/600) %.3f | r(PT error, last-year WAR) %.3f | r(PT error, age) %.3f" % (
    st.correlation([r["err"] for r in rows_], [r["r600"] for r in rows_]), st.correlation([r["err"] for r in rows_], [r["wl"] for r in rows_]), st.correlation([r["err"] for r in rows_], [r["age"] for r in rows_])))
print("PT error by regressed rate band (WAR/600):")
for lo, hi in ((-9, 0.5), (0.5, 1.5), (1.5, 2.5), (2.5, 3.5), (3.5, 9)):
    v = [r for r in rows_ if lo <= r["r600"] < hi]; print("  %4.1f..%3.1f n %4d  pe %3.0f  actual %3.0f  error %+5.1f" % (lo, hi, len(v), st.mean(r["pe"] for r in v), st.mean(r["act"] for r in v), st.mean(r["err"] for r in v)))
print("PT error by LAST-YEAR WAR rate band, players with 400+ PA last year:")
for lo, hi in ((-9, 0.0), (0.0, 1.0), (1.0, 2.0), (2.0, 3.5), (3.5, 9)):
    v = [r for r in rows_ if r["lpa"] >= 400 and r["lrate"] is not None and lo <= r["lrate"] < hi]
    if v: print("  %4.1f..%3.1f n %4d  pe %3.0f  actual %3.0f  error %+5.1f" % (lo, hi, len(v), st.mean(r["pe"] for r in v), st.mean(r["act"] for r in v), st.mean(r["err"] for r in v)))
# walk-forward fit: act ~ pe + rate600 + age terms, trained on years < T
def X(r): return [r["pe"], r["r600"] * 600 / 600, max(0, r["age"] - 30), 1.0]
pred_fit = {}
for T in range(2019, 2027):
    tr = [r for r in rows_ if r["T"] < T]; te = [r for r in rows_ if r["T"] == T]
    A = np.array([X(r) for r in tr]); b, *_ = np.linalg.lstsq(A, np.array([r["act"] for r in tr]), rcond=None)
    for r in te: pred_fit[(T, r["pid"])] = min(CAP["bat"], max(0, float(np.dot(b, X(r)))))
    if T == 2026: print("fit coefficients (train <2026): pe %.3f, rate/600 %.1f PA per WAR, age>30 %.1f PA/yr, const %.1f" % tuple(b))
te = [r for r in rows_ if (r["T"], r["pid"]) in pred_fit]
e0 = [r["pe"] - r["act"] for r in te]; e1 = [pred_fit[(r["T"], r["pid"])] - r["act"] for r in te]
print("PT rmse 2019-26: current %.1f -> with WAR rate %.1f (bias %+.1f -> %+.1f)" % (st.mean(x*x for x in e0) ** 0.5, st.mean(x*x for x in e1) ** 0.5, st.mean(e0), st.mean(e1)))
w0 = [R[(r["T"], r["pid"])] * r["pe"] + AG(r["pid"], r["T"], "bat", r["pe"]) - r["y"] for r in te]
w1 = [R[(r["T"], r["pid"])] * pred_fit[(r["T"], r["pid"])] + AG(r["pid"], r["T"], "bat", pred_fit[(r["T"], r["pid"])]) - r["y"] for r in te]
print("WAR rmse 2019-26: current %.4f -> with WAR-informed PT %.4f (bias %+.3f -> %+.3f)" % (st.mean(x*x for x in w0) ** 0.5, st.mean(x*x for x in w1) ** 0.5, st.mean(w0), st.mean(w1)))
for lo, hi in ((-9, 0.5), (0.5, 1.5), (1.5, 2.5), (2.5, 9)):
    v = [r for r in te if lo <= r["r600"] < hi]
    a0 = [R[(r["T"], r["pid"])] * r["pe"] + AG(r["pid"], r["T"], "bat", r["pe"]) - r["y"] for r in v]; a1 = [R[(r["T"], r["pid"])] * pred_fit[(r["T"], r["pid"])] + AG(r["pid"], r["T"], "bat", pred_fit[(r["T"], r["pid"])]) - r["y"] for r in v]
    print("  rate %4.1f..%3.1f n %4d WAR bias %+.3f -> %+.3f, rmse %.3f -> %.3f" % (lo, hi, len(v), st.mean(a0), st.mean(a1), st.mean(x*x for x in a0) ** 0.5, st.mean(x*x for x in a1) ** 0.5))
