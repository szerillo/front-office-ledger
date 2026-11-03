"""v6.1: prospects who reached the majors in 2026.

The Top 100 and the org lists still carry players who debuted during the
season (rookie limits, not service time, decide who graduates). The boards
show their level as MLB and their 2026 big-league line, so a player like
Cooper Pratt is not listed as a Triple-A bat. Values are unchanged: they
come from rank and the minor-league record, as before.

Writes debut26.json: {pid: [debut date, line]}.
"""
import json, os, time, urllib.request

ROOT = "/work"
RANKS = [x for x in json.load(open(f"{ROOT}/prospect_ranks.json")) if x["year"] == 2026]
PROS = json.load(open(f"{ROOT}/pros.json"))
DEB = json.load(open(f"{ROOT}/debuts.json")) if os.path.exists(f"{ROOT}/debuts.json") else {}
cands = {str(x["pid"]) for x in RANKS if x.get("pid")} | set(PROS.get("org", {}))

def get(url):
    for att in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
        except Exception as e: print("retry", e); time.sleep(2 + att * 2)
    return {}

todo = [p for p in cands if p not in DEB]
for i in range(0, len(todo), 150):
    d = get("https://statsapi.mlb.com/api/v1/people?personIds=" + ",".join(todo[i:i + 150]) + "&fields=people,id,mlbDebutDate")
    for x in d.get("people", []): DEB[str(x["id"])] = x.get("mlbDebutDate")
deb = [p for p in cands if str(DEB.get(p) or "").startswith("2026")]
out = {}
for pid in deb:
    d = get(f"https://statsapi.mlb.com/api/v1/people/{pid}/stats?stats=season&season=2026&group=hitting,pitching&sportId=1")
    hit = pit = None
    for s in d.get("stats", []):
        sp = (s.get("splits") or [{}])[0].get("stat") or {}
        if s.get("group", {}).get("displayName") == "hitting" and sp.get("plateAppearances"): hit = sp
        if s.get("group", {}).get("displayName") == "pitching" and sp.get("inningsPitched") not in (None, "0.0"): pit = sp
    if pit and (not hit or float(pit.get("inningsPitched", 0)) * 3 >= hit.get("plateAppearances", 0)):
        line = f"{pit.get('era')} ERA, {pit.get('strikeOuts')} K in {pit.get('inningsPitched')} IP"
    elif hit:
        line = f"{hit.get('avg')}/{hit.get('obp')}/{hit.get('slg')}, {hit.get('homeRuns')} HR in {hit.get('plateAppearances')} PA"
    else:
        line = ""
    out[pid] = [DEB[pid], line]
    time.sleep(0.15)
json.dump(out, open(f"{ROOT}/debut26.json", "w"), ensure_ascii=False)
print("prospects who debuted in 2026:", len(out))
for pid, v in list(out.items())[:12]: print("  ", pid, v)
