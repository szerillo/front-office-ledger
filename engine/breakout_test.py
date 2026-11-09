"""Nov 9: do breakouts and collapses carry forward more than the 5/3/2
projection assumes? Signal: the change in contact quality (xwOBA for
hitters, xwOBA allowed for pitchers) from the prior season, and its level.
Target: next-season Ledger WAR minus the 5/3/2 baseline. Train 2017-22,
test 2023-25."""
import csv, json, statistics as st, sys
sys.path.insert(0, "/work/skills"); sys.argv = ["x"]
src = open("/work/skills/skills_fit.py").read().split("import numpy as np")[0]
src = src.replace("baseline(w, y, y - b0, True)", "baseline(w, y, y - b0, True)").replace("(w.get(y, 0), 5), (w.get(y-1, 0), 4), (w.get(y-2, 0), 3)", "(w.get(y, 0), 5), (w.get(y-1, 0), 3), (w.get(y-2, 0), 2)")
exec(src)
import numpy as np
XWL = {}
for y in range(2016, 2027):
    for r in rd(f"{H}/xb_{y}.csv"):
        if f(r.get("pa")) and f(r["pa"]) >= 150: XWL.setdefault(int(r["player_id"]), {})[y] = f(r["est_woba"])
XPL = {}
for y in range(2016, 2027):
    for r in rd(f"{H}/xp_{y}.csv"):
        if f(r.get("pa")) and f(r["pa"]) >= 150: XPL.setdefault(int(r["player_id"]), {})[y] = f(r["est_woba"])
def run(k, rowsk, extra):
    R = [r for r in rowsk if all(r.get(x) is not None for x in extra)]
    tr = [r for r in R if r["y"] <= 2022]; te = [r for r in R if r["y"] >= 2023]
    mu = {x: st.mean(r[x] for r in tr) for x in extra}
    X = lambda r: [1.0] + [r[x] - mu[x] for x in extra]
    A = np.array([X(r) for r in tr]); yv = np.array([r["tgt"] - r["base"] for r in tr])
    c, *_ = np.linalg.lstsq(A, yv, rcond=None)
    rm = lambda use: (st.mean((r["tgt"] - r["base"] - ((float(np.dot(c, X(r))) - c[0]) if use else 0)) ** 2 for r in te)) ** 0.5
    print(k, extra, "n", len(te), "RMSE base", round(rm(False), 4), "with", round(rm(True), 4), "coef", [round(float(v), 3) for v in c[1:]])
for r in rows["H"]:
    xl = XWL.get(r["pid"], {}); r["xw"] = xl.get(r["y"]); r["dxw"] = (xl[r["y"]] - xl[r["y"]-1]) if (r["y"] in xl and r["y"]-1 in xl) else None
for r in rows["P"]:
    xl = XPL.get(r["pid"], {}); r["xw"] = xl.get(r["y"]); r["dxw"] = (xl[r["y"]] - xl[r["y"]-1]) if (r["y"] in xl and r["y"]-1 in xl) else None
for k in ("H", "P"):
    run(k, rows[k], ["xg"]); run(k, rows[k], ["xw"]); run(k, rows[k], ["dxw"]); run(k, rows[k], ["xw", "dxw", "xg"])
