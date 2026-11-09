"""Nov 9: hitter playing time as availability x role, walk-forward 2016-2026.

Inputs per prior season y (T-1, T-2, T-3):
  PA_y          plate appearances (MLB Stats API; 2020 scaled x162/60)
  il_y          injured-list share of the season (il_days.json from the transaction sweep)
  role_y        PA per healthy team game: PA_y / (162 x (1 - il_y)), capped at 4.6
  vl_y          share of PA against left-handers, minus the league share for his bat side
  gap_y         OPS vs right-handers minus OPS vs left-handers (sign flipped for left-handed
                pitchers' side is not needed: the platoon side is the weak side)
Target: PA in season T (0 if he did not play), hitters 37 or younger with 150+ PA in T-1.

Models compared on the same rows:
  A  shipped formula (desk_data: weighted/top-two blend, 27+ reversion, rate cut, last-season floor)
  B  structural: 162 x expected availability x expected role
  C  ridge on A's inputs plus the availability, role and platoon features (walk-forward)
  D  gradient boosting on the same features (reference only: not explainable enough to ship)
Then WAR: the 5/3/2 regressed rate x predicted PA + the aging step, against actual WAR."""
import json, statistics as st, numpy as np
from collections import defaultdict
src = open("/work/proj_bt.py").read().split("TEST = range")[0]
exec(src)
IL = json.load(open("/work/il_days.json")); ILD = IL["days"]; SEAS = {int(k): v for k, v in IL["season"].items()}
BAT = json.load(open("/work/splits/batside.json"))
G = defaultdict(dict)
for y in range(2013, 2027):
    for s in json.load(open(f"/work/mlb_hist/hit_{y}.json"))["stats"][0]["splits"]:
        G[s["player"]["id"]][y] = s["stat"].get("gamesPlayed", 0)
SPL = defaultdict(dict)   # pid -> y -> {vl: (pa, ops), vr: (pa, ops)}
for y in range(2013, 2027):
    for c in ("vl", "vr"):
        for s in json.load(open(f"/work/splits/h_{c}_{y}.json"))["stats"][0]["splits"]:
            t = s["stat"]
            try: ops = float(t.get("ops") or 0)
            except Exception: ops = 0.0
            SPL[s["player"]["id"]].setdefault(y, {})[c] = (t.get("plateAppearances", 0), ops)
POST = defaultdict(dict); GMAXP = {}
for y in range(2013, 2027):
    ss = json.load(open(f"/work/splits/h_posas_{y}.json"))["stats"][0]["splits"]
    GMAXP[y] = max([s["stat"].get("gamesPlayed", 0) for s in ss] or [0]) or 70
    for s in ss: POST[s["player"]["id"]][y] = (s["stat"].get("plateAppearances", 0), s["stat"].get("gamesPlayed", 0))
def postf(pid, y):
    """after the All-Star break: share of team games played and PA per game against the first half"""
    pp, gp = POST.get(pid, {}).get(y, (0, 0)); tp = ptv(pid, y, "bat"); gt = G.get(pid, {}).get(y, 0)
    if gt < 20: return 0.0, 0.0
    pre_g, pre_p = gt - gp, tp - pp
    pagd = (pp / gp - pre_p / pre_g) if (gp >= 10 and pre_g >= 10) else 0.0
    return gp / GMAXP[y], pagd
# league share of PA vs LHP by bat side and year (hitters with 200+ PA)
LGV = {}
for y in range(2013, 2027):
    acc = defaultdict(lambda: [0, 0])
    for pid, d in SPL.items():
        z = d.get(y, {}); a, b = z.get("vl", (0, 0))[0], z.get("vr", (0, 0))[0]
        if a + b >= 200: k = BAT.get(str(pid), "R"); acc[k][0] += a; acc[k][1] += a + b
    LGV[y] = {k: v[0] / v[1] for k, v in acc.items() if v[1]}
SC = lambda y: 162 / 60 if y == 2020 else 1.0
def pa(pid, y): return ptv(pid, y, "bat") * SC(y)
def ils(pid, y): return min(1.0, ILD.get(str(pid), {}).get(str(y), 0) / max(SEAS.get(y, 186), 1))
def role(pid, y): h = max(0.08, 1 - ils(pid, y)); return min(4.6, pa(pid, y) / (162 * h))
def vl(pid, y):
    z = SPL.get(pid, {}).get(y, {}); a, b = z.get("vl", (0, 0))[0], z.get("vr", (0, 0))[0]
    if a + b < 100: return None
    return a / (a + b) - LGV[y].get(BAT.get(str(pid), "R"), 0.27)
def gap(pid, y):
    z = SPL.get(pid, {}).get(y, {}); (a, oa), (b, ob) = z.get("vl", (0, 0)), z.get("vr", (0, 0))
    if a < 40 or b < 40: return None
    g = ob - oa
    if BAT.get(str(pid)) == "S": g = abs(g)
    return g * (a / (a + 150))   # regressed toward no split by vs-LHP sample
W3 = (5, 3, 2); K = 1800.0
def rate600(pid, T):
    num = den = 0.0
    for y, w in zip((T-1, T-2, T-3), W3):
        p_ = pa(pid, y)
        if p_ > 0: num += w * WAR.get(pid, {}).get(y, 0.0) * SC(y); den += w * p_
    return (num + K * POP[T-1]["bat"]) / (den + K) * 600
def shipped(pid, T):
    """desk_data playing time as shipped Nov 9 (on 2020-scaled PA)."""
    age = T - AGES[pid]; ys = [y for y in (T-1, T-2, T-3) if not (y not in PT[pid] and y < min(PT[pid]))]
    pts = [pa(pid, y) for y in ys]; ws = [W3[(T-1) - y] for y in ys]
    ptw = sum(w * p_ for w, p_ in zip(ws, pts)); ptd = sum(ws)
    if not ptd: return 0.0
    top2 = sorted(pts, reverse=True)[:2]
    l = pa(pid, T-1); p2 = max(pa(pid, T-2), pa(pid, T-3)); inj = l < 340 and p2 >= 544
    a = 0.6 if age - 1 <= 26 else 0.4 if inj else 0.2
    pe = min(a * sum(top2) / len(top2) + (1 - a) * ptw / ptd, 680)
    if age - 1 <= 26 and l >= 408: pe = min(max(pe, 0.85 * l), 680)
    if age - 1 >= 26:
        pe0 = pe; pe = 0.85 * pe + 52.5
        if pe0 >= 300: pe *= max(0.7, min(1.0, 1 + 0.12 * (rate600(pid, T) - 3.5)))
        if l >= 510: pe = min(680, max(pe, 0.75 * l))
    return pe
ROWS = []
for T in list(range(2016, 2020)) + list(range(2021, 2028)):
    for pid in PT:
        if pid not in AGES or ((T-1) not in PT[pid] and (T-2) not in PT[pid]): continue
        if max(ptv(pid, T-1, "bat"), 0.5 * ptv(pid, T-2, "bat")) < 150 or ptv(pid, T-1, "pit") * 3 > ptv(pid, T-1, "bat"): continue
        age = T - AGES[pid]
        if age > 37: continue
        f = dict(T=T, pid=pid, age=age, act=(pa(pid, T) if T <= 2026 else None), y=(WAR.get(pid, {}).get(T, 0.0) if T <= 2026 else None))
        f["A"] = shipped(pid, T); f["r600"] = rate600(pid, T)
        for k, y in (("1", T-1), ("2", T-2), ("3", T-3)):
            f["pa" + k] = pa(pid, y); f["il" + k] = ils(pid, y); f["ro" + k] = role(pid, y) if pa(pid, y) > 0 else 0.0
            f["g" + k] = G.get(pid, {}).get(y, 0) * SC(y)
        v1 = vl(pid, T-1); v2 = vl(pid, T-2)
        f["vl1"] = v1 if v1 is not None else 0.0; f["dvl"] = (v1 - v2) if (v1 is not None and v2 is not None) else 0.0
        gs = [g for g in (gap(pid, T-1), gap(pid, T-2), gap(pid, T-3)) if g is not None]
        f["gap"] = st.mean(gs) if gs else 0.0
        f["ilsum"] = f["il1"] * 5 + f["il2"] * 3 + f["il3"] * 2
        f["gpost"], f["pagd"] = postf(pid, T-1)
        ROWS.append(f)
TR = [r for r in ROWS if r["T"] <= 2026]
print("rows", len(TR), "| 2027 rows", len(ROWS) - len(TR))
# ---------- B: structural ----------
def B(r, kh=1.0, wr=(6, 3, 1), a_h=0.5):
    # availability: weighted IL share regressed toward the population (0.07 for this group)
    ih = (r["il1"] * 5 + r["il2"] * 3 + r["il3"] * 2) / 10
    eh = 1 - (a_h * ih + (1 - a_h) * 0.07) - 0.004 * max(0, r["age"] - 30)
    # role: PA per healthy game, recent-heavy, only seasons he played
    xs = [(r["ro" + k], w) for k, w in zip("123", wr) if r["pa" + k] > 0]
    er = sum(a * w for a, w in xs) / sum(w for _, w in xs) if xs else 0
    return min(700, 162 * eh * er * kh)
# ---------- features for C / D ----------
FE = ["A", "pa1", "pa2", "pa3", "il1", "il2", "il3", "ro1", "ro2", "ro3", "g1", "r600", "age", "age30", "vl1", "dvl", "gap", "ilsum", "ro1xage", "gpost", "pagd"]
import os
DROP = set(os.environ.get("DROP", "").split(",")) - {""}
FE = [k for k in FE if k not in DROP]
# production (Nov 9): the injured-list, platoon and second-half terms add nothing out of sample
# once PA, games and PA per healthy game are in (ablations: 158.6 with them, 157.4 without),
# so the shipped fit leaves them out. FULL=1 restores them for the comparison.
if not os.environ.get("FULL") and not DROP:
    FE = [k for k in FE if k not in ("il1", "il2", "il3", "ilsum", "vl1", "dvl", "gap", "gpost", "pagd")]
def X(r):
    z = dict(r); z["age30"] = max(0, r["age"] - 30); z["ro1xage"] = r["ro1"] * max(0, r["age"] - 27)
    return [z[k] for k in FE]
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
predC, predD = {}, {}
for T in [t for t in range(2016, 2027) if t != 2020]:
    tr = [r for r in TR if r["T"] < T]; te = [r for r in TR if r["T"] == T]
    if len(tr) < 400:
        for r in te: predC[(T, r["pid"])] = r["A"]; predD[(T, r["pid"])] = r["A"]
        continue
    sc = StandardScaler().fit([X(r) for r in tr])
    m = Ridge(alpha=5.0).fit(sc.transform([X(r) for r in tr]), [r["act"] for r in tr])
    g = None if not os.environ.get("GBM") else GradientBoostingRegressor(n_estimators=250, max_depth=3, learning_rate=0.04, subsample=0.8, random_state=1).fit([X(r) for r in tr], [r["act"] for r in tr]) if os.environ.get("GBM") else None
    pc = m.predict(sc.transform([X(r) for r in te])); pd_ = g.predict([X(r) for r in te]) if g else pc
    for r, a, b in zip(te, pc, pd_): predC[(T, r["pid"])] = float(min(700, max(0, a))); predD[(T, r["pid"])] = float(min(700, max(0, b)))
EVAL = [r for r in TR if r["T"] >= 2018]   # first two years train only
def ag(r, p_): return CUR["bat"].get(str(min(max(r["age"], 20), 41)), -0.3) * p_ / 680
def score(fn, rs):
    ep = [fn(r) - r["act"] for r in rs]; ew = [r["r600"] / 600 * fn(r) + ag(r, fn(r)) - r["y"] for r in rs]
    return "PT rmse %5.1f bias %+6.1f | WAR rmse %.4f bias %+.3f" % (st.mean(x * x for x in ep) ** 0.5, st.mean(ep), st.mean(x * x for x in ew) ** 0.5, st.mean(ew))
MODELS = [("A shipped", lambda r: r["A"]), ("B structural", lambda r: B(r)), ("C ridge", lambda r: predC[(r["T"], r["pid"])])] + ([("D boosted", lambda r: predD[(r["T"], r["pid"])])] if os.environ.get("GBM") else [])
GROUPS = [("all", lambda r: True), ("played 100+ in T", lambda r: r["act"] >= 100),
          ("injury year (IL 25%+ last)", lambda r: r["il1"] >= 0.25), ("IL-prone (2+ of 3 yrs 15%+)", lambda r: sum(r["il" + k] >= 0.15 for k in "123") >= 2),
          ("role drop (PA/healthy game down 0.4+)", lambda r: r["pa2"] > 0 and r["ro1"] - r["ro2"] <= -0.4),
          ("vs-LHP share down 4+ pts", lambda r: r["dvl"] <= -0.04), ("big platoon gap (.150+)", lambda r: r["gap"] >= 0.15),
          ("age <=26", lambda r: r["age"] <= 26), ("age 27-30", lambda r: 27 <= r["age"] <= 30), ("age 31+", lambda r: r["age"] >= 31)]
for gname, keep in GROUPS:
    v = [r for r in EVAL if keep(r)]
    print("\n-- %s (n %d)" % (gname, len(v)))
    for nm, fn in MODELS: print("   %-13s %s" % (nm, score(fn, v)))
json.dump(dict(fe=FE), open("/work/pt_model.json", "w"))
import pickle; pickle.dump(ROWS, open("/work/pt_rows.pkl", "wb"))

# ---------- final fit on 2016-2026 targets, 2027 predictions ----------
sc = StandardScaler().fit([X(r) for r in TR]); m = Ridge(alpha=5.0).fit(sc.transform([X(r) for r in TR]), [r["act"] for r in TR])
print("\nridge, standardized coefficients (PA per 1 sd):", {k: round(float(c), 1) for k, c in sorted(zip(FE, m.coef_), key=lambda t: -abs(t[1]))}, "intercept", round(float(m.intercept_), 1))
P27 = {}
for r in ROWS:
    if r["T"] != 2027: continue
    P27[str(r["pid"])] = round(float(min(700, max(0, m.predict(sc.transform([X(r)]))[0]))))
if not DROP and not os.environ.get("FULL"):
    json.dump(dict(fe=FE, mean=[float(x) for x in sc.mean_], scale=[float(x) for x in sc.scale_], coef=[float(x) for x in m.coef_], intercept=float(m.intercept_), p27=P27), open("/work/pt_model.json", "w"))
NM = {r["pid"]: r for r in ROWS if r["T"] == 2027}
for pid, n in ((680776, "Duran"), (665833, "Cruz"), (641343, "Bauers"), (643396, "IKF"), (660670, "Acuna"), (676059, "Westburg"), (650489, "Castro"), (606192, "Teoscar"), (663656, "Tucker"), (666182, "Bichette"), (592450, "Judge"), (545361, "Trout"), (650402, "Gleyber"), (668930, "Turang")):
    r = NM.get(pid)
    if r: print("  %-9s A %3.0f -> ridge %3d | PA %s IL %s role %s vl1 %+.3f dvl %+.3f gap %.3f gpost %.2f pagd %+.2f" % (n, r["A"], P27[str(pid)], [round(r["pa" + k]) for k in "123"], [round(r["il" + k], 2) for k in "123"], [round(r["ro" + k], 2) for k in "123"], r["vl1"], r["dvl"], r["gap"], r["gpost"], r["pagd"]))
