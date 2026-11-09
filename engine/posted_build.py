"""Posted NPB/KBO players (v5.2): a translated line from the real record of
every comparable import since 2017-18.

No projection system the Ledger trusts translates foreign-league stats, so the
Ledger does it the only way it can defend in public: by the nearest real
precedents. For each posted player and each of his last three seasons, find
the five comparable imports (same role, nearest age and production, a penalty
for the other league) and read what they ACTUALLY produced per season over
their first two MLB seasons on the Ledger's own WAR scale (first season only
when that is all there is). That comp-weighted figure stands in for the
season's MLB-equivalent value, so the standard projection (5/4/3 weights, 15%
regression, aging curve) runs on him exactly as on everyone else.

Comps: non-returning imports on guaranteed MLB deals (posted_research.json,
contract terms from contemporaneous reporting; Ohtani excluded as a two-way
outlier). Writes posted.json.
"""
import json, math

ROOT = "/work"
R = json.load(open(f"{ROOT}/posted_research.json"))
LVM = {int(k): v for k, v in json.load(open(f"{ROOT}/lvm_cache.json")).items() if not k.startswith("__")}

def ipf(x):
    i = int(x); return i + round((x - i) * 10) / 3

def season_wars(pid):
    rec = LVM.get(int(pid)) if pid else None
    by = {}
    for y, t, v in (rec["rows"] if rec else []):
        by[y] = by.get(y, 0) + v
    return [round(by[y], 1) for y in sorted(by)]

# Nov 9: hitters are matched on lines relative to their own league's season, not raw.
# The KBO plays a much higher-offense game than NPB (2024: .352 OBP / .420 SLG against
# .305 / .346), so raw matching paired a good KBO line with NPB stars and their MLB
# results (Si Hwan Roh had come out within 0.3 WAR of Teruaki Sato, an NPB Triple
# Crown winner). League averages (both NPB leagues combined; KBO), season by season;
# 2026 uses 2025.
LG = {"NPB": {2016: (.318, .375, .021), 2017: (.317, .375, .021), 2018: (.323, .390, .024), 2019: (.320, .383, .023), 2020: (.321, .381, .023),
              2021: (.316, .369, .021), 2022: (.309, .354, .019), 2023: (.310, .356, .019), 2024: (.305, .346, .017), 2025: (.307, .352, .018)},
      "KBO": {2016: (.365, .437, .023), 2017: (.358, .437, .025), 2018: (.356, .450, .029), 2019: (.337, .385, .016), 2020: (.348, .409, .021),
              2021: (.342, .383, .018), 2022: (.330, .369, .016), 2023: (.335, .372, .015), 2024: (.352, .420, .022), 2025: (.339, .391, .019)}}
def lgavg(lg, yr):
    t = LG.get(lg) or LG["NPB"]; yr = min(max(int(yr), 2016), 2025); return t[yr]
def feat_hit(line, age, lg, yr=2025):
    if not line or line.get("PA", 0) < 150: return None
    iso = line["SLG"] - line["AVG"]
    lo, ls, lh = lgavg(lg, yr)
    return dict(kind="H", obp=line["OBP"] - lo, slg=line["SLG"] - ls, iso=iso, hrpa=line["HR"] / line["PA"] - lh, age=age, lg=lg)

def feat_pit(line, age, lg):
    if not line or ipf(line.get("IP", 0)) < 30: return None
    ip = ipf(line["IP"]); bf = ip * 4.2
    gs = line.get("GS") or 0; g = line.get("G") or 1
    return dict(kind="P", kbb=(line["K"] - line["BB"]) / bf * 100, era=line["ERA"], hr9=line["HR"] * 9 / ip,
                sp=1 if gs / g >= 0.5 else 0, age=age, lg=lg)

def dist(a, b):
    lg = 0 if a["lg"] == b["lg"] else 0.8
    if a["kind"] == "H":
        return (abs(a["obp"] - b["obp"]) / 0.03 + abs(a["slg"] - b["slg"]) / 0.05 + abs(a["hrpa"] - b["hrpa"]) / 0.02
                + abs(a["age"] - b["age"]) / 3 + lg)
    return (abs(a["kbb"] - b["kbb"]) / 3.0 + abs(a["era"] - b["era"]) / 0.8 + abs(a["age"] - b["age"]) / 3
            + (0 if a["sp"] == b["sp"] else 1.5) + lg)

comps = []
for c in R["comps"]:
    if c.get("returning_import") or c.get("minor_league_deal") or not c.get("years"): continue
    if c["name"] == "Shohei Ohtani": continue
    w = season_wars(c.get("mlbam_id"))
    if not w: continue
    fl = c["final_season_line"]
    h, p = fl.get("hitting"), fl.get("pitching")
    f = feat_pit(p, c["age_at_signing"], c["prior_league"]) if "P" in c["role"].split("/")[0][:2] or (p and not h) else feat_hit(h, c["age_at_signing"], c["prior_league"], c.get("final_pre_mlb_season") or int(str(c["offseason"])[:4]))
    if not f: continue
    comps.append(dict(name=c["name"], off=c["offseason"], yrs=c["years"], tot=c["guaranteed_musd"], club=c["signing_club"],
                      lg=c["prior_league"], age=c["age_at_signing"], y1=w[0], y2=(w[1] if len(w) > 1 else None),
                      v=(w[0] + w[1]) / 2 if len(w) > 1 else w[0], f=f))   # first two MLB seasons, averaged
print("usable comps:", len(comps), "| hitters", sum(1 for c in comps if c["f"]["kind"] == "H"), "pitchers", sum(1 for c in comps if c["f"]["kind"] == "P"))

# Nov 3: a second translation, from the money. Across the same imports, what
# each was paid (AAV, drifted 5% a winter to today's market) against what he
# went on to produce: v = a + b x AAV, hitters and pitchers apart. The page
# blends it with the stat translation for a posted player whose price the
# published projections give (DESK.cons): the stat comps are thin (10 hitters,
# 15 pitchers) and the market's price carries scouting the box score lacks.
import statistics as _st
def _fit(xs, ys):
    mx, my = _st.mean(xs), _st.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return [round(my - b * mx, 3), round(b, 4)]
MT = {}
for _k in ("H", "P"):
    _pool = [c for c in comps if c["f"]["kind"] == _k]
    MT[_k] = _fit([c["tot"] / c["yrs"] * (1.05 ** (2026 - int(c["off"][:4]))) for c in _pool], [c["v"] for c in _pool])
print("money translation (v = a + b x AAV):", MT)
# Nov 9: a comps average cannot reach past its best comp, and with ten hitter comps one
# glove-first outlier (Ha-Seong Kim) carried any line near his. Hitters' seasons are now
# half the comps average and half a line fit on the same comps: MLB value against the
# league-relative line (2 x OBP over league + SLG over league), which extends to lines
# better than any comp's and does not hand a bat a shortstop's defense.
import numpy as _np
_H = [c for c in comps if c["f"]["kind"] == "H"]
_X = _np.array([[2 * c["f"]["obp"] + c["f"]["slg"], 1.0] for c in _H]); _Y = _np.array([c["v"] for c in _H])
HFIT = [float(x) for x in _np.linalg.lstsq(_X, _Y, rcond=None)[0]]
print("hitter line fit (v = a x (2 OBP+ + SLG+) + b):", [round(x, 2) for x in HFIT], "on", len(_H), "comps")
out = {}
for pz in R["posted"]:
    if pz.get("status") != "posted" or not pz.get("mlbam_id"): continue
    pit = pz["primary_position"] in ("SP", "RP", "P")
    age26 = 2026 - int(pz["birth_date"][:4]) - (1 if pz["birth_date"][5:10] > "06-30" else 0)   # season age (June 30)
    per_season = {}
    feats = {}
    for yr in ("2024", "2025", "2026"):
        line = pz["stats"].get(yr)
        f = feat_pit(line, age26 + 1 - (2026 - int(yr)), pz["league"]) if pit else feat_hit(line, age26 + 1 - (2026 - int(yr)), pz["league"], int(yr))
        if not f: continue
        pool = [c for c in comps if c["f"]["kind"] == f["kind"]]
        ranked = sorted(pool, key=lambda c: dist(f, c["f"]))[:5]
        wts = [1 / (1 + dist(f, c["f"])) for c in ranked]
        cv = sum(c["v"] * w for c, w in zip(ranked, wts)) / sum(wts)
        if not pit: cv = 0.5 * cv + 0.5 * (HFIT[0] * (2 * f["obp"] + f["slg"]) + HFIT[1])
        per_season[yr] = round(cv, 2)
        feats[yr] = f
    # market comps: the two-season platform, as the contract book reads it
    # (a 2025 match counts with a half-point penalty)
    pool = [c for c in comps if c["f"]["kind"] == ("P" if pit else "H")]
    def dmin(c):
        ds = [dist(feats["2026"], c["f"])] if "2026" in feats else []
        if "2025" in feats: ds.append(dist(feats["2025"], c["f"]) + 0.5)
        return min(ds)
    used = [(c, round(dmin(c), 2)) for c in sorted(pool, key=dmin)[:5]]
    s26 = pz["stats"]["2026"]
    if pit:
        line = f'{s26["IP"]} IP, {s26["ERA"]:.2f} ERA, {s26["K"]} K, {s26["BB"]} BB, {s26["HR"]} HR' + (f', {s26["GS"]} starts' if s26.get("GS") else '')
    else:
        line = f'{s26["AVG"]:.3f}/{s26["OBP"]:.3f}/{s26["SLG"]:.3f}, {s26["HR"]} HR in {s26["PA"]} PA'.replace("0.", ".")
    out[str(pz["mlbam_id"])] = dict(
        name=pz["name"], club=pz["team"], league=pz["league"], pos=pz["primary_position"], pit=1 if pit else 0,
        age=age26, line26=line, awards=pz.get("awards", [])[:3], deadline=pz.get("signing_deadline"),
        translated=per_season,
        mt=MT["P" if pit else "H"],
        comps=[[c["name"], c["off"], c["yrs"], c["tot"], c["club"], c["y1"], c["y2"], d] for c, d in used],
        public=[[x.get("outlet"), x.get("years"), x.get("total_musd")] for x in (pz.get("projections") or [])
                if x.get("years") and x.get("total_musd") and "secondary" not in (x.get("outlet") or "")],
    )
    print(pz["name"], age26, per_season, [(c["name"], c["y1"], d) for c, d in used])
json.dump(out, open(f"{ROOT}/posted.json", "w"), indent=1, ensure_ascii=False)
