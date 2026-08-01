"""LVM v1 inputs: real defense and baserunning from Baseball Savant
(Statcast, MLB's own property, free CSV endpoints, native MLBAM ids).

  fielding_runs_prevented   OAA leaderboard, 2016+ (position players)
  rv_tot                    catcher framing runs, 2015+
  runner_runs               baserunning run value, 2016+

Output: savant_runs.json {pid: {year: {"def": r, "frame": r, "bsr": r}}}
Pre-2016 seasons stay batting+positional only (disclosed).
"""
import csv, io, json, time, urllib.request

def get_csv(url, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for a in range(tries):
        try:
            d = urllib.request.urlopen(req, timeout=45).read().decode("utf-8-sig", "ignore")
            return list(csv.DictReader(io.StringIO(d)))
        except Exception:
            time.sleep(3 + 2 * a)
    return []

OUT = {}
def add(pid, yr, key, val):
    if not pid or not val: return
    try: v = float(val)
    except ValueError: return
    if v == 0: return
    OUT.setdefault(str(int(float(pid))), {}).setdefault(str(yr), {})[key] = \
        OUT.get(str(int(float(pid))), {}).get(str(yr), {}).get(key, 0.0) + v

for yr in range(2016, 2027):
    rows = get_csv(f"https://baseballsavant.mlb.com/leaderboard/outs_above_average?type=Fielder&startYear={yr}&endYear={yr}&split=no&team=&range=year&min=1&pos=&roles=&viz=hide&csv=true")
    for r in rows:
        add(r.get("player_id"), yr, "def", r.get("fielding_runs_prevented"))
    print(f"{yr} OAA rows: {len(rows)}", flush=True)
    time.sleep(0.8)

for yr in range(2015, 2027):
    rows = get_csv(f"https://baseballsavant.mlb.com/leaderboard/catcher-framing?type=catcher&seasonStart={yr}&seasonEnd={yr}&team=&min=1&sortColumn=rv_tot&sortDirection=desc&csv=true")
    for r in rows:
        add(r.get("id"), yr, "frame", r.get("rv_tot"))
    print(f"{yr} framing rows: {len(rows)}", flush=True)
    time.sleep(0.8)

for yr in range(2016, 2027):
    rows = get_csv(f"https://baseballsavant.mlb.com/leaderboard/baserunning-run-value?game_type=Regular&season_start={yr}&season_end={yr}&split=no&n=1&sortColumn=runner_runs_tot&sortDirection=desc&csv=true")
    key = "runner_runs_tot" if rows and "runner_runs_tot" in rows[0] else "runner_runs"
    for r in rows:
        add(r.get("player_id") or r.get("entity_id"), yr, "bsr", r.get(key))
    print(f"{yr} baserunning rows: {len(rows)}", flush=True)
    time.sleep(0.8)

json.dump(OUT, open("/home/claude/savant_runs.json", "w"))
n_py = sum(len(v) for v in OUT.values())
print(f"\nsaved savant_runs.json: {len(OUT)} players, {n_py} player-seasons")
