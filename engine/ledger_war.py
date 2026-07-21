"""
Front Office Ledger, valuation module: LEDGER WAR v0
=====================================================
A transparent, self-computed value metric built entirely from the free MLB
Stats API, so the valuation stage of the pipeline has no licensing
dependency. FanGraphs-flavored by construction:

  BATTING  wOBA from counting stats (fixed generic weights, wOBA scale
           1.15) -> wRAA vs league; + positional adjustment (per 600 PA:
           C +12.5, SS +7.5, 2B/3B/CF +2.5, LF/RF -7.5, 1B -12.5, DH -17.5);
           + replacement offset (+20 runs / 600 PA); / runs-per-win.
  PITCHING FIP (13HR + 3(BB+HBP) - 2K)/IP + yearly cFIP so lgFIP = lgRA-ish;
           WAR = ((lgFIP - FIP) / RPW) x IP/9 + 0.105 x IP/9 replacement.
  RPW      1.5 x league runs/game + 3.

KNOWN v0 GAPS (documented, not hidden): no fielding runs, no baserunning,
no park factors, no league (AL/NW) adjustment, one primary position per
season, flat reliever replacement. Expect LVM to run ~0.5-1.5 wins under
full WAR for elite defenders/baserunners and to be FIP-flavored for
pitchers. Validation against public anchors below; tolerance is fine for
channel grades (which sum many decisions), not for single-player debates.

League constants are computed per season from the same feed (team totals),
so the metric is internally consistent by construction.
"""
import json, time, urllib.request

UA = {"User-Agent": "FrontOfficeLedger-POC/0.1"}
API = "https://statsapi.mlb.com/api/v1"
W = dict(bb=0.69, hbp=0.72, x1b=0.89, x2b=1.27, x3b=1.61, hr=2.10)
WOBA_SCALE = 1.15
POS_ADJ = {"C": 12.5, "SS": 7.5, "2B": 2.5, "3B": 2.5, "CF": 2.5,
           "LF": -7.5, "RF": -7.5, "OF": -2.5, "1B": -12.5, "DH": -17.5, "P": 0.0}

def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            if i == retries - 1: raise
            time.sleep(2)

def _woba_num(st):
    bb = st.get("baseOnBalls", 0) - st.get("intentionalWalks", 0)
    h = st.get("hits", 0); d = st.get("doubles", 0); t = st.get("triples", 0); hr = st.get("homeRuns", 0)
    x1b = h - d - t - hr
    return (W["bb"] * bb + W["hbp"] * st.get("hitByPitch", 0) + W["x1b"] * x1b
            + W["x2b"] * d + W["x3b"] * t + W["hr"] * hr)

def _woba_den(st):
    return (st.get("atBats", 0) + st.get("baseOnBalls", 0) - st.get("intentionalWalks", 0)
            + st.get("sacFlies", 0) + st.get("hitByPitch", 0))

_constants = {}
def constants(year):
    if year in _constants: return _constants[year]
    hit = get(f"{API}/teams/stats?season={year}&group=hitting&stats=season&sportId=1")["stats"][0]["splits"]
    pit = get(f"{API}/teams/stats?season={year}&group=pitching&stats=season&sportId=1")["stats"][0]["splits"]
    tot = {}
    for s in hit:
        for k, v in s["stat"].items():
            if isinstance(v, int): tot[k] = tot.get(k, 0) + v
    lg_woba = _woba_num(tot) / _woba_den(tot)
    games = tot.get("gamesPlayed", 2430); runs = tot.get("runs", 0)
    rpg = runs / games
    rpw = 1.5 * rpg + 3
    ip = hr = bbp = k = r = 0.0
    for s in pit:
        st = s["stat"]
        ip += float(st.get("inningsPitched", 0)); hr += st.get("homeRuns", 0)
        bbp += st.get("baseOnBalls", 0) + st.get("hitByPitch", 0); k += st.get("strikeOuts", 0)
        r += st.get("runs", 0)
    raw_fip = (13 * hr + 3 * bbp - 2 * k) / ip
    lg_ra9 = 9 * r / ip
    cfip = lg_ra9 - raw_fip          # anchor FIP scale to league RA9
    _constants[year] = dict(lg_woba=lg_woba, rpw=rpw, cfip=cfip, lg_fip=lg_ra9)
    return _constants[year]

def lvm_batting(st, year, pos):
    c = constants(year)
    pa = st.get("plateAppearances", 0)
    den = _woba_den(st)
    if not pa or not den: return 0.0
    woba = _woba_num(st) / den
    wraa = (woba - c["lg_woba"]) / WOBA_SCALE * pa
    adj = (POS_ADJ.get(pos, 0.0) + 20.0) * pa / 600.0
    return (wraa + adj) / c["rpw"]

def lvm_pitching(st, year):
    c = constants(year)
    ip = float(st.get("inningsPitched", 0) or 0)
    if not ip: return 0.0
    fip = (13 * st.get("homeRuns", 0) + 3 * (st.get("baseOnBalls", 0) + st.get("hitByPitch", 0))
           - 2 * st.get("strikeOuts", 0)) / ip + c["cfip"]
    return ((c["lg_fip"] - fip) / c["rpw"]) * ip / 9 + 0.105 * ip / 9

def player_seasons(person_ids):
    """{mlbam: {'name','pos', seasons: {year: {'bat':war,'pit':war,'pa','ip','team'}}}}"""
    out = {}
    for i in range(0, len(person_ids), 40):
        chunk = ",".join(str(x) for x in person_ids[i:i + 40])
        d = get(f"{API}/people?personIds={chunk}&hydrate=stats(group=[hitting,pitching],type=[yearByYear])")
        for p in d.get("people", []):
            pos = p["primaryPosition"]["abbreviation"]
            rec = out[p["id"]] = dict(name=p["fullName"], pos=pos, seasons={})
            for grp in p.get("stats", []):
                g = grp["group"]["displayName"]
                for sp in grp.get("splits", []):
                    if sp.get("team") is None and sp.get("league") is None: continue
                    yr = int(sp["season"]); st = sp["stat"]
                    if sp.get("team") and len([x for x in grp["splits"] if int(x["season"]) == yr]) > 1 and not sp.get("team"):
                        continue
                    row = rec["seasons"].setdefault(yr, dict(bat=0.0, pit=0.0, pa=0, ip=0.0, team=""))
                    tm = (sp.get("team") or {}).get("name", "")
                    if tm: row["team"] = tm if not row["team"] else row["team"] + "/" + tm if tm not in row["team"] else row["team"]
                    if g == "hitting" and st.get("plateAppearances"):
                        # aggregate multi-stint rows by recomputing on summed stats is complex; sum WAR per stint instead
                        row["bat"] += lvm_batting(st, yr, pos); row["pa"] += st.get("plateAppearances", 0)
                    if g == "pitching" and st.get("inningsPitched"):
                        row["pit"] += lvm_pitching(st, yr); row["ip"] += float(st.get("inningsPitched", 0))
    return out

if __name__ == "__main__":
    # ---- validation anchors (public figures, FG-flavored where possible) ----
    ANCHORS = [
        (592450, "Aaron Judge", 2024, "fWAR ~11.2"),
        (683002, "Gunnar Henderson", 2024, "fWAR ~7.8 / bWAR 9.1"),
        (605141, "Mookie Betts", 2020, "fWAR ~3.1 / bWAR 3.7"),
        (668939, "Adley Rutschman", 2023, "fWAR ~4.3"),
        (669203, "Corbin Burnes", 2024, "fWAR ~2.9 / bWAR 4.4 (FIP vs RA9 gap)"),
        (660271, "Shohei Ohtani", 2024, "fWAR ~9.1 (bat only ~9)"),
        (687401, "Joey Ortiz", 2024, "fWAR ~2.7 / bWAR 2.9"),
        (663697, "William Contreras", 2024, "fWAR ~5.4"),
    ]
    ids = list({a[0] for a in ANCHORS})
    data = player_seasons(ids)
    print(f"{'player':<20}{'yr':>6}{'LVM':>7}   published anchor")
    print("-" * 62)
    for pid, name, yr, anchor in ANCHORS:
        rec = data.get(pid)
        if not rec or yr not in rec["seasons"]:
            print(f"{name:<20}{yr:>6}{'n/a':>7}   {anchor}"); continue
        s = rec["seasons"][yr]
        print(f"{name:<20}{yr:>6}{s['bat'] + s['pit']:>7.1f}   {anchor}")
