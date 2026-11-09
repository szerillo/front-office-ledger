"""Nov 9: infield defense. Ledger WAR uses DRS for 1B/2B/3B/SS; Statcast FRV is
the alternative. Which is more reliable year to year, and which predicts the
other's next season? Infielders 2016-2026 with 700+ innings at IF in both years."""
import json, statistics as st, numpy as np
F = json.load(open("/work/frv_runs.json")); D = json.load(open("/work/drs_runs.json"))
IF = ("3", "4", "5", "6")
rows = []
for pid, d in D.items():
    if pid.startswith("__"): continue
    f = F.get(pid, {})
    for y in range(2016, 2026):
        a, b = d.get(str(y)), d.get(str(y + 1))
        fa, fb = f.get(str(y)), f.get(str(y + 1))
        if not (a and b and fa and fb): continue
        ia = sum(a.get("inn", {}).get(p, 0) for p in IF); ib = sum(b.get("inn", {}).get(p, 0) for p in IF)
        if ia < 700 or ib < 700: continue
        da = sum(a["pos"].get(p, 0) for p in IF); db = sum(b["pos"].get(p, 0) for p in IF)
        va = sum(fa.get("pos", {}).get(p, 0) for p in IF); vb = sum(fb.get("pos", {}).get(p, 0) for p in IF)
        # per 1200 innings
        rows.append((da / ia * 1200, db / ib * 1200, va / ia * 1200, vb / ib * 1200))
A = np.array(rows); print("pairs", len(A))
c = lambda i, j: round(float(np.corrcoef(A[:, i], A[:, j])[0, 1]), 3)
print("sd per 1200 inn: DRS %.1f  FRV %.1f" % (A[:, 0].std(), A[:, 2].std()))
print("same-year r(DRS, FRV)", c(0, 2))
print("y/y reliability: DRS", c(0, 1), " FRV", c(2, 3))
print("cross: DRS(t)->FRV(t+1)", c(0, 3), " FRV(t)->DRS(t+1)", c(2, 1))
# best predictor of next year's average of the two (a neutral target)
tgt = (A[:, 1] + A[:, 3]) / 2
for nm, x in (("DRS", A[:, 0]), ("FRV", A[:, 2]), ("avg", (A[:, 0] + A[:, 2]) / 2)):
    s = np.polyfit(x, tgt, 1); r = np.corrcoef(x, tgt)[0, 1]
    print("%s -> next-year avg(DRS,FRV): r %.3f slope %.3f" % (nm, r, s[0]))
X = np.c_[A[:, 0], A[:, 2], np.ones(len(A))]; b, *_ = np.linalg.lstsq(X, tgt, rcond=None)
print("joint fit next avg = %.3f*DRS + %.3f*FRV + %.2f" % tuple(b))
# how much does each predict ITS OWN next year (regression slope = how much to keep)
for nm, i, j in (("DRS", 0, 1), ("FRV", 2, 3)):
    s = np.polyfit(A[:, i], A[:, j], 1); print("%s own next-year slope %.3f" % (nm, s[0]))
