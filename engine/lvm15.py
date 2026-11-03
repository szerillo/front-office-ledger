"""
LEDGER WAR v1.5: park factors.

Park factor pipeline (park_ingest.py -> parks.json): for each team-year
2004-2026, the home/away run-environment ratio (runs scored + allowed per
game, both sides of the ball), 3-yr centered rolling average, then halved
toward 1 to spread the home effect across a season played half on the road.
Mean 1.002 across 690 team-years; Coors lands ~1.15-1.19, Seattle/SD ~0.91-0.96.

Application (FanGraphs-style):
  BATTING  wRAA_adj = wRAA - (PF - 1) * lgR/PA * PA
           (hitters in hitter parks are docked the runs the park gave them)
  PITCHING FIP_adj = FIP / PF before comparison to league
           (pitchers in hitter parks get the credit back)
Seasons before 2004 and teams/years without a computed factor use PF = 1.

This module also exposes player_team_seasons_v15(ids): a park-adjusted,
defense-joined (v1.7: DRS infield, Statcast FRV catcher/outfield, see
def_runs; v1.6 SDI/Statcast join kept as fallback) fetcher used by the sweep and
the historical scorer so newly discovered players enter the cache at v1.5.
"""
import json
from ledger_war import get, API, constants, _woba_num, _woba_den, WOBA_SCALE, POS_ADJ

PARKS = json.load(open("/work/parks.json"))["byTeamId"]
SV = json.load(open("/work/savant_runs.json"))
SDI = json.load(open("/work/sdi_runs.json"))
# v1.7 defense sources (frv_ingest.py, drs_ingest.py); MLBAM-keyed
try: FRV = json.load(open("/work/frv_runs.json"))
except FileNotFoundError: FRV = {}
try: DRS = json.load(open("/work/drs_runs.json"))
except FileNotFoundError: DRS = {}

IF_POS, C_POS, OF_POS = ("3", "4", "5", "6"), ("2",), ("7", "8", "9")
POS_NUM = {"C": "2", "1B": "3", "2B": "4", "3B": "5", "SS": "6", "LF": "7", "CF": "8", "RF": "9"}
DRS_FROM, FRV_FROM, FRV_C_FULL = 2003, 2016, 2018

# League rates for centering each source at zero per position-season.
# Neither source sums to zero as published (DRS at C..RF: +154 runs in 2015,
# -95 in 2004; FRV -43..+28), so each player's runs at a position are taken
# relative to the league rate there: runs - (league runs / league innings) *
# his innings. A full-time regular moves by about 0-3 runs; ordering within a
# position-season is unchanged. DRS rates use every SIS fielder (resolved or
# not), FRV rates every Savant fielder.
DRS_RATE = {}
for _y, _ps in DRS.get("__league__", {}).items():
    for _p, _a in _ps.items():
        if _a["inn"] > 0:
            DRS_RATE[(_y, _p)] = (_a["drs"] / _a["inn"], _a["sz"] / _a["inn"])
FRV_RATE = {}
_fs = {}
for _pid, _r in FRV.items():
    if _pid.startswith("__"): continue
    for _y, _s in _r.items():
        for _p, _v in _s.get("pos", {}).items():
            a = _fs.setdefault((_y, _p), [0.0, 0.0]); a[0] += _v
        for _p, _o in _s.get("outs", {}).items():
            a = _fs.setdefault((_y, _p), [0.0, 0.0]); a[1] += _o
FRV_RATE = {k: v[0] / v[1] for k, v in _fs.items() if v[1] > 0}

def _drs_c(d, ys, p):
    """centered DRS at position p"""
    return d["pos"][p] - DRS_RATE.get((ys, p), (0.0, 0.0))[0] * d["inn"].get(p, 0.0)
def _drs_sz(d, ys):
    """centered DRS strike-zone (framing) runs, catchers, 2010+"""
    return d.get("sz", 0.0) - DRS_RATE.get((ys, "2"), (0.0, 0.0))[1] * d["inn"].get("2", 0.0)
def _frv_c(f, ys, p):
    """centered FRV at position p"""
    return f["pos"][p] - FRV_RATE.get((ys, p), 0.0) * f.get("outs", {}).get(p, 0.0)

def _ip(x):
    """MLB/SIS innings notation: 1393.2 = 1393 and 2/3."""
    try: x = float(x)
    except (TypeError, ValueError): return 0.0
    w = int(x); return w + round((x - w) * 10) / 3.0

def season_innings(fielding_splits):
    """{year: {"2".."9": innings}} from MLB Stats API fielding splits; the
    combined (no-team) row wins for traded players, as in season_posadj."""
    by, tot = {}, {}
    for sp in fielding_splits:
        pos = POS_NUM.get((sp.get("position") or {}).get("abbreviation"))
        if not pos: continue
        y = int(sp["season"]); inn = _ip(sp["stat"].get("innings"))
        if not sp.get("team"): tot[(y, pos)] = inn
        else: by[(y, pos)] = by.get((y, pos), 0.0) + inn
    by.update(tot)
    out = {}
    for (y, pos), inn in by.items():
        if inn > 0: out.setdefault(y, {})[pos] = inn
    return out

def old_def_runs(pid, y):
    """v1.6 defense (kept as the fallback): SDI where published, else Statcast
    OAA fielding runs prevented + Savant catcher framing."""
    ys = str(y)
    sdi = SDI.get(str(pid), {}).get(ys)
    sv = SV.get(str(pid), {}).get(ys, {})
    return sdi if sdi is not None else (sv.get("def", 0.0) + sv.get("frame", 0.0))

def def_runs(pid, y, inn=None):
    """LEDGER WAR v1.7 defense, runs vs position average, per player-season.
      1B/2B/3B/SS  DRS (SIS) at those positions, 2003+
      C            2018+ Statcast FRV catching runs (framing + throwing +
                   blocking). 2016-17: FRV publishes throwing only and Savant
                   publishes no framing run values before 2018, so FRV
                   throwing + DRS strike-zone (framing) runs; framing is
                   counted once. 2003-2015: DRS (includes framing from 2010).
      LF/CF/RF     2016+ Statcast FRV at those positions; 2003-2015 DRS
      pre-2003     v1.6 value (old_def_runs)
    Every source value is centered per position-season (see DRS_RATE).
    A group whose source has no record for the player-season falls back to the
    v1.6 value times that group's share of the player's fielding innings.
    Returns (runs, detail dict)."""
    old = old_def_runs(pid, y)
    if y < DRS_FROM: return old, {"src": "v16"}
    ys = str(y)
    d = DRS.get(str(pid), {}).get(ys)
    f = FRV.get(str(pid), {}).get(ys)
    # innings by position: MLB feed, else DRS, else FRV outs
    I = dict(inn or {})
    if not I and d: I = dict(d.get("inn", {}))
    if not I and f: I = {p: o / 3.0 for p, o in f.get("outs", {}).items()}
    tot_inn = sum(I.get(p, 0.0) for p in IF_POS + C_POS + OF_POS)
    if tot_inn <= 0:
        # no fielding innings anywhere (DH, pinch hitter, pitcher): keep v1.6
        return old, {"src": "v16", "old": old}
    det = {"src": [], "old": old}
    runs = 0.0
    def share(ps): return sum(I.get(p, 0.0) for p in ps) / tot_inn

    # infield: DRS
    if share(IF_POS) > 0:
        if d and any(p in d["pos"] for p in IF_POS):
            v = sum(_drs_c(d, ys, p) for p in IF_POS if p in d["pos"]); tag = "IF:DRS"
        else:
            v = old * share(IF_POS); tag = "IF:v16"
        runs += v; det["src"].append(tag); det["IF"] = v
    # catcher
    if share(C_POS) > 0:
        v = None
        if y >= FRV_FROM and f and "2" in f.get("pos", {}):
            v = _frv_c(f, ys, "2"); tag = "C:FRV"
            if y < FRV_C_FULL and "frame" not in f.get("c", {}):
                if d and "2" in d["pos"]:
                    v += _drs_sz(d, ys); tag = "C:FRV+DRSframing"
                else:
                    tag = "C:FRV(no framing)"
        elif y < FRV_FROM and d and "2" in d["pos"]:
            v = _drs_c(d, ys, "2"); tag = "C:DRS"
        if v is None:
            v = old * share(C_POS); tag = "C:v16"
        runs += v; det["src"].append(tag); det["C"] = v
    # outfield
    if share(OF_POS) > 0:
        v = None
        if y >= FRV_FROM:
            if f and any(p in f.get("pos", {}) for p in OF_POS):
                v = sum(_frv_c(f, ys, p) for p in OF_POS if p in f["pos"]); tag = "OF:FRV"
        elif d and any(p in d["pos"] for p in OF_POS):
            v = sum(_drs_c(d, ys, p) for p in OF_POS if p in d["pos"]); tag = "OF:DRS"
        if v is None:
            v = old * share(OF_POS); tag = "OF:v16"
        runs += v; det["src"].append(tag); det["OF"] = v
    return runs, det

_lg_rpa = {}
def lg_rpa(year):
    if year in _lg_rpa: return _lg_rpa[year]
    hit = get(f"{API}/teams/stats?season={year}&group=hitting&stats=season&sportId=1")["stats"][0]["splits"]
    runs = pa = 0
    for s in hit:
        runs += s["stat"].get("runs", 0); pa += s["stat"].get("plateAppearances", 0)
    _lg_rpa[year] = runs / max(1, pa)
    return _lg_rpa[year]

def pf(team_id, year):
    return PARKS.get(str(team_id), {}).get(str(year), 1.0)

def lvm_batting_pf(st, year, pos, p, posadj=None):
    c = constants(year)
    pa = st.get("plateAppearances", 0)
    den = _woba_den(st)
    if not pa or not den: return 0.0
    woba = _woba_num(st) / den
    wraa = (woba - c["lg_woba"]) / WOBA_SCALE * pa
    if p != 1.0:
        wraa -= (p - 1.0) * lg_rpa(year) * pa
    adj = ((POS_ADJ.get(pos, 0.0) if posadj is None else posadj) + 20.0) * pa / 600.0
    return (wraa + adj) / c["rpw"]

def season_posadj(fielding_splits):
    """v1.6: the positional adjustment a season actually earned, weighted by
    games at each position that season (DH included), instead of the
    player's CURRENT primary position applied to every season of his career
    (a second baseman who spent 2025 at first base was credited +2.5 runs
    per 600 PA instead of -12.5). {year: runs per 600 PA}"""
    by = {}
    tot_rows = {}
    for sp in fielding_splits:
        y = int(sp["season"]); pos = (sp.get("position") or {}).get("abbreviation")
        if not pos or pos == "P": continue
        g = sp["stat"].get("gamesPlayed", 0) or 0
        key = (y, pos)
        if not sp.get("team"): tot_rows[key] = g          # combined row for a traded player
        else: by[key] = by.get(key, 0) + g
    by.update(tot_rows)
    out = {}
    for (y, pos), g in by.items():
        if g <= 0 or pos not in POS_ADJ: continue
        a = out.setdefault(y, [0.0, 0])
        a[0] += POS_ADJ[pos] * g; a[1] += g
    return {y: v[0] / v[1] for y, v in out.items() if v[1] > 0}

def lvm_pitching_pf(st, year, p):
    c = constants(year)
    ip = float(st.get("inningsPitched", 0) or 0)
    if not ip: return 0.0
    fip = (13 * st.get("homeRuns", 0) + 3 * (st.get("baseOnBalls", 0) + st.get("hitByPitch", 0))
           - 2 * st.get("strikeOuts", 0)) / ip + c["cfip"]
    if p != 1.0:
        fip = fip / p
    return ((c["lg_fip"] - fip) / c["rpw"]) * ip / 9 + 0.105 * ip / 9

def season_extra(pid, y, inn=None, diag=None):
    """defense + baserunning runs -> wins. v1.7: defense from def_runs()
    (DRS infield, FRV catcher/outfield); baserunning unchanged (Statcast
    runner runs, 2016+). diag, if a dict, receives the components."""
    d, det = def_runs(pid, y, inn)
    b = SV.get(str(pid), {}).get(str(y), {}).get("bsr", 0.0)
    if diag is not None:
        diag.update(det); diag["def"] = d; diag["bsr"] = b; diag["rpw"] = constants(y)["rpw"]
    runs = d + b
    if not runs: return 0.0
    return runs / constants(y)["rpw"]

def player_team_seasons_v15(ids, diag=None):
    """{mlbam: {'name', rows: [[year, teamName, parkAdjValue+defJoin]]}}
    diag, if a dict, receives {mlbam: {"base": rows before the join,
    "years": {year: season_extra components}}} for audits."""
    out = {}
    ids = [i for i in ids if i]
    for i in range(0, len(ids), 40):
        chunk = ",".join(str(x) for x in ids[i:i+40])
        try:
            d = get(f"{API}/people?personIds={chunk}&hydrate=stats(group=[hitting,pitching,fielding],type=[yearByYear])")
        except Exception as e:
            print(f"  batch fail {i}: {e}", flush=True); continue
        for pp in d.get("people", []):
            pos = pp["primaryPosition"]["abbreviation"]
            rows = []
            FSPL = [sp for grp in pp.get("stats", []) if grp["group"]["displayName"] == "fielding" for sp in grp.get("splits", [])]
            PADJ = season_posadj(FSPL)
            INN = season_innings(FSPL)
            for grp in pp.get("stats", []):
                g = grp["group"]["displayName"]
                if g == "fielding": continue
                for sp in grp.get("splits", []):
                    tmo = sp.get("team") or {}
                    tm = tmo.get("name")
                    if not tm: continue
                    yr = int(sp["season"]); st = sp["stat"]
                    p = pf(tmo.get("id"), yr)
                    if g == "hitting" and st.get("plateAppearances"):
                        rows.append([yr, tm, lvm_batting_pf(st, yr, pos, p, PADJ.get(yr))])
                    elif g == "pitching" and st.get("inningsPitched"):
                        rows.append([yr, tm, lvm_pitching_pf(st, yr, p)])
            # defense/baserunning join, split across team rows by |off| share
            byyear = {}
            for idx, (y, tm, v) in enumerate(rows):
                byyear.setdefault(y, []).append(idx)
            if diag is not None:
                diag[pp["id"]] = {"base": [list(r) for r in rows], "years": {}}
            for y, idxs in byyear.items():
                dg = None
                if diag is not None: dg = diag[pp["id"]]["years"].setdefault(y, {})
                extra = season_extra(pp["id"], y, INN.get(y), dg)
                if not extra: continue
                tot = sum(abs(rows[k][2]) for k in idxs)
                for k in idxs:
                    share = (abs(rows[k][2]) / tot) if tot > 0 else (1.0 / len(idxs))
                    rows[k][2] += extra * share
            out[pp["id"]] = dict(name=pp["fullName"], rows=rows)
        if (i // 40) % 10 == 0: print(f"  LVM15 {i}/{len(ids)}", flush=True)
    return out
