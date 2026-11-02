"""Season box-score lines (v5.6) for every contract-book player and every
Desk player, from the public MLB Stats API (yearByYear, hitting + pitching).
These are the numbers the market itself sees; the contract model uses them
alongside Ledger WAR. Cache: season_stats.json {pid: {year: {...}}}."""
import json, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT = "/work"
OUT = f"{ROOT}/season_stats.json"
cache = {}   # v5.6 fix: always rebuild (combined rows for traded players)
desk = json.load(open(f"{ROOT}/desk_data.json"))
pids = {str(c[11]) for c in desk["book"] if c[11]} | {str(p[1]) for p in desk["players"]}
todo = sorted(p for p in pids if p not in cache)
print("players:", len(pids), "to fetch:", len(todo), flush=True)
def get(pid):
    u = f"https://statsapi.mlb.com/api/v1/people/{pid}/stats?stats=yearByYear&group=hitting,pitching&sportId=1"
    for a in range(4):
        try:
            x = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
            out = {}
            for st in x.get("stats", []):
                g = st["group"]["displayName"]
                sps = [sp for sp in st.get("splits", []) if sp.get("sport", {}).get("id", 1) == 1]
                # a traded player's season comes as one row per club PLUS a
                # combined row without a team: use the combined row alone
                tot_seasons = {sp["season"] for sp in sps if not sp.get("team")}
                sps = [sp for sp in sps if not sp.get("team") or sp["season"] not in tot_seasons]
                for sp in sps:
                    y = sp["season"]; s = sp["stat"]
                    d = out.setdefault(y, {})
                    if g == "hitting":
                        h = d.setdefault("h", dict(pa=0, ab=0, hits=0, hr=0, bb=0, so=0, tb=0, sb=0, hbp=0, sf=0))
                        for k, kk in (("pa","plateAppearances"),("ab","atBats"),("hits","hits"),("hr","homeRuns"),("bb","baseOnBalls"),("so","strikeOuts"),("tb","totalBases"),("sb","stolenBases"),("hbp","hitByPitch"),("sf","sacFlies")):
                            h[k] += int(s.get(kk, 0) or 0)
                    elif g == "pitching":
                        p = d.setdefault("p", dict(ip=0.0, gs=0, g=0, er=0, so=0, bb=0, bf=0, hr=0, sv=0))
                        ip = str(s.get("inningsPitched", "0") or "0"); w, _, f = ip.partition(".")
                        p["ip"] += int(w or 0) + int(f or 0) / 3
                        for k, kk in (("gs","gamesStarted"),("g","gamesPlayed"),("er","earnedRuns"),("so","strikeOuts"),("bb","baseOnBalls"),("bf","battersFaced"),("hr","homeRuns"),("sv","saves")):
                            p[k] += int(s.get(kk, 0) or 0)
            return pid, out
        except Exception:
            time.sleep(1.5 * (a + 1))
    return pid, None
done = 0
with ThreadPoolExecutor(8) as ex:
    for pid, out in ex.map(get, todo):
        if out is not None: cache[pid] = out
        done += 1
        if done % 200 == 0:
            json.dump(cache, open(OUT, "w")); print("fetched", done, flush=True)
json.dump(cache, open(OUT, "w"))
print("season_stats.json:", len(cache))
