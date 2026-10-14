"""Park factors from home/away run environments, 2005-2026. 3-yr centered
rolling, regressed halfway to 1. Output parks.json {teamName: {year: PF}}."""
import json, time, urllib.request
def get(u, tries=3):
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=40))
        except Exception: time.sleep(2+2*a)
    return {}
API = "https://statsapi.mlb.com/api/v1"
cfg = json.load(open("regimes.json"))
raw = {}
for reg in cfg["regimes"]:
    tid = reg["teamId"]
    for yr in range(2004, 2027):
        hs = ha = as_ = aa = hg = ag = 0
        for grp in ("hitting", "pitching"):
            d = get(f"{API}/teams/{tid}/stats?stats=statSplits&sitCodes=h,a&group={grp}&season={yr}")
            try: splits = d["stats"][0]["splits"]
            except Exception: splits = []
            for s in splits:
                code = s.get("split", {}).get("code"); st = s["stat"]
                r = st.get("runs", 0); g = st.get("gamesPlayed", 0)
                if grp == "hitting":
                    if code == "h": hs, hg = r, g
                    else: as_, ag = r, g
                else:
                    if code == "h": ha = r
                    else: aa = r
        if hg >= 20 and ag >= 20:
            raw[(tid, yr)] = ((hs + ha) / hg) / max(0.1, (as_ + aa) / ag)
    print(reg["abbr"], "done", flush=True)
# 3-yr centered rolling, regress 50% to 1
PF = {}
NAMES = {r["teamId"]: r["team"] for r in cfg["regimes"]}
ALIAS = cfg["aliases"]
for (tid, yr), v in raw.items():
    window = [raw.get((tid, y)) for y in (yr-1, yr, yr+1)]
    window = [x for x in window if x]
    pf3 = sum(window) / len(window)
    pf = 1 + (pf3 - 1) * 0.5
    PF.setdefault(str(tid), {})[str(yr)] = round(pf, 4)
out = dict(byTeamId=PF)
json.dump(out, open("parks.json", "w"))
print("parks.json written:", sum(len(v) for v in PF.values()), "team-years")
