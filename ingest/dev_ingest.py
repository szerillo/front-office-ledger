"""DEV pillar ingest: for every player who ever appeared on a Pipeline top-100
(2011-2026), pull minor-league season->team splits (sports 11-16), map each
minor club to its MLB parent org by season, and pull MLB debut dates.
Output: prospect_orgs.json  {pid: {"debut": date|None, "name": str,
  "seasons": {year: [teamIds...]}, "orgs": {year: [parentOrgIds...]}}}"""
import json, time, urllib.request

def get(url, tries=4):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception:
            time.sleep(2 + a*2)
    return {}

API = "https://statsapi.mlb.com/api/v1"
ranks = json.load(open("/home/claude/prospect_ranks.json"))
pids = sorted({r["pid"] for r in ranks})
print(f"distinct ranked players: {len(pids)}", flush=True)

# 1. minor team -> parent org, per season
parent = {}  # (season, teamId) -> parentOrgId
for sid in [11, 12, 13, 14, 15, 16]:
    for yr in range(2010, 2027):
        d = get(f"{API}/teams?sportId={sid}&season={yr}&fields=teams,id,parentOrgId")
        for t in d.get("teams", []):
            if t.get("parentOrgId"): parent[(yr, t["id"])] = t["parentOrgId"]
print(f"minor team-season parent map: {len(parent)}", flush=True)

# 2. per-player minor season splits
out = {}
t0 = time.time()
for i, pid in enumerate(pids):
    seasons = {}
    for sid in [11, 12, 13, 14, 15, 16]:
        d = get(f"{API}/people/{pid}/stats?stats=yearByYear&group=hitting,pitching&sportId={sid}&fields=stats,splits,season,team,id")
        for st in d.get("stats", []):
            for sp in st.get("splits", []):
                y = int(float(sp["season"])); tid = (sp.get("team") or {}).get("id")
                if tid: seasons.setdefault(y, []).append(tid)
    orgs = {}
    for y, tids in seasons.items():
        o = []
        for tid in tids:
            po = parent.get((y, tid))
            if po and po not in o: o.append(po)
        if o: orgs[y] = o
    out[str(pid)] = dict(seasons={str(k): v for k, v in seasons.items()},
                         orgs={str(k): v for k, v in orgs.items()})
    if (i+1) % 50 == 0:
        el = time.time() - t0
        print(f"{i+1}/{len(pids)} players, {el:.0f}s elapsed, eta {el/(i+1)*(len(pids)-i-1):.0f}s", flush=True)
        json.dump(out, open("/home/claude/prospect_orgs.json", "w"))

# 3. debut dates + names in batches
for i in range(0, len(pids), 100):
    chunk = ",".join(str(p) for p in pids[i:i+100])
    d = get(f"{API}/people?personIds={chunk}&fields=people,id,mlbDebutDate,fullName")
    for p in d.get("people", []):
        rec = out.setdefault(str(p["id"]), {})
        rec["debut"] = p.get("mlbDebutDate")
        rec["name"] = p.get("fullName")

json.dump(out, open("/home/claude/prospect_orgs.json", "w"))
print("saved prospect_orgs.json:", len(out), "players", flush=True)
