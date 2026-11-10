import sys, json; sys.path.insert(0, '.')
from aging_bt import *
def rows_for(lo, hi, y0=1990, y1=2019):
    out = []
    for pid, by in BY.items():
        b = AGES.get(str(pid))
        if not b: continue
        pit = POS.get(str(pid)) in PIT
        for Y in range(y0, y1 + 1):
            obs = [(by.get(Y, 0), 5), (by.get(Y - 1, 0), 3), (by.get(Y - 2, 0), 2)]
            obs = [(v, w) for v, w in obs if abs(v) > 0.05]
            if not obs or abs(by.get(Y, 0)) <= 0.05: continue
            base = 0.85 * sum(v * w for v, w in obs) / sum(w for _, w in obs) + 0.15 * POP
            age0 = Y - b
            curve = CUR["pit" if pit else "bat"]
            y1p = max(base + curve.get(str(min(max(age0 + 1, 20), 41)), -0.3), 0)
            if lo <= y1p < hi: out.append((base, age0, pit, [by.get(Y + k, 0) for k in range(1, 7)], Y))
    return out
def walk2(base, age0, pit, tbl, off):
    curve = CUR["pit" if pit else "bat"]; val = base; surv = 1; out = []
    for i in range(1, 7):
        age = age0 + i; val += curve.get(str(min(max(age, 20), 41)), -0.3)
        if i >= 2:
            s = tbl[0] if age <= 26 else tbl[1] if age <= 29 else tbl[2] if age <= 32 else tbl[3] if age <= 35 else tbl[4]
            surv *= min(1.0, max(0.5, s - (off if pit else 0)))
        out.append(max(val, 0) * surv)
    return out
BK = (("23-26", 0, 26), ("27-29", 27, 29), ("30-32", 30, 32), ("33-36", 33, 36), ("37+", 37, 99))
def loss(rows, tbl, off, pit):
    tot = 0
    for _, a, b in BK:
        g = [r for r in rows if r[2] == pit and a <= r[1] + 1 <= b]
        if len(g) < 12: continue
        P = [0] * 6; A = [0] * 6
        for r in g:
            w = walk2(r[0], r[1], r[2], tbl, off)
            for k in range(6): P[k] += w[k]; A[k] += r[3][k]
        tot += sum((P[k] - A[k]) ** 2 / len(g) for k in range(1, 6))
    return tot
def fit(rows):
    tbl = [0.97, 0.94, 0.89, 0.84, 0.78]
    for _ in range(4):
        for j in range(5):
            best = min((loss(rows, tbl[:j] + [v / 100] + tbl[j + 1:], 0, False), v / 100) for v in range(70, 101))
            tbl[j] = best[1]
        # keep it monotone: older never survives better than younger
        for j in range(1, 5): tbl[j] = min(tbl[j], tbl[j - 1])
    off = min((loss(rows, tbl, o / 100, True), o / 100) for o in range(0, 16))[1]
    return tbl, off
def show(rows, tbl, off, title):
    print(title, "table", tbl, "pitcher offset", off)
    for pit in (False, True):
        for lbl, a, b in BK:
            g = [r for r in rows if r[2] == pit and a <= r[1] + 1 <= b]
            if len(g) < 12: continue
            P = [0] * 6; A = [0] * 6
            for r in g:
                w = walk2(r[0], r[1], r[2], tbl, off)
                for k in range(6): P[k] += w[k] / len(g); A[k] += r[3][k] / len(g)
            print(f"  {'pit' if pit else 'bat'} {lbl:6s} n{len(g):4d} pred " + " ".join(f"{x:4.1f}" for x in P) + " | act " + " ".join(f"{x:4.1f}" for x in A) + f" | total {sum(P)/sum(A):.2f} y4-6 {sum(P[3:])/max(sum(A[3:]),.01):.2f}")
if __name__ == "__main__":
    res = {}
    for name, lo, hi in (("stars", 4.0, 99), ("regulars", 2.0, 4.0)):
        tr = rows_for(lo, hi, 1990, 2009); te = rows_for(lo, hi, 2010, 2019); allr = tr + te
        tbl, off = fit(tr)
        show(te, tbl, off, f"\n{name}: fit on 1990-2009, tested on 2010-2019:")
        show(te, [0.97, 0.94, 0.89, 0.84, 0.78], 0.06, f"{name}: current rule on 2010-2019:")
        tbl2, off2 = fit(allr); res[name] = (tbl2, off2)
        show(allr, tbl2, off2, f"{name}: final fit on all years:")
    json.dump(res, open('aging_fit.json', 'w'))
