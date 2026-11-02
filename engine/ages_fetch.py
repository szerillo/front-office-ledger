"""Fetch birth dates for every player in the value cache (people API, batched).
Writes ages.json: {pid: season birth year}.

v5.4: baseball's season age is the player's age on June 30 of the season.
The stored value is the birth year, plus one when the birthday falls after
June 30, so (season - value) IS the season age everywhere it is used. The
plain birth year ran half the league a year old (Soto "24" in a winter he
was 23)."""
import json, time, urllib.request

def get(u, tries=3):
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=40))
        except Exception: time.sleep(2 + 2*a)
    return {}

ids = sorted(int(k) for k in json.load(open("/work/lvm_cache.json")) if not k.startswith("__"))
out = {}
for i in range(0, len(ids), 100):
    chunk = ",".join(str(x) for x in ids[i:i+100])
    d = get(f"https://statsapi.mlb.com/api/v1/people?personIds={chunk}&fields=people,id,birthDate")
    for p in d.get("people", []):
        bd = p.get("birthDate")
        if bd: out[str(p["id"])] = int(bd[:4]) + (1 if bd[5:10] > "06-30" else 0)
    if (i // 100) % 30 == 0: print(i, len(out), flush=True)
json.dump(out, open("/work/ages.json", "w"))
print("ages:", len(out))
