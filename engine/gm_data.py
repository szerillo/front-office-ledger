"""
GM Mode data: historical offseason profiles for comp matching.
For every club-winter 2009-2024: previous season wins, next season wins,
FA dollars committed that winter (book), signing count, offseason trade
activity (deals in the archive dated Nov-Mar), and eventual trade net.
Writes gm_offseasons.json.
"""
import json, urllib.request, time
from collections import defaultdict

DESK = json.load(open("/home/claude/desk_data.json"))
ARCH = json.load(open("/home/claude/deal_archive.json"))
cfg = json.load(open("/home/claude/regimes.json"))
TID2AB = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}

def get(u, tries=3):
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
        except Exception as e:
            if a == tries - 1: print("fail", e)
            time.sleep(2 + 2 * a)
    return {}

WINS = defaultdict(dict)   # season -> ab -> wins
for season in range(2009, 2027):
    d = get(f"https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season={season}&standingsTypes=regularSeason")
    for g in d.get("records", []):
        for t in g.get("teamRecords", []):
            ab = TID2AB.get(t["team"]["id"])
            if ab: WINS[season][ab] = t["wins"]
    time.sleep(0.2)
print("standings seasons:", len(WINS))

# FA dollars by club-winter from the book (FA rows only)
FA = defaultdict(lambda: [0.0, 0])   # (ab, winter) -> [$M, n]
for r in DESK["book"]:
    pl, off, ab, yrs, tot = r[0], r[1], r[2], r[3], r[4]
    if r[12] == 1: continue
    FA[(ab, off)][0] += tot
    FA[(ab, off)][1] += 1

# offseason trades by club-winter (archive is buyer-seat; count both seats)
TR = defaultdict(lambda: [0, 0.0, 0.0])  # (ab, winter) -> [n, in, out]
for x in ARCH:
    if x["ph"] != "offseason": continue
    m = int(x["d"][5:7])
    w = x["yr"] if m >= 10 else x["yr"] - 1
    TR[(x["ab"], w)][0] += 1
    TR[(x["ab"], w)][1] += x["recv"]
    TR[(x["ab"], w)][2] += x["paid"]

rows = []
for winter in range(2009, 2025):
    for ab in TID2AB.values():
        pw, nw = WINS.get(winter, {}).get(ab), WINS.get(winter + 1, {}).get(ab)
        if pw is None or nw is None: continue
        if winter == 2019: continue           # 60-game 2020 poisons next-season wins
        fa = FA.get((ab, winter), [0.0, 0])
        tr = TR.get((ab, winter), [0, 0.0, 0.0])
        rows.append(dict(ab=ab, w=winter, prevW=pw, nextW=nw, faM=round(fa[0], 1), faN=fa[1],
                         trN=tr[0], trIn=round(tr[1], 1), trOut=round(tr[2], 1)))
print("club-winters:", len(rows))
json.dump(dict(winters=rows, wins2026={ab: w for ab, w in WINS.get(2026, {}).items()}),
          open("/home/claude/gm_offseasons.json", "w"), separators=(",", ":"))
print("wrote gm_offseasons.json")
