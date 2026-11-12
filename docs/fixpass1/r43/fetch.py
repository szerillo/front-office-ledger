# Round 43, item 3: pitching splits (innings as the feed writes them) for every cache player, plus league totals.
import json, sys, time, urllib.request, concurrent.futures as cf
API = "https://statsapi.mlb.com/api/v1"
def get(u):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "FrontOfficeLedger-audit/0.1"}), timeout=40) as r: return json.load(r)
        except Exception as e:
            if i == 3: raise
            time.sleep(2 + 2 * i)
L = json.load(open('/work/lvm_cache.json'))
ids = sorted(int(k) for k, v in L.items() if isinstance(v, dict) and k.isdigit())
chunks = [ids[i:i + 40] for i in range(0, len(ids), 40)]
out = {}; fails = []
def job(ch):
    d = get(f"{API}/people?personIds={','.join(map(str, ch))}&hydrate=stats(group=[pitching],type=[yearByYear])")
    res = {}
    for pp in d.get("people", []):
        rows = []
        for grp in pp.get("stats", []):
            for sp in grp.get("splits", []):
                tmo = sp.get("team") or {}
                if not tmo.get("name") or not sp["stat"].get("inningsPitched"): continue
                st = sp["stat"]; rows.append([int(sp["season"]), tmo["name"], tmo.get("id"), st.get("inningsPitched"), st.get("homeRuns", 0), st.get("baseOnBalls", 0), st.get("hitByPitch", 0), st.get("strikeOuts", 0)])
        if rows: res[pp["id"]] = rows
    return res
with cf.ThreadPoolExecutor(3) as ex:
    futs = {ex.submit(job, ch): n for n, ch in enumerate(chunks)}
    for i, f in enumerate(cf.as_completed(futs)):
        try: out.update(f.result())
        except Exception as e: fails.append(futs[f])
        if i % 100 == 0: print(i, len(chunks), len(out), flush=True)
lg = {}
for y in range(1998, 2027):
    hit = get(f"{API}/teams/stats?season={y}&group=hitting&stats=season&sportId=1")["stats"][0]["splits"]
    pit = get(f"{API}/teams/stats?season={y}&group=pitching&stats=season&sportId=1")["stats"][0]["splits"]
    lg[y] = {"hit": [s["stat"] for s in hit], "pit": [s["stat"] for s in pit]}
json.dump({"pitch": out, "lg": lg, "fails": fails}, open('/tmp/r43/ip/feed.json', 'w'))
print('DONE', len(out), 'fails', len(fails))
