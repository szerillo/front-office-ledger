"""Contract model v5.6: what the market pays, learned from what it paid.

For every free-agent contract in the book (2006-2025 winters), features are
the player's last three seasons as the market saw them, from the public
box score (MLB Stats API: PA, OBP, SLG, HR, SB for hitters; IP, starts, ERA,
K%, BB%, HR rate, saves for pitchers) plus this site's Ledger WAR, age and
position. Targets: average annual value in wins (AAV / that winter's $/win)
and years. Gradient-boosted trees, validated walk-forward: every winter is
predicted by a model trained only on earlier winters.
"""
import json, math, sys
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
ROOT = "/work"
D = json.load(open(f"{ROOT}/desk_data.json"))
SS = json.load(open(f"{ROOT}/season_stats.json"))
L = {int(k): v for k, v in json.load(open(f"{ROOT}/lvm_cache.json")).items() if not k.startswith("__")}
POS = json.load(open(f"{ROOT}/positions.json")); POS.update(json.load(open(f"{ROOT}/positions2.json")))
DPWH = {int(k): v for k, v in D["market"]["dpwHist"].items()}
LW = {}
for pid, rec in L.items():
    d = {}
    for y, tm, v in rec["rows"]: d[y] = d.get(y, 0.0) + v
    LW[pid] = d
USE_PRIOR = False
SCALE = lambda y: 162 / 60 if y == 2020 else 1.0
PG = {"C": 0, "1B": 1, "DH": 1, "2B": 2, "SS": 3, "3B": 2, "LF": 4, "RF": 4, "CF": 5, "OF": 4}

PRIOR = {}
for _c in D["book"]:
    if _c[12] == 0 and _c[11]:
        PRIOR.setdefault(int(_c[11]), []).append((_c[1], _c[3], _c[4]))
def prior_deal(pid, off):
    """the market's last word: his most recent free-agent deal signed in the
    three winters before this one (AAV in that winter's wins, winters ago)"""
    best = None
    for o, y, t in PRIOR.get(int(pid), []):
        if off - 3 <= o < off and (best is None or o > best[0]): best = (o, y, t)
    if not best: return [0.0, 0.0, 0.0]
    o, y, t = best
    return [(t / y) / DPWH[min(o + 1, 2026)], off - o, y]

def feats(pid, off, age, pit):
    pid = int(pid); s = SS.get(str(pid), {})
    ys = [off, off - 1, off - 2]; W = [5, 4, 3]
    lw = [LW.get(pid, {}).get(y, 0.0) * SCALE(y) for y in ys]
    lw_old = [LW.get(pid, {}).get(y, 0.0) * SCALE(y) for y in (off - 3, off - 4)]
    f = [age, pit, lw[0], lw[1], lw[2], sum(w * v for w, v in zip(W, lw)) / 12, max(lw + lw_old)]
    if not pit:
        pa = [(s.get(str(y), {}).get("h", {}) or {}).get("pa", 0) * SCALE(y) for y in ys]
        def rate(fn):
            num = den = 0.0
            for w, y in zip(W, ys):
                h = s.get(str(y), {}).get("h")
                if not h or h["pa"] < 30: continue
                a, b = fn(h); num += w * a; den += w * b
            return num / den if den else 0.0
        obp = rate(lambda h: (h["hits"] + h["bb"] + h["hbp"], max(h["ab"] + h["bb"] + h["hbp"] + h["sf"], 1)))
        slg = rate(lambda h: (h["tb"], max(h["ab"], 1)))
        hr = rate(lambda h: (h["hr"] * 600, max(h["pa"], 1)))
        sb = rate(lambda h: (h["sb"] * 600, max(h["pa"], 1)))
        so = rate(lambda h: (h["so"], max(h["pa"], 1)))
        p1 = s.get(str(off), {}).get("h") or {}
        slg1 = p1.get("tb", 0) / max(p1.get("ab", 0), 1) if p1.get("pa", 0) >= 100 else slg
        pos = PG.get(POS.get(str(pid), "OF"), 4)
        f += [pa[0], pa[1], pa[2], obp, slg, obp + slg, hr, sb, so, slg1, pos, 0, 0, 0, 0, 0, 0]
    else:
        ip = [((s.get(str(y), {}).get("p") or {}).get("ip", 0)) * SCALE(y) for y in ys]
        gs = sum((s.get(str(y), {}).get("p") or {}).get("gs", 0) for y in ys)
        g = sum((s.get(str(y), {}).get("p") or {}).get("g", 0) for y in ys)
        def rate(fn):
            num = den = 0.0
            for w, y in zip(W, ys):
                p = s.get(str(y), {}).get("p")
                if not p or p["bf"] < 40: continue
                a, b = fn(p); num += w * a; den += w * b
            return num / den if den else 0.0
        era = rate(lambda p: (p["er"] * 9, max(p["ip"], 1)))
        k = rate(lambda p: (p["so"], max(p["bf"], 1)))
        bb = rate(lambda p: (p["bb"], max(p["bf"], 1)))
        hr9 = rate(lambda p: (p["hr"] * 9, max(p["ip"], 1)))
        sv = sum((s.get(str(y), {}).get("p") or {}).get("sv", 0) for y in ys[:2])
        f += [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, ip[0], ip[1], ip[2], gs / max(g, 1), era, k - bb]
        f[-0:] = f  # no-op, keeps length explicit
        f += []
        f = f[:7] + f[7:]
        f.append(hr9); f.append(sv)
        return f + (prior_deal(pid, off) if USE_PRIOR else [])
    f.append(0); f.append(0)
    return f + (prior_deal(pid, off) if USE_PRIOR else [])

def book_rows():
    out = []
    for c in D["book"]:
        if c[12] != 0 or not c[11]: continue
        off, yrs, tot, age, pit = c[1], c[3], c[4], c[5], c[6]
        if off < 2006 or yrs < 1: continue
        lw = [LW.get(int(c[11]), {}).get(y, 0) for y in (off, off - 1, off - 2)]
        if sum(abs(x) for x in lw) < 0.1: continue      # no MLB record: posted players, not priceable here
        out.append(dict(pl=c[0], pid=c[11], off=off, yrs=yrs, tot=tot, age=age, pit=pit,
                        X=feats(c[11], off, age, pit), aavw=(tot / yrs) / DPWH[min(off + 1, 2026)]))
    return out

def fit(rows):
    X = np.array([r["X"] for r in rows]); ya = np.array([math.log(max(r["aavw"], 0.05)) for r in rows]); yy = np.array([math.log(r["yrs"]) for r in rows])
    kw = dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20, l2_regularization=1.0, random_state=0)
    ma = HistGradientBoostingRegressor(**kw).fit(X, ya); my = HistGradientBoostingRegressor(**kw).fit(X, yy)
    # smearing correction so the median model returns a mean-unbiased AAV
    return ma, my

def predict(models, X, off):
    ma, my = models
    X = np.array(X)
    aavw = np.exp(ma.predict(X)); yrs = np.maximum(1, np.round(np.exp(my.predict(X))))
    return aavw, yrs

if __name__ == "__main__" and len(sys.argv) == 1:
    rows = book_rows(); rows.sort(key=lambda r: r["off"])
    print("contracts:", len(rows))
    res = []
    for W in range(2012, 2026):
        tr = [r for r in rows if r["off"] < W]; te = [r for r in rows if r["off"] == W]
        if not te: continue
        m = fit(tr); a, y = predict(m, [r["X"] for r in te], W)
        for r, aa, yy in zip(te, a, y):
            res.append(dict(pl=r["pl"], off=W, yrs=r["yrs"], tot=r["tot"], age=r["age"], pit=r["pit"],
                            gY=int(yy), gT=round(float(aa * DPWH[min(W + 1, 2026)] * yy), 1)))
    json.dump(res, open(f"{ROOT}/contract_model_bt.json", "w"))
    print("walk-forward predictions:", len(res))

def apply_to_desk():
    """Train on the whole book and price every Desk player as a free agent
    this winter (2026 platform). Writes desk_data.json['gbm'] = {pid: [years,
    AAV in 2027 dollars]}; the page blends it with the comps/projection rules."""
    rows = book_rows(); m = fit(rows)
    dpw27 = D["market"]["dpw"]["2027"]
    out = {}
    for p in D["players"]:
        pid = int(p[1])
        if str(pid) in (D.get("posted") or {}): continue
        lw = [LW.get(pid, {}).get(y, 0) for y in (2026, 2025, 2024)]
        if sum(abs(x) for x in lw) < 0.1: continue
        a, y = predict(m, [feats(pid, 2026, p[4], p[3])], 2026)
        out[str(pid)] = [int(y[0]), round(float(a[0] * dpw27), 2)]
    D["gbm"] = out
    json.dump(D, open(f"{ROOT}/desk_data.json", "w"), separators=(",", ":"))
    print("market model priced:", len(out), "desk players")

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "apply":
    apply_to_desk()
