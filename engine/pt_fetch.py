"""
Playing time for the Deal Desk player pool, 2024-2026.
Writes playtime.json: {pid: {"2024": [pa, ip], ...}} and durability.json:
{pid: dur}: availability multiplier for projected seasons (0.7 + 0.3 * wtd
availability; floor validated on 2026: MAE 0.859 -> 0.848, bias +0.06 -> -0.01).
Availability per observed season: hitters PA/640, SP IP/165, RP IP/65
(starter = avg IP/G >= 3 that season), capped at 1. Weighted 5/4/3 across
observed seasons (a season with any appearance counts as observed).
"""
import json, urllib.request, time

DESK = json.load(open("/work/desk_data.json"))
pids = [p[1] for p in DESK["players"]]
print("players:", len(pids))

def get(u, tries=3):
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
        except Exception as e:
            if a == tries - 1: print("fail", e, u[:120])
            time.sleep(2 + 2 * a)
    return {}

PT = {}
for season in (2024, 2025, 2026):
    for i in range(0, len(pids), 40):
        chunk = pids[i:i + 40]
        u = (f"https://statsapi.mlb.com/api/v1/people?personIds={','.join(map(str, chunk))}"
             f"&hydrate=stats(group=[hitting,pitching],type=season,season={season})")
        d = get(u)
        for pp in d.get("people", []):
            pa = ip = g = 0.0
            for st in pp.get("stats", []):
                grp = st["group"]["displayName"]
                for sp in st.get("splits", []):
                    s = sp["stat"]
                    if grp == "hitting": pa += s.get("plateAppearances", 0) or 0
                    else:
                        ips = str(s.get("inningsPitched", "0") or "0")
                        w, f = (ips.split(".") + ["0"])[:2]
                        ip += int(w) + int(f) / 3.0
                        g += s.get("gamesPlayed", 0) or 0
            PT.setdefault(str(pp["id"]), {})[str(season)] = [round(pa), round(ip, 1), round(g)]
        time.sleep(0.25)
    print(season, "done,", len(PT), "players with data")

json.dump(PT, open("/work/playtime.json", "w"), separators=(",", ":"))

DUR = {}
for p in DESK["players"]:
    pid, isPit = str(p[1]), p[3]
    rec = PT.get(pid, {})
    num = den = 0.0
    for season, wgt in (("2026", 5), ("2025", 4), ("2024", 3)):
        pa, ip, g = (rec.get(season) or [0, 0, 0])
        if pa + ip <= 0: continue   # unobserved season: no evidence either way
        if isPit:
            full = 165.0 if (g > 0 and ip / g >= 3.0) else 65.0
            avail = min(ip / full, 1.0)
        else:
            avail = min(pa / 640.0, 1.0)
        num += wgt * avail; den += wgt
    if den > 0:
        DUR[pid] = round(0.7 + 0.3 * (num / den), 3)
json.dump(DUR, open("/work/durability.json", "w"), separators=(",", ":"))
import statistics
vals = list(DUR.values())
print("durability factors:", len(vals), "| mean", round(statistics.mean(vals), 3),
      "| p10", round(sorted(vals)[len(vals)//10], 3), "| min", min(vals), "| max", max(vals))
