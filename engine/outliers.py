"""Nov 9: hitters where our 2027 projection and Steamer/DC disagree most, and why.
Mirrors desk_data (rate x expected PT, 5/3/2, K 1800) + skill adj + one aging step,
then splits each gap into playing time vs rate, and attaches the 2026 evidence
(xwOBA vs wOBA, sprint, defense runs, Steamer Off/Def, recency)."""
import csv, json, statistics as st, sys
sys.path.insert(0, "/work")
import lvm15
D = json.load(open("/work/desk_data.json")); PC = json.load(open("/work/proj_curves.json"))
CUR = PC["curves"]["bat"]; SK = json.load(open("/work/skill_adj.json"))["adj"]
PT = json.load(open("/work/playtime.json"))
DEBUT = {}
for _y in range(2013, 2027):
    for _s in json.load(open(f"/work/pt_hist/hitting_{_y}.json"))["stats"][0]["splits"]:
        if _s["stat"].get("plateAppearances", 0) > 0: DEBUT.setdefault(_s["player"]["id"], _y)
def rd(f):
    o = {}
    for r in csv.DictReader(open("/work/proj_ext/" + f, encoding="utf-8-sig")):
        try: o[int(r["MLBAMID"])] = r
        except Exception: pass
    return o
SH, DH = rd("17aab87b-Steamer_H.csv"), rd("b7efdcef-DC_H.csv")
def sav(kind, y):
    o = {}
    for r in csv.DictReader(open(f"/work/savant_hist/{kind}_{y}.csv", encoding="utf-8-sig")):
        o[int(r["player_id"])] = r
    return o
XB = {y: sav("xb", y) for y in (2024, 2025, 2026)}; SPD = {y: sav("spd", y) for y in (2024, 2025, 2026)}
CAP = 680.0; W = {2026: 5, 2025: 3, 2024: 2}
def pt_exp_of(p):
    rec = PT.get(str(p[1]));
    if not rec: return None
    pts = []; ptw = ptd = 0.0; debut = DEBUT.get(p[1], 2026)
    for y in (2024, 2025, 2026):
        v = float((rec.get(str(y)) or [0])[0])
        if y < debut: pts.append(0.0); continue
        pts.append(v); ptw += W[y] * v; ptd += W[y]
    if ptd == 0: return None
    pts_used = [v for y, v in zip((2024, 2025, 2026), pts) if y >= debut]
    top2 = sorted(pts_used, reverse=True)[:2]
    l = pts[2]; p2 = max(pts[0], pts[1]); inj = l < 0.5 * CAP and p2 >= 0.8 * CAP
    a = 0.6 if p[4] <= 26 else 0.4 if inj else 0.2
    pe = min(a * (sum(top2) / len(top2)) + (1 - a) * (ptw / ptd), CAP)
    if p[4] <= 26 and l >= 0.6 * CAP: pe = min(max(pe, 0.85 * l), CAP)
    return pe, pts
rows = []
for p in D["players"]:
    if p[3] or len(p) <= 16 or p[16] is None or (len(p) > 17 and p[17] == 1): continue
    if (D.get("posted") or {}).get(str(p[1])): continue
    S = SH.get(p[1]);
    if not S or float(S["PA"]) < 250: continue
    z = pt_exp_of(p)
    if not z or z[0] <= 0: continue
    pe, pts = z
    sk = SK.get(str(p[1]), [0])[0]; sk = sk if abs(sk) >= 0.02 else 0
    age = p[4] + 1; ag = CUR.get(str(min(max(age, 20), 41)), -0.3)
    ours = max(0, p[16] + sk + ag)
    rate600 = p[16] / pe * 600; ours600 = ours / pe * 600
    spa = float(S["PA"]); swar = float(S["WAR"]); st600 = swar / spa * 600
    dcw = float(DH[p[1]]["WAR"]) if p[1] in DH else None
    # evidence
    def xg(y):
        r = XB[y].get(p[1]);
        return (float(r["woba"]), float(r["est_woba"])) if r and r["woba"] else (None, None)
    w26, x26 = xg(2026); w25, x25 = xg(2025)
    def spd(y):
        r = SPD[y].get(p[1]); return float(r["sprint_speed"]) if r and r["sprint_speed"] else None
    dfr = {y: round(lvm15.def_runs(p[1], y)[0], 1) for y in (2024, 2025, 2026)}
    l3 = p[5:8]; rec = (p[7] - st.mean(l3))
    rows.append(dict(n=p[0], pid=p[1], age=age, l3=l3, pts=[int(x) for x in pts], pe=round(pe), rate600=round(rate600, 2), sk=round(sk, 2), ag=round(ag, 2),
                     ours=round(ours, 2), ours600=round(ours600, 2), st=round(swar, 2), spa=round(spa), st600=round(st600, 2), dc=dcw,
                     soff=round(float(S["Off"]), 1), sdef=round(float(S["Def"]), 1),
                     w26=w26, x26=x26, w25=w25, x25=x25, spd25=spd(2025), spd26=spd(2026), dfr=dfr, rec=round(rec, 2)))
print("hitters matched (Steamer PA >= 250):", len(rows))
for r in rows:
    r["gap"] = round(r["ours"] - r["st"], 2); r["gap600"] = round(r["ours600"] - r["st600"], 2)
    r["ptgap"] = round((r["pe"] - r["spa"]) * r["ours600"] / 600, 2)   # playing-time share of the gap at our rate
    r["dsum"] = round(sum(r["dfr"].values()), 1)
    r["xg26"] = round(r["w26"] - r["x26"], 3) if r["w26"] is not None else None
print("mean gap", round(st.mean(r["gap"] for r in rows), 3), "| mean rate gap /600", round(st.mean(r["gap600"] for r in rows), 3),
      "| mean PT share", round(st.mean(r["ptgap"] for r in rows), 3), "| sd rate gap", round(st.pstdev(r["gap600"] for r in rows), 3))
print("r(rate gap, L3 def runs)", round(st.correlation([r["gap600"] for r in rows], [r["dsum"] for r in rows]), 3))
print("r(rate gap, 2026 wOBA-xwOBA)", round(st.correlation([r["gap600"] for r in rows if r["xg26"] is not None], [r["xg26"] for r in rows if r["xg26"] is not None]), 3))
print("r(rate gap, age)", round(st.correlation([r["gap600"] for r in rows], [r["age"] for r in rows]), 3))
print("r(rate gap, recency = w26 - mean L3)", round(st.correlation([r["gap600"] for r in rows], [r["rec"] for r in rows]), 3))
print("r(rate gap, Steamer Def)", round(st.correlation([r["gap600"] for r in rows], [r["sdef"] for r in rows]), 3))
def show(r):
    print("  %-22s %2d  L3 %-18s PT %-16s pe %3d | ours %5.2f (%.2f/600, sk %+.2f ag %+.2f) | St %5.2f in %3d PA (%.2f/600) DC %s | gap %+.2f (/600 %+.2f, PT part %+.2f) | def %s (sum %+.1f) StDef %+.1f | wOBA/x 26 %s/%s 25 %s/%s | spd %s->%s" % (
        r["n"], r["age"], r["l3"], r["pts"], r["pe"], r["ours"], r["ours600"], r["sk"], r["ag"], r["st"], r["spa"], r["st600"], r["dc"], r["gap"], r["gap600"], r["ptgap"],
        list(r["dfr"].values()), r["dsum"], r["sdef"], r["w26"], r["x26"], r["w25"], r["x25"], r["spd25"], r["spd26"]))
rows.sort(key=lambda r: -r["gap600"])
print("\nWE ARE HIGHER (per 600 PA):"); [show(r) for r in rows[:22]]
print("\nWE ARE LOWER (per 600 PA):"); [show(r) for r in rows[-22:]]
json.dump(rows, open("/work/outliers.json", "w"))
