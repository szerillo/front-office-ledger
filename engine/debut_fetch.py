"""v5.9: MLB debut dates for every valued player (MLB Stats API), so club
control can be dated: a player who debuts after mid-April does not bank a
full year of service that season, and his control runs one season longer."""
import json, os, sys, time, urllib.request
OUT = "/work/debuts.json"
have = json.load(open(OUT)) if os.path.exists(OUT) else {}
L = json.load(open("/work/lvm_cache.json"))
pids = [k for k in L if not k.startswith("__")]
E = json.load(open("/work/ext_lvm_cache.json"))
pids += [k for k in E if not str(k).startswith("__")]
todo = [p for p in dict.fromkeys(pids) if p not in have]
print("to fetch", len(todo))
for i in range(0, len(todo), 150):
    ch = todo[i:i+150]
    url = "https://statsapi.mlb.com/api/v1/people?personIds=" + ",".join(ch) + "&fields=people,id,mlbDebutDate"
    for att in range(3):
        try:
            d = json.load(urllib.request.urlopen(url, timeout=60)); break
        except Exception as e:
            print("retry", e); time.sleep(2)
    else: continue
    for p in d.get("people", []): have[str(p["id"])] = p.get("mlbDebutDate")
    for p in ch: have.setdefault(p, None)
    if i % 3000 == 0: print(i); json.dump(have, open(OUT, "w"))
json.dump(have, open(OUT, "w"))
print("debuts:", sum(1 for v in have.values() if v), "of", len(have))
