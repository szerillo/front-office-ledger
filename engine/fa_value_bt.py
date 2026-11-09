"""Nov 9: is the fair value right for hitters and pitchers? For free-agent contracts signed in the
2011-12 to 2021-22 winters (2+ years, $10M+), project the contract years the way the page's fair
offer does (5/3/2 rate x expected playing time, the aging walk, 7%/yr after year two), and compare
with the Ledger WAR each player actually produced in those seasons. Also: what the market paid per
realized win, hitters vs pitchers."""
import json, statistics as st, sys, math
from collections import defaultdict
src = open("/work/calib_suggest.py").read().split("def dk_base")[0]
exec(src)
CROWS = rows
exec(open("/work/proj_bt.py").read().split("TEST = range")[0].replace('PC = json.load(open("/work/proj_curves.json"))', 'PC = json.load(open("/work/proj_curves.json"))'))
CURV = json.load(open("/work/proj_curves.json"))["curves"]
def proj_contract(pid, off, age_sign, pit, yrs, geff=0.93, mode="page"):
    T = off + 1; rl = "bat" if not pit else role(pid, [off, off - 1, off - 2])
    if rl == "RP" and pit: rl = "RP"
    num = den = 0.0; pts = []; ptw = ptd = 0.0
    for y, w in zip((T-1, T-2, T-3), (5, 3, 2)):
        pt = ptv(pid, y, rl); pts.append(pt); ptw += w * pt; ptd += w
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    if not ptd: return None
    K = {"bat": 1800, "SP": 900, "RP": 675}[rl]
    rate = (num + K * POP[T-1][rl]) / (den + K)
    cap = CAP[rl]; top2 = sorted(pts, reverse=True)[:2]; l = pts[0]; p2 = max(pts[1], pts[2])
    a0 = age_sign - 1; inj = l < 0.5 * cap and p2 >= 0.8 * cap
    a = 0.6 if a0 <= 26 else 0.4 if inj else 0.2
    pe = min(a * sum(top2) / len(top2) + (1 - a) * ptw / ptd, cap)
    if mode == "page" and a0 >= 26 and rl in ("bat", "SP"):
        pe0 = pe; mid = 350.0 if rl == "bat" else 0.5 * cap; pe = 0.85 * pe + 0.15 * mid
        full = rate * (600 if rl == "bat" else cap); m, c, lo, thr = (3.5, 0.12, 0.7, 300) if rl == "bat" else (3.0, 0.10, 0.75, 0.45 * cap)
        if pe0 >= thr: pe *= max(lo, min(1.0, 1 + c * (full - m)))
        if l >= 0.75 * cap: pe = min(cap, max(pe, (0.75 if rl == "bat" else 0.70) * l))
    val = rate * pe; curve = CURV["pit" if pit else "bat"]; per = []
    for i in range(1, yrs + 1):
        val += curve.get(str(min(max(age_sign - 1 + i, 20), 41)), -0.3); per.append(max(val, 0.0))
    return per
out = []
for r in CROWS:
    if not (2014 <= r["off"] <= 2022 and r["yrs"] >= 2 and r["tot"] >= 10): continue
    pid = r["pid"]
    if pid not in PT: continue
    per = proj_contract(pid, r["off"], r["age"] + 1, r["pit"], r["yrs"])
    if per is None: continue
    ys = [r["off"] + 1 + i for i in range(r["yrs"]) if r["off"] + 1 + i <= 2026 and r["off"] + 1 + i != 2020]
    idx = [i for i in range(r["yrs"]) if r["off"] + 1 + i in ys]
    real = sum(WAR.get(pid, {}).get(y, 0.0) for y in ys)
    proj = sum(per[i] for i in idx)
    projF = sum(per[i] * 0.93 ** max(0, i - 1) for i in idx)
    dpw = DPWH.get(r["off"] + 1, 9.7)
    out.append(dict(pl=r["pl"], off=r["off"], pit=r["pit"], age=r["age"] + 1, yrs=r["yrs"], tot=r["tot"], n=len(ys), real=real, proj=proj, projF=projF, aavW=(r["tot"] / r["yrs"]) / dpw, frac=len(ys) / r["yrs"]))
print("contracts", len(out))
def summ(v, lbl):
    R = sum(x["real"] for x in v); P = sum(x["proj"] for x in v); PF = sum(x["projF"] for x in v)
    paid = sum(x["aavW"] * x["n"] for x in v)   # wins of money paid over the realized seasons
    print("%-28s n %3d | realized %6.1f  projected %6.1f (ratio %.2f) | fair-weighted %6.1f (ratio %.2f) | paid %6.1f wins: paid/realized %.2f, paid/fair-projected %.2f" % (lbl, len(v), R, P, R / P, PF, R / PF, paid, paid / max(R, 1), paid / PF))
for pit in (0, 1):
    v = [x for x in out if x["pit"] == pit]; summ(v, "PITCHERS" if pit else "HITTERS")
    for lo, hi in ((20, 29), (30, 31), (32, 33), (34, 45)):
        summ([x for x in v if lo <= x["age"] <= hi], ("  P" if pit else "  H") + " age %d-%d" % (lo, hi))
    for yl, yh in ((2, 3), (4, 5), (6, 13)):
        summ([x for x in v if yl <= x["yrs"] <= yh], ("  P" if pit else "  H") + " %d-%d yrs" % (yl, yh))
json.dump(out, open("/work/fa_value_bt.json", "w"))
print("--- by contract year (realized / projected), and with the old playing-time formula")
for mode in ("page", "old"):
    acc = defaultdict(lambda: [0.0, 0.0, 0])
    for r in CROWS:
        if not (2014 <= r["off"] <= 2022 and r["yrs"] >= 2 and r["tot"] >= 10) or r["pid"] not in PT: continue
        per = proj_contract(r["pid"], r["off"], r["age"] + 1, r["pit"], r["yrs"], mode=mode)
        if per is None: continue
        for i in range(min(r["yrs"], 5)):
            y = r["off"] + 1 + i
            if y > 2026 or y == 2020: continue
            a = acc[(r["pit"], i)]; a[0] += WAR.get(r["pid"], {}).get(y, 0.0); a[1] += per[i]; a[2] += 1
    print(mode, " ".join("%s y%d %.2f(n%d)" % ("P" if k[0] else "H", k[1] + 1, v[0] / v[1], v[2]) for k, v in sorted(acc.items())))
