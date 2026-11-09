"""Nov 9: refit the hitter Statcast adjustment on the CURRENT baseline (5/3/2, K1800, aging),
with and without age, to see whether sprint speed is an age proxy. Train 2017-2022, test 2023-2026."""
import numpy as np, statistics as st
exec(open("/work/skadj_pos.py").read().split("res = defaultdict")[0])
R = []
for T in range(2017, 2027):
    for pid, rl in rows(T):
        if rl != "bat" or (T-1) not in XW[pid] or pid not in AGES: continue
        y = WAR.get(pid, {}).get(T, 0.0); p0, pe = pred(pid, T); sp = SPD[pid]
        if (T-1) not in sp: continue
        R.append(dict(T=T, pid=pid, res=y - p0, sh=pe / CAP["bat"], xg=XW[pid][T-1], spd=sp[T-1], dspd=(sp[T-1] - sp.get(T-2, sp[T-1])), age=T - AGES[pid], g=grp(pid, (T-1, T-2, T-3)), y=y, p0=p0))
tr = [r for r in R if r["T"] <= 2022]; te = [r for r in R if r["T"] >= 2023]
print("train", len(tr), "test", len(te))
def fit(feats):
    X = np.array([[r[f] for f in feats] + [1.0] for r in tr]); yv = np.array([r["res"] / r["sh"] for r in tr]); w = np.array([r["sh"] for r in tr])
    b, *_ = np.linalg.lstsq(X * w[:, None] ** 0.5, yv * w ** 0.5, rcond=None)
    def adj(r): return float(np.dot(b, [r[f] for f in feats] + [1.0])) - b[-1] * 0  # keep intercept out? report both
    return b, adj
def score(adj, rs, clip=0.8):
    e = []
    for r in rs:
        a = max(-clip, min(clip, adj(r))) if adj else 0.0
        e.append(r["p0"] + a * r["sh"] - r["y"])
    return "rmse %.4f bias %+.3f" % ((st.mean(x * x for x in e)) ** 0.5, st.mean(e))
print("none           ", score(None, te))
for feats in (["xg"], ["spd"], ["xg", "spd", "dspd"], ["age"], ["xg", "age"], ["xg", "spd", "dspd", "age"], ["xg", "dspd", "age"]):
    b, adj = fit(feats)
    # drop the intercept when applying (the page adds the adjustment to a baseline that is already centered)
    adj0 = lambda r, b=b, feats=feats: float(np.dot(b[:-1], [r[f] for f in feats]) - np.dot(b[:-1], [MU[f] for f in feats]))
    MU = {f: st.mean(r[f] for r in tr) for f in feats}
    print("%-26s" % "+".join(feats), score(adj0, te), "| coef", {f: round(float(c), 3) for f, c in zip(feats, b[:-1])})
# catchers and the speed term
b, adj = fit(["xg", "spd", "dspd"]); MU = {f: st.mean(r[f] for r in tr) for f in ("xg", "spd", "dspd")}
adjf = lambda r: float(np.dot(b[:-1], [r[f] for f in ("xg", "spd", "dspd")]) - np.dot(b[:-1], [MU[f] for f in ("xg", "spd", "dspd")]))
for g in ("C", "MI", "CF", "1B", "DH", "COF", "3B"):
    sub = [r for r in te if r["g"] == g]; print("  %-4s n %3d  none %s | full %s" % (g, len(sub), score(None, sub), score(adjf, sub)))
# fast vs slow
for lo, hi in ((20, 26), (26, 27.5), (27.5, 29), (29, 32)):
    sub = [r for r in te if lo <= r["spd"] < hi]; print("  spd %.1f-%.1f n %3d  none %s | full %s" % (lo, hi, len(sub), score(None, sub), score(adjf, sub)))
