"""Nov 3: do Statcast skill signals add to the free-agent projection?
Baseline = the page's projection for a season (Ledger WAR over the last
three seasons weighted 5/4/3, 15% regressed to the role's population mean,
plus the age-curve step). Target = the next season's Ledger WAR. Fit the
residual on: pitchers, fastball velocity and its change; hitters, xwOBA minus
wOBA (contact quality the results did not show) and sprint speed and its
change. Train on 2017-2022 seasons, test on 2023-2025."""
import csv, json, glob, statistics as st
from collections import defaultdict
H = "/work/savant_hist"
D = json.load(open("/work/desk_data.json"))
CUR = D["curves"]; POP = CUR.get("pop", 0.6)
LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
BY = {int(k): v for k, v in json.load(open("/work/ages.json")).items()}
def war(pid):
    d = defaultdict(float)
    for y, t, v in LVM.get(pid, {}).get("rows", []): d[y] += v
    return d
def rd(path):
    try: return list(csv.DictReader(open(path, encoding="utf-8-sig")))
    except Exception: return []
def f(x):
    try: return float(x)
    except Exception: return None
VELO = defaultdict(dict); XW = defaultdict(dict); SPD = defaultdict(dict); XWP = defaultdict(dict)
for y in range(2016, 2027):
    for r in rd(f"{H}/velo_{y}.csv"):
        v = f(r.get("ff_avg_speed")) or f(r.get("si_avg_speed"))
        if v: VELO[int(r["pitcher"])][y] = v
    for r in rd(f"{H}/xb_{y}.csv"):
        if f(r.get("pa")) and f(r["pa"]) >= 150: XW[int(r["player_id"])][y] = (f(r["est_woba"]) - f(r["woba"]), f(r["pa"]))
    for r in rd(f"{H}/xp_{y}.csv"):
        if f(r.get("pa")) and f(r["pa"]) >= 150: XWP[int(r["player_id"])][y] = (f(r["woba"]) - f(r["est_woba"]), f(r["pa"]))
    for r in rd(f"{H}/spd_{y}.csv"):
        if f(r.get("sprint_speed")): SPD[int(r["player_id"])][y] = f(r["sprint_speed"])
def baseline(w, y, age, pit):
    obs = [(w.get(y, 0), 5), (w.get(y-1, 0), 4), (w.get(y-2, 0), 3)]
    obs = [(v, k) for v, k in obs if abs(v) > 0.05]
    if not obs: return None
    b = sum(v*k for v, k in obs) / sum(k for _, k in obs)
    b = 0.85*b + 0.15*POP
    c = CUR["pit" if pit else "bat"]
    return b + c.get(str(min(max(age + 1, 20), 41)), -0.3)
rows = {"P": [], "H": []}
for pid, vs in VELO.items():
    w = war(pid); b0 = BY.get(pid)
    if not b0: continue
    for y in range(2017, 2026):
        if y not in vs or y + 1 not in w and y + 1 > 2026: continue
        if (pid in XW and y in XW[pid]): continue          # two-way: skip
        base = baseline(w, y, y - b0, True)
        if base is None or y + 1 > 2026: continue
        dv = vs[y] - vs[y-1] if (y-1) in vs else 0.0
        xg = XWP[pid][y][0] if y in XWP.get(pid, {}) else 0.0
        rows["P"].append(dict(pid=pid, y=y, base=base, tgt=w.get(y+1, 0.0), velo=vs[y], dv=dv, xg=xg, age=y-b0))
for pid, xs in XW.items():
    w = war(pid); b0 = BY.get(pid)
    if not b0: continue
    for y in range(2017, 2026):
        if y not in xs: continue
        base = baseline(w, y, y - b0, False)
        if base is None: continue
        sp = SPD.get(pid, {})
        rows["H"].append(dict(pid=pid, y=y, base=base, tgt=w.get(y+1, 0.0), xg=xs[y][0], spd=sp.get(y), dspd=(sp[y] - sp[y-1]) if (y in sp and y-1 in sp) else 0.0, age=y-b0))
import numpy as np
out = {}
for k, feats in (("P", ["velo", "dv", "xg"]), ("H", ["xg", "spd", "dspd"])):
    R = [r for r in rows[k] if all(r.get(x) is not None for x in feats)]
    mu = {x: st.mean(r[x] for r in R) for x in feats}
    def X(r): return [1.0] + [r[x] - mu[x] for x in feats]
    tr = [r for r in R if r["y"] <= 2022]; te = [r for r in R if r["y"] >= 2023]
    A = np.array([X(r) for r in tr]); yv = np.array([r["tgt"] - r["base"] for r in tr])
    coef, *_ = np.linalg.lstsq(A, yv, rcond=None)
    def mae(rs, use):
        return st.mean(abs(r["tgt"] - (r["base"] + (float(np.dot(coef, X(r))) - coef[0] if use else 0))) for r in rs)
    def rmse(rs, use):
        return (st.mean((r["tgt"] - (r["base"] + (float(np.dot(coef, X(r))) - coef[0] if use else 0)))**2 for r in rs))**0.5
    print(k, "n train", len(tr), "test", len(te), "| coef", dict(zip(["int"] + feats, [round(c, 3) for c in coef])), "| means", {x: round(v, 3) for x, v in mu.items()})
    print("   test MAE base", round(mae(te, False), 3), "skills", round(mae(te, True), 3), "| RMSE base", round(rmse(te, False), 3), "skills", round(rmse(te, True), 3))
    out[k] = dict(coef=[round(float(c), 4) for c in coef[1:]], feats=feats, mu={x: round(v, 4) for x, v in mu.items()},
                  test=dict(n=len(te), mae_base=round(mae(te, False), 3), mae_skills=round(mae(te, True), 3), rmse_base=round(rmse(te, False), 3), rmse_skills=round(rmse(te, True), 3)))
json.dump(out, open("/work/skills/skills_fit.json", "w"), indent=1)

# ---- apply to the 2026 season: one adjustment per player for the 2027 projection
ADJ = {}
for k, src in (("P", VELO), ("H", XW)):
    o = out[k]; feats = o["feats"]; mu = o["mu"]; cf = o["coef"]
    for pid in src:
        y = 2026
        if k == "P":
            vs = VELO[pid]
            if y not in vs: continue
            if pid in XW and y in XW[pid]: continue
            r = dict(velo=vs[y], dv=(vs[y] - vs[y-1]) if (y-1) in vs else 0.0, xg=XWP[pid][y][0] if y in XWP.get(pid, {}) else 0.0)
        else:
            if y not in XW[pid]: continue
            sp = SPD.get(pid, {})
            r = dict(xg=XW[pid][y][0], spd=sp.get(y, mu["spd"]), dspd=(sp[y] - sp[y-1]) if (y in sp and y-1 in sp) else 0.0)
        a = sum(c * (r[x] - mu[x]) for c, x in zip(cf, feats))
        ADJ[str(pid)] = [round(max(-0.8, min(0.8, a)), 2)] + [round(r[x], 3) for x in feats]
json.dump({"fit": out, "adj": ADJ}, open("/work/skill_adj.json", "w"))
nm = {p[1]: p[0] for p in D["players"]}
for n in ("Freddy Peralta", "Jack Flaherty", "Michael King", "Trevor Rogers", "Sonny Gray", "Kevin Gausman", "Randy Arozarena", "Seiya Suzuki", "Brandon Lowe", "Tarik Skubal"):
    pid = next((k for k, v in nm.items() if v == n), None)
    print(n, ADJ.get(str(pid)))
