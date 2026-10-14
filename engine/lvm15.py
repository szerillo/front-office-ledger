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
defense-joined (SDI/Statcast, per lvm_v1.py) fetcher used by the sweep and
the historical scorer so newly discovered players enter the cache at v1.5.
"""
import json
from ledger_war import get, API, constants, _woba_num, _woba_den, WOBA_SCALE, POS_ADJ

PARKS = json.load(open("/home/claude/parks.json"))["byTeamId"]
SV = json.load(open("/home/claude/savant_runs.json"))
SDI = json.load(open("/home/claude/sdi_runs.json"))

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

def lvm_batting_pf(st, year, pos, p):
    c = constants(year)
    pa = st.get("plateAppearances", 0)
    den = _woba_den(st)
    if not pa or not den: return 0.0
    woba = _woba_num(st) / den
    wraa = (woba - c["lg_woba"]) / WOBA_SCALE * pa
    if p != 1.0:
        wraa -= (p - 1.0) * lg_rpa(year) * pa
    adj = (POS_ADJ.get(pos, 0.0) + 20.0) * pa / 600.0
    return (wraa + adj) / c["rpw"]

def lvm_pitching_pf(st, year, p):
    c = constants(year)
    ip = float(st.get("inningsPitched", 0) or 0)
    if not ip: return 0.0
    fip = (13 * st.get("homeRuns", 0) + 3 * (st.get("baseOnBalls", 0) + st.get("hitByPitch", 0))
           - 2 * st.get("strikeOuts", 0)) / ip + c["cfip"]
    if p != 1.0:
        fip = fip / p
    return ((c["lg_fip"] - fip) / c["rpw"]) * ip / 9 + 0.105 * ip / 9

def season_extra(pid, y):
    """defense + baserunning runs -> wins (same join as lvm_v1.py)."""
    ys = str(y)
    sdi = SDI.get(str(pid), {}).get(ys)
    sv = SV.get(str(pid), {}).get(ys, {})
    d = sdi if sdi is not None else (sv.get("def", 0.0) + sv.get("frame", 0.0))
    b = sv.get("bsr", 0.0)
    runs = d + b
    if not runs: return 0.0
    return runs / constants(y)["rpw"]

def player_team_seasons_v15(ids):
    """{mlbam: {'name', rows: [[year, teamName, parkAdjValue+defJoin]]}}"""
    out = {}
    ids = [i for i in ids if i]
    for i in range(0, len(ids), 40):
        chunk = ",".join(str(x) for x in ids[i:i+40])
        try:
            d = get(f"{API}/people?personIds={chunk}&hydrate=stats(group=[hitting,pitching],type=[yearByYear])")
        except Exception as e:
            print(f"  batch fail {i}: {e}", flush=True); continue
        for pp in d.get("people", []):
            pos = pp["primaryPosition"]["abbreviation"]
            rows = []
            for grp in pp.get("stats", []):
                g = grp["group"]["displayName"]
                for sp in grp.get("splits", []):
                    tmo = sp.get("team") or {}
                    tm = tmo.get("name")
                    if not tm: continue
                    yr = int(sp["season"]); st = sp["stat"]
                    p = pf(tmo.get("id"), yr)
                    if g == "hitting" and st.get("plateAppearances"):
                        rows.append([yr, tm, lvm_batting_pf(st, yr, pos, p)])
                    elif g == "pitching" and st.get("inningsPitched"):
                        rows.append([yr, tm, lvm_pitching_pf(st, yr, p)])
            # defense/baserunning join, split across team rows by |off| share
            byyear = {}
            for idx, (y, tm, v) in enumerate(rows):
                byyear.setdefault(y, []).append(idx)
            for y, idxs in byyear.items():
                extra = season_extra(pp["id"], y)
                if not extra: continue
                tot = sum(abs(rows[k][2]) for k in idxs)
                for k in idxs:
                    share = (abs(rows[k][2]) / tot) if tot > 0 else (1.0 / len(idxs))
                    rows[k][2] += extra * share
            out[pp["id"]] = dict(name=pp["fullName"], rows=rows)
        if (i // 40) % 10 == 0: print(f"  LVM15 {i}/{len(ids)}", flush=True)
    return out
