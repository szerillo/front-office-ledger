"""v6.1 (Nov 3): where every player's career started, for the top of his tree.

Draftees: year, round, overall pick, club and signing bonus from the MLB Stats
API draft results (1985-2026). International amateurs: birth country and date
(ifa_bios.json), so the page can say who signed him, where from and at what
age; their bonuses are not in the public data, so none is shown.

Writes origins.json: {"d": {pid: [year, round, pick, abbr, bonus$]}, "b": {pid: [birthdate, country]}}.
"""
import json, os, time, urllib.request
ROOT = "/work"; C = f"{ROOT}/milb_cache"; os.makedirs(C, exist_ok=True)
cfg = json.load(open(f"{ROOT}/regimes.json"))
n2a = {}
for r in cfg["regimes"]: n2a[r["team"]] = r["abbr"]
tid2a = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
for k, v in cfg.get("aliases", {}).items():
    for nm in v: n2a[nm] = tid2a.get(int(k), n2a.get(nm))
def get(y):
    p = f"{C}/draft_{y}.json"
    if os.path.exists(p): return json.load(open(p))
    for a in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(f"https://statsapi.mlb.com/api/v1/draft/{y}", headers={"User-Agent": "Mozilla/5.0"}), timeout=90))
            json.dump(d, open(p, "w")); time.sleep(0.3); return d
        except Exception as e: print("retry", y, e); time.sleep(3)
    return {}
D = {}
for y in range(1985, 2027):
    d = get(y)
    for rd in (d.get("drafts") or {}).get("rounds", []):
        for pk in rd.get("picks", []):
            per = pk.get("person") or {}
            pid = per.get("id")
            if not pid: continue
            ab = tid2a.get((pk.get("team") or {}).get("id")) or n2a.get((pk.get("team") or {}).get("name", ""))
            if not ab: continue
            bonus = pk.get("signingBonus")
            try: bonus = int(float(bonus)) if bonus not in (None, "") else 0
            except Exception: bonus = 0
            rnd = pk.get("pickRound") or ""
            row = [y, rnd, pk.get("pickNumber") or 0, ab, bonus]
            prev = D.get(str(pid))
            # the draft he signed out of wins; otherwise the latest one
            if not prev or (bonus and not prev[4]) or (bool(bonus) == bool(prev[4]) and y > prev[0]): D[str(pid)] = row
    print(y, len(D))
B = {k: v for k, v in json.load(open(f"{ROOT}/ifa_bios.json")).items() if v and len(v) > 1 and v[1] and v[1] != "USA"}
json.dump({"d": D, "b": B}, open(f"{ROOT}/origins.json", "w"), separators=(",", ":"))
print("draft origins", len(D), "| non-US bios", len(B))
