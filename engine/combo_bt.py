"""Nov 9: combined candidates for hitters: steeper decline curve x Statcast adjustment variants.
Train adj 2017-2022, test 2023-2026 (hitters with a Statcast line the year before)."""
import numpy as np, statistics as st, json
exec(open("/work/skadj_pos.py").read().split("res = defaultdict")[0])
BASE = dict(CUR["bat"])
def curve(sd):
    return {k: (v * sd if (int(k) >= 27 and v < 0) else v) for k, v in BASE.items()}
def predc(pid, T, cv):
    num = den = 0.0
    for y, w in zip((T-1, T-2, T-3), W):
        pt = ptv(pid, y, "bat")
        if y not in PT[pid] and y < min(PT[pid]): continue
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    rate = (num + K * POP[T-1]["bat"]) / (den + K); pt_exp = ptv(pid, T, "bat"); pr = rate * pt_exp
    if pid in AGES: pr += cv.get(str(min(max(T - AGES[pid], 20), 41)), -0.3) * (pt_exp / CAP["bat"])
    return pr, pt_exp
ROWS = []
for T in range(2017, 2027):
    for pid, rl in rows(T):
        if rl != "bat" or (T-1) not in XW[pid] or pid not in AGES: continue
        sp = SPD[pid]
        if (T-1) not in sp: continue
        ROWS.append(dict(T=T, pid=pid, y=WAR.get(pid, {}).get(T, 0.0), xg=XW[pid][T-1], spd=sp[T-1], dspd=sp[T-1] - sp.get(T-2, sp[T-1]), age=T - AGES[pid]))
def run(sd, feats, label, clip=0.8):
    cv = curve(sd)
    for r in ROWS: r["p0"], pe = predc(r["pid"], r["T"], cv); r["sh"] = pe / CAP["bat"]; r["res"] = r["y"] - r["p0"]
    tr = [r for r in ROWS if r["T"] <= 2022]; te = [r for r in ROWS if r["T"] >= 2023]
    if feats:
        X = np.array([[r[f] for f in feats] + [1.0] for r in tr]); yv = np.array([r["res"] / r["sh"] for r in tr]); w = np.sqrt(np.array([r["sh"] for r in tr]))
        b, *_ = np.linalg.lstsq(X * w[:, None], yv * w, rcond=None); MU = {f: st.mean(r[f] for r in tr) for f in feats}
        adj = lambda r: max(-clip, min(clip, float(sum(c * (r[f] - MU[f]) for c, f in zip(b[:-1], feats)))))
    else: adj = lambda r: 0.0; b = []
    out = []
    for nm, rs in (("test 23-26", te), ("all 17-26", ROWS)):
        e = [r["p0"] + adj(r) * r["sh"] - r["y"] for r in rs]
        out.append("%s rmse %.4f bias %+.3f" % (nm, (st.mean(x * x for x in e)) ** 0.5, st.mean(e)))
    # age bands on test
    ab = []
    for lo, hi in ((20, 26), (27, 30), (31, 34), (35, 45)):
        e = [r["p0"] + adj(r) * r["sh"] - r["y"] for r in te if lo <= r["age"] <= hi]; ab.append("%d-%d %+.2f" % (lo, hi, st.mean(e)))
    print("%-34s | %s | age bias: %s | coef %s" % (label, " | ".join(out), ", ".join(ab), {f: round(float(c), 3) for f, c in zip(feats, b[:-1])} if feats else ""))
run(1.0, [], "A0 current curve, no adj")
run(1.0, ["xg", "spd", "dspd"], "A current curve + xg/spd/dspd")
run(1.5, [], "B decline x1.5, no adj")
run(1.5, ["xg"], "C decline x1.5 + xg")
run(1.5, ["xg", "dspd"], "C2 decline x1.5 + xg/dspd")
run(1.5, ["xg", "spd", "dspd"], "D decline x1.5 + xg/spd/dspd")
run(1.75, ["xg"], "E decline x1.75 + xg")
run(2.0, ["xg"], "F decline x2 + xg")
run(1.5, ["xg", "age"], "G decline x1.5 + xg/age (check)")
