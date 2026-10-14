"""
DEAL DESK data pack: everything the in-page evaluator needs, compact.
Writes desk_data.json:
  players: [name, pid, team abbr (2026 club or prospect org), isPit,
            age2026, w2024, w2025, w2026, ctrlDefault, rank2026]
  curves:  aging curves + pop mean (proj_curves.json)
  market:  dollars-per-win table, control-bucket price ratios + bust rates,
           star-rental rate, unranked prospect EV
  slot:    draft pick slot-expectation anchors
  teams:   {abbr: 2026 win total}
  deals:   compact 1998-2023 archive [yr, ab, ph, ck, po, recv, paid, who]
"""
import json, sqlite3
from collections import defaultdict

LVM = {int(k): v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}
AGES = json.load(open("/home/claude/ages.json"))
POS = json.load(open("/home/claude/positions.json"))
PITPOS = {"RHP", "LHP", "SP", "RP", "P"}
PC = json.load(open("/home/claude/proj_curves.json"))
RM = json.load(open("/home/claude/rental_market.json"))
cfg = json.load(open("/home/claude/regimes.json"))
ABBR_BY_NAME = {}
for r in cfg["regimes"]:
    ABBR_BY_NAME[r["team"]] = r["abbr"]
    for al in cfg["aliases"].get(str(r["teamId"]), []):
        ABBR_BY_NAME[al] = r["abbr"]

RANKS = {}
ORGS = {}
for rr in json.load(open("/home/claude/prospect_ranks.json")):
    if rr["year"] in (2025, 2026):
        RANKS[str(rr["pid"])] = rr["rank"]
        ORGS[str(rr["pid"])] = rr.get("name")
try:
    porgs = json.load(open("/home/claude/prospect_orgs.json"))
except Exception:
    porgs = {}

BY = {}
for pid, rec in LVM.items():
    d = defaultdict(float)
    last_team = None; last_y = 0
    for (y, tm, v) in rec["rows"]:
        d[y] += v
        if y >= last_y: last_y, last_team = y, tm
    BY[pid] = (dict(d), last_team, rec["name"])

players = []
for pid, (d, last_team, name) in BY.items():
    recent = any(y in d for y in (2024, 2025, 2026))
    ranked = str(pid) in RANKS
    if not (recent or ranked): continue
    mlb_seasons = sum(1 for v in d.values() if abs(v) > 0.05)
    ctrl = max(1, min(6, 6 - mlb_seasons))
    age = 2026 - AGES.get(str(pid), 2000)
    ab = ABBR_BY_NAME.get(last_team or "", "")
    players.append([name, pid, ab, 1 if POS.get(str(pid)) in PITPOS else 0,
                    age if 16 < age < 50 else 27,
                    round(d.get(2024, 0), 1), round(d.get(2025, 0), 1), round(d.get(2026, 0), 1),
                    ctrl, RANKS.get(str(pid), 0)])
players.sort(key=lambda p: -(abs(p[5]) + abs(p[6]) + abs(p[7])))
print("desk players:", len(players))

# team 2026 win totals
import urllib.request, time
def get(u, tries=3):
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=40))
        except Exception: time.sleep(2+2*a)
    return {}
TID2AB = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
teams = {}
d = get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason")
for g in d.get("records", []):
    for t in g.get("teamRecords", []):
        ab = TID2AB.get(t["team"]["id"])
        if ab: teams[ab] = t.get("wins", 81)

deals = json.load(open("/home/claude/deal_archive.json"))
compact = [[x["yr"], x["ab"], x["ph"][0], x["ck"], x.get("po", "mid")[0], x["recv"], x["paid"], x["who"][:24]] for x in deals]

out = dict(
    players=players,
    curves=dict(bat=PC["curves"]["bat"], pit=PC["curves"]["pit"], pop=PC["pop_mean"],
                unrankedEV=PC["unranked_ev"], backtest=PC["backtest"]),
    market=dict(dpw={str(k): v for k, v in
                     {2026: 9.7, 2027: 10.0, 2028: 10.3, 2029: 10.6, 2030: 10.9, 2031: 11.2, 2032: 11.5}.items()},
                buckets={"rental": dict(ratio=0.8, bust=0.55), "+1": dict(ratio=0.99, bust=0.48),
                         "+2": dict(ratio=0.86, bust=0.39), "3+": dict(ratio=0.37, bust=0.71)},
                extDiscount={"predebut": 0.35, "early": 0.45, "arb": 0.60, "vet": 0.90}),
    slot=[[1, 9.9], [2, 7.5], [3, 6.7], [5, 5.5], [8, 4.6], [12, 3.6], [17, 3.0], [22, 2.6],
          [30, 2.1], [45, 1.5], [65, 1.1], [90, 0.85], [120, 0.6], [200, 0.35], [400, 0.18], [620, 0.10]],
    vrank=[[1, 8.0], [3, 7.0], [5, 6.5], [10, 5.5], [15, 4.8], [25, 4.0], [40, 3.2], [50, 2.8], [75, 2.0], [100, 1.5]],
    teams=teams,
    deals=compact,
)
json.dump(out, open("/home/claude/desk_data.json", "w"), separators=(",", ":"))
import os
print("desk_data.json:", round(os.path.getsize("/home/claude/desk_data.json") / 1e6, 2), "MB")
