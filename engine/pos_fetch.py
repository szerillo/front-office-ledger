"""Fetch primary position for every player in the value cache. Writes positions2.json {pid: posAbbr}."""
import json, time, urllib.request
def get(u, tries=3):
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=40))
        except Exception: time.sleep(2 + 2*a)
    return {}
ids = sorted(int(k) for k in json.load(open("/home/claude/lvm_cache.json")) if not k.startswith("__"))
out = {}
for i in range(0, len(ids), 100):
    chunk = ",".join(str(x) for x in ids[i:i+100])
    d = get(f"https://statsapi.mlb.com/api/v1/people?personIds={chunk}&fields=people,id,primaryPosition,abbreviation")
    for p in d.get("people", []):
        ab = (p.get("primaryPosition") or {}).get("abbreviation")
        if ab: out[str(p["id"])] = ab
    if (i // 100) % 50 == 0: print(i, len(out), flush=True)
json.dump(out, open("/home/claude/positions2.json", "w"))
print("positions2:", len(out))
