"""Nov 2026: does a peak-talent term help hitters with an elite recent peak who are coming off a down
year (Luis Robert Jr. type)? Rows from inj_talent_bt.py (walk-forward 2018-2026, ridge playing time).
Candidate: rate' = r600 + w * (peak600 - r600) for players whose best season in the last four
(250+ PA) ran at 6+ WAR per 600 and whose last season ran under 2.5. w chosen walk-forward."""
import pickle, statistics as st
EV = pickle.load(open("/work/inj_rows.pkl", "rb"))
def grp(r, pk_min=6.0, last_max=2.5): return r["pk"] is not None and r["pk"] >= pk_min and r["l600"] is not None and r["l600"] < last_max
def proj(r, w, pk_min=6.0):
    rate = r["r600"] + (w * (r["pk"] - r["r600"]) if grp(r, pk_min) else 0)
    return rate / 600 * r["C"] + (r["proj"] - r["r600"] / 600 * r["C"])
def score(rs, w, pk_min=6.0):
    e = [proj(r, w, pk_min) - r["y"] for r in rs]
    return st.mean(x * x for x in e) ** 0.5, st.mean(e)
G = [r for r in EV if grp(r)]
print("group n", len(G))
for w in (0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4):
    print("w %.2f | group rmse %.3f bias %+.3f | all rmse %.4f bias %+.3f" % ((w,) + score(G, w) + score(EV, w)))
# walk-forward: choose w on seasons before T, score on T
ws = [x / 20 for x in range(0, 11)]
errs0, errs1 = [], []
for T in sorted({r["T"] for r in EV}):
    tr = [r for r in G if r["T"] < T]; te = [r for r in G if r["T"] == T]
    if len(tr) < 20 or not te: continue
    w = min(ws, key=lambda w: score(tr, w)[0])
    for r in te: errs0.append(proj(r, 0) - r["y"]); errs1.append(proj(r, w) - r["y"])
    print(T, "w", w, "n", len(te))
f = lambda e: (st.mean(x * x for x in e) ** 0.5, st.mean(e))
print("walk-forward group: without %.3f (%+.3f)  with %.3f (%+.3f)  n %d" % (f(errs0) + f(errs1) + (len(errs0),)))
for pkm in (5.0, 5.5, 6.0, 7.0):
    Gp = [r for r in EV if grp(r, pkm)]
    print("peak >= %.1f: n %d, best in-sample w" % (pkm, len(Gp)), min(ws, key=lambda w: score(Gp, w, pkm)[0]), "rmse 0 %.3f" % score(Gp, 0, pkm)[0], "bias %+.3f" % score(Gp, 0, pkm)[1])
