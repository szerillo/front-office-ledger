"""
GM Mode data: historical offseason profiles for comp matching.
For every club-winter 2009-2025: previous season wins, next season wins,
FA dollars committed that winter (book), signing count, offseason trade
activity (deals in the trade book dated Nov-Mar), and eventual trade net.
Writes gm_offseasons.json.
"""
import json, urllib.request, time
from collections import defaultdict

DESK = json.load(open("/work/desk_data.json"))
cfg = json.load(open("/work/regimes.json"))
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
    if r[12] != 0: continue
    FA[(ab, off)][0] += tot
    FA[(ab, off)][1] += 1

# offseason trades by club-winter, from the deal-level trade book (every
# seat, through the current winter; v5.4 replaces the 1998-2023 buyer archive)
TB = json.load(open("/work/trade_book.json"))
TR = defaultdict(lambda: [0, 0.0, 0.0])  # (ab, winter) -> [n, in, out]
for d, seats in TB["trades"]:
    m = int(d[5:7]); y = int(d[:4])
    if 4 <= m <= 10: continue                 # in-season (April-October)
    w = y if m >= 11 else y - 1
    for s in seats:
        ab = s[0]
        TR[(ab, w)][0] += 1
        TR[(ab, w)][1] += sum(v for _, v in s[2])
        TR[(ab, w)][2] += sum(v for _, v in s[3])

rows = []
for winter in range(2009, 2026):
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
          open("/work/gm_offseasons.json", "w"), separators=(",", ":"))
print("wrote gm_offseasons.json")
