"""Nov 9: combined check, hitters (proj_bt population): PT fix (27+: 0.85*pe+52.5, rate factor when pe>=300) x decline curve 1.5."""
import statistics as st
exec(open("/work/pt_war_bt.py").read().split("rows_ = []")[0])
BASE = dict(CUR["bat"])
def cv(sd): return {k: (v * sd if (int(k) >= 27 and v < 0) else v) for k, v in BASE.items()}
def ptfix(r600, pe, age):
    if age < 27: return pe
    pe2 = 0.85 * pe + 52.5
    if pe >= 300: pe2 *= max(0.7, min(1.0, 1 + 0.12 * (r600 - 3.5)))
    return pe2
def ag(pid, T, pt, c): return c.get(str(min(max(T - AGES[pid], 20), 41)), -0.3) * pt / CAP["bat"]
rows_ = [(T, pid, y, pe_cur(pid, T), R[(T, pid)], T - AGES[pid]) for T, pid, y in HIT]
def ev(fix, sd, keep=lambda a: True):
    c = cv(sd); e = []
    for T, pid, y, pe, rt, a in rows_:
        if not keep(a): continue
        pt = ptfix(rt * 600, pe, a) if fix else pe
        e.append(rt * pt + ag(pid, T, pt, c) - y)
    return "rmse %.4f bias %+.3f" % (st.mean(x*x for x in e) ** 0.5, st.mean(e))
for fix, sd, nm in ((False, 1.0, "current"), (True, 1.0, "PT fix"), (False, 1.5, "decline x1.5"), (True, 1.5, "PT fix + decline x1.5"), (True, 1.75, "PT fix + decline x1.75")):
    print("%-24s all %s | <=26 %s | 27-30 %s | 31-34 %s | 35+ %s" % (nm, ev(fix, sd), ev(fix, sd, lambda a: a <= 26), ev(fix, sd, lambda a: 27 <= a <= 30), ev(fix, sd, lambda a: 31 <= a <= 34), ev(fix, sd, lambda a: a >= 35)))
