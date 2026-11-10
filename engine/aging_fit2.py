import sys; sys.path.insert(0, '.')
from aging_fit import *
CURT = [0.97, 0.94, 0.89, 0.84, 0.78]
def ratio(rows, tbl, off, pit):
    P = [0] * 6; A = [0] * 6; n = 0
    for r in rows:
        if r[2] != pit: continue
        w = walk2(r[0], r[1], r[2], tbl, off); n += 1
        for k in range(6): P[k] += w[k]; A[k] += r[3][k]
    return n, sum(P) / max(sum(A), .01), sum(P[1:3]) / max(sum(A[1:3]), .01), sum(P[3:]) / max(sum(A[3:]), .01)
for name, lo, hi in (("pitchers 2.0+", 2.0, 99), ("pitcher stars 4.0+", 4.0, 99), ("pitchers 1.0-2.0", 1.0, 2.0)):
    for era, y0, y1 in (("2010-14", 2010, 2014), ("2015-19", 2015, 2019), ("2000-09", 2000, 2009)):
        rows = rows_for(lo, hi, y0, y1)
        print(name, era, " | ".join(f"off {o:.2f}: n{ratio(rows, CURT, o, True)[0]} tot {ratio(rows, CURT, o, True)[1]:.2f} y2-3 {ratio(rows, CURT, o, True)[2]:.2f} y4-6 {ratio(rows, CURT, o, True)[3]:.2f}" for o in (0.06, 0.03, 0.0)))
print()
for name, lo, hi in (("hitters 2.0-4.0", 2.0, 4.0), ("hitter stars 4.0+", 4.0, 99)):
    for era, y0, y1 in (("2010-14", 2010, 2014), ("2015-19", 2015, 2019), ("2000-09", 2000, 2009), ("1990-99", 1990, 1999)):
        rows = rows_for(lo, hi, y0, y1); r = ratio(rows, CURT, 0.06, False)
        print(name, era, f"n{r[0]} tot {r[1]:.2f} y2-3 {r[2]:.2f} y4-6 {r[3]:.2f}")
