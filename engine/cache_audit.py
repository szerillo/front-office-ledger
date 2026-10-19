"""
Value-cache completeness audit: every player with a meaningful MLB season
(>= 150 PA or >= 40 IP) 1998-2026 vs the lvm cache. Writes cache_missing.json.
"""
import json, urllib.request, time

raw = json.load(open("/home/claude/lvm_cache.json"))
have = {int(k) for k in raw if not k.startswith("__")}

def get(u, tries=3):
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
        except Exception as e:
            if a == tries - 1: print("fail", e, u[:100])
            time.sleep(2 + 2 * a)
    return {}

missing = {}          # pid -> {name, seasons: [...], maxpa, maxip}
seen_sig = set()      # all significant pids
for season in range(1998, 2027):
    for grp, key, floor in (("hitting", "plateAppearances", 150), ("pitching", "inningsPitched", 40)):
        u = (f"https://statsapi.mlb.com/api/v1/stats?stats=season&group={grp}&season={season}"
             f"&sportId=1&playerPool=ALL&limit=1500")
        d = get(u)
        for sp in (d.get("stats", [{}])[0].get("splits", []) if d.get("stats") else []):
            st = sp.get("stat", {})
            val = float(st.get(key, 0) or 0)
            if val < floor: continue
            pid = sp.get("player", {}).get("id")
            if not pid: continue
            seen_sig.add(pid)
            if pid not in have:
                m = missing.setdefault(pid, dict(name=sp["player"].get("fullName"), seasons=[], pa=0, ip=0.0))
                m["seasons"].append(season)
                if grp == "hitting": m["pa"] += int(val)
                else: m["ip"] += val
    time.sleep(0.2)
    if season % 5 == 0: print(season, "sig so far", len(seen_sig), "missing", len(missing), flush=True)

print("significant players 1998-2026:", len(seen_sig))
print("MISSING from cache:", len(missing))
top = sorted(missing.items(), key=lambda kv: -(kv[1]["pa"] + kv[1]["ip"] * 3))
for pid, m in top[:25]:
    print(pid, m["name"], "PA", m["pa"], "IP", round(m["ip"]), "seasons", f'{min(m["seasons"])}-{max(m["seasons"])}')
json.dump({str(k): v for k, v in missing.items()}, open("/home/claude/cache_missing.json", "w"))
