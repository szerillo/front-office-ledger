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

def feat_hit(line, age, lg):
    if not line or line.get("PA", 0) < 150: return None
    iso = line["SLG"] - line["AVG"]
    return dict(kind="H", obp=line["OBP"], slg=line["SLG"], iso=iso, hrpa=line["HR"] / line["PA"], age=age, lg=lg)

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
    f = feat_pit(p, c["age_at_signing"], c["prior_league"]) if "P" in c["role"].split("/")[0][:2] or (p and not h) else feat_hit(h, c["age_at_signing"], c["prior_league"])
    if not f: continue
    comps.append(dict(name=c["name"], off=c["offseason"], yrs=c["years"], tot=c["guaranteed_musd"], club=c["signing_club"],
                      lg=c["prior_league"], age=c["age_at_signing"], y1=w[0], y2=(w[1] if len(w) > 1 else None),
                      v=(w[0] + w[1]) / 2 if len(w) > 1 else w[0], f=f))   # first two MLB seasons, averaged
print("usable comps:", len(comps), "| hitters", sum(1 for c in comps if c["f"]["kind"] == "H"), "pitchers", sum(1 for c in comps if c["f"]["kind"] == "P"))

out = {}
for pz in R["posted"]:
    if pz.get("status") != "posted" or not pz.get("mlbam_id"): continue
    pit = pz["primary_position"] in ("SP", "RP", "P")
    age26 = 2026 - int(pz["birth_date"][:4])
    per_season = {}
    feats = {}
    for yr in ("2024", "2025", "2026"):
        line = pz["stats"].get(yr)
        f = (feat_pit if pit else feat_hit)(line, age26 + 1 - (2026 - int(yr)), pz["league"])
        if not f: continue
        pool = [c for c in comps if c["f"]["kind"] == f["kind"]]
        ranked = sorted(pool, key=lambda c: dist(f, c["f"]))[:5]
        wts = [1 / (1 + dist(f, c["f"])) for c in ranked]
        per_season[yr] = round(sum(c["v"] * w for c, w in zip(ranked, wts)) / sum(wts), 2)
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
        comps=[[c["name"], c["off"], c["yrs"], c["tot"], c["club"], c["y1"], c["y2"], d] for c, d in used],
        public=[[x.get("outlet"), x.get("years"), x.get("total_musd")] for x in (pz.get("projections") or [])
                if x.get("years") and x.get("total_musd") and "secondary" not in (x.get("outlet") or "")],
    )
    print(pz["name"], age26, per_season, [(c["name"], c["y1"], d) for c, d in used])
json.dump(out, open(f"{ROOT}/posted.json", "w"), indent=1, ensure_ascii=False)
