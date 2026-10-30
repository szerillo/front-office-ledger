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
                    ctrl, RANKS.get(str(pid), 0), mlb_seasons])  # mlb_seasons moved to idx 11 below
players.sort(key=lambda p: -(abs(p[5]) + abs(p[6]) + abs(p[7])))
# reorder tail fields: durability at index 10 (from pt_fetch.py; 1.0 default),
# true MLB seasons (service proxy, unclamped) at index 11
try:
    DUR = json.load(open("/home/claude/durability.json"))
except Exception:
    DUR = {}
try:
    PT_RAW = json.load(open("/home/claude/playtime.json"))
except Exception:
    PT_RAW = {}
for p in players:
    svc = p.pop(10)                      # mlb_seasons appended during build
    p.append(DUR.get(str(p[1]), 1.0))    # idx 10: durability
    p.append(svc)                        # idx 11: MLB seasons played
    pp = POS.get(str(p[1]))
    p.append("C" if pp == "C" else "IF" if pp in ("1B","2B","3B","SS") else
             "OF" if pp in ("LF","CF","RF","OF","DH") else "SP" if pp == "SP" else
             "RP" if pp == "RP" else "P")   # idx 12: position group
    # idx 13: depth-chart position. RHP/LHP/P resolved SP vs RP by most
    # recent observed workload (IP/G >= 3 = starter); no record -> RP
    raw = pp or ("P" if p[3] else "OF")
    if raw in ("RHP", "LHP", "P"):
        rec = PT_RAW.get(str(p[1]), {})
        role = "RP"
        for season in ("2026", "2025", "2024"):
            ip, g = (rec.get(season) or [0, 0, 0])[1], (rec.get(season) or [0, 0, 0])[2]
            if ip > 0 and g > 0: role = "SP" if ip / g >= 3.0 else "RP"; break
        raw = role
    p.append(raw)
print("desk players:", len(players), "| with durability:", sum(1 for p in players if p[10] != 1.0))

# resolve org for ranked prospects with no MLB track (no value rows -> no team abbr)
import urllib.request as _ur, time as _t
TID2AB_ALL = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
need = [p for p in players if not p[2] and p[9]]
for i in range(0, len(need), 50):
    chunk = need[i:i+50]
    ids = ",".join(str(p[1]) for p in chunk)
    try:
        d = json.load(_ur.urlopen(f"https://statsapi.mlb.com/api/v1/people?personIds={ids}&hydrate=currentTeam", timeout=40))
        bypid = {pp["id"]: pp.get("currentTeam", {}) for pp in d.get("people", [])}
        for p in chunk:
            ct = bypid.get(p[1], {})
            org = ct.get("parentOrgId") or (ct.get("id") if ct.get("id") in TID2AB_ALL else None)
            if org in TID2AB_ALL: p[2] = TID2AB_ALL[org]
    except Exception as e:
        print("prospect org fetch failed:", e)
    _t.sleep(0.5)
print("prospect orgs resolved:", sum(1 for p in need if p[2]), "of", len(need))

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

# ---- contract book with platform context and realized outcomes ----
import csv, unicodedata, sys
sys.path.insert(0, "/home/claude")
from contracts_recent import RECENT
def norm(nm):
    x = unicodedata.normalize("NFKD", nm or "").encode("ascii", "ignore").decode()
    return x.lower().replace(".", "").replace(" jr", "").strip()
NAME2PIDS = defaultdict(list)
for pid, (d, lt, name) in BY.items():
    NAME2PIDS[norm(name)].append(pid)
TID2AB2 = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
TEAMNAMES = {r["teamId"]: set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in cfg["regimes"]}
def short_to_tid(short):
    for r in cfg["regimes"]:
        names = TEAMNAMES[r["teamId"]]
        if any(short and short.lower() in nm.lower() for nm in names):
            return r["teamId"]
    return None
raw_contracts = []
with open("/home/claude/repo/data/contracts_espn.csv") as f:
    for row in csv.DictReader(f):
        tid = short_to_tid(row["to_team"])
        if tid: raw_contracts.append((int(row["offseason"]), row["player"], tid, int(row["years"]), float(row["total_m"]), 0))
AB2TID = {r["abbr"]: r["teamId"] for r in cfg["regimes"]}
for off, pl, ab, yrs, tot in RECENT:
    raw_contracts.append((off, pl, AB2TID[ab], yrs, float(tot), 0))
# extensions (contracts_ext.EXT): big guaranteed money the FA book never sees.
# A spring signing (month <= 3) covers that season (off = year-1); later
# signings start the next season. CBT value used where it diverges (deferrals).
from contracts_ext import EXT
for (dt, pl, ab, yrs, tot, cbt) in EXT:
    y, m = int(dt[:4]), int(dt[5:7])
    off = y - 1 if m <= 3 else y
    if ab in AB2TID:
        raw_contracts.append((off, pl, AB2TID[ab], yrs, float(cbt if cbt else tot), 1))
book = []
for (off, pl, tid, yrs, tot, typ) in raw_contracts:
    cands = NAME2PIDS.get(norm(pl), [])
    pid = None
    if len(cands) == 1: pid = cands[0]
    elif len(cands) > 1:
        pid = max(cands, key=lambda p: abs(BY[p][0].get(off, 0)) + abs(BY[p][0].get(off - 1, 0)))
    if pid is None: continue
    d = BY[pid][0]
    plat1 = round(d.get(off, 0), 1)             # platform season
    plat2 = round(d.get(off - 1, 0), 1)         # season before
    age = off - AGES.get(str(pid), 0)
    if not (18 < age < 46): continue
    names = TEAMNAMES.get(tid, set())
    elapsed = min(yrs, 2026 - off)
    realized = round(sum(v for (y, tm, v) in LVM[pid]["rows"]
                         if off + 1 <= y <= off + elapsed and tm in names), 1) if elapsed > 0 else None
    pit = 1 if POS.get(str(pid)) in PITPOS else 0
    pgroup = (lambda p: "C" if p == "C" else "IF" if p in ("1B","2B","3B","SS") else
              "OF" if p in ("LF","CF","RF","OF","DH") else "SP" if p == "SP" else
              "RP" if p == "RP" else "P")(POS.get(str(pid)))
    book.append([pl, off, TID2AB2.get(tid, ""), yrs, round(tot, 1), age, pit, plat1, plat2,
                 realized if realized is not None else "", elapsed, pid, typ, pgroup])
print("contract book rows matched:", len(book), "of", len(raw_contracts))

# ---- committed payroll per club per season (book contracts, AAV spread) ----
payroll = {}
for row in book:
    pl, off, ab, yrs, tot = row[0], row[1], row[2], row[3], row[4]
    if not ab or off + yrs < 2026: continue
    aav = tot / yrs
    for season in range(max(2026, off + 1), min(off + yrs, 2031) + 1):
        payroll.setdefault(ab, {}).setdefault(str(season), [0.0, 0])
        payroll[ab][str(season)][0] += aav
        payroll[ab][str(season)][1] += 1
payroll = {ab: {s: [round(v, 1), n] for s, (v, n) in yrsmap.items()} for ab, yrsmap in payroll.items()}
print("payroll clubs:", len(payroll), "| NYM 2027:", payroll.get("NYM", {}).get("2027"))

deals = json.load(open("/home/claude/deal_archive.json"))
compact = [[x["yr"], x["ab"], x["ph"][0], x["ck"], x.get("po", "mid")[0], x["recv"], x["paid"], x["who"][:24]] for x in deals]

out = dict(
    players=players,
    curves=dict(bat=PC["curves"]["bat"], pit=PC["curves"]["pit"], pop=PC["pop_mean"],
                unrankedEV=PC["unranked_ev"], backtest=PC["backtest"]),
    market=dict(dpw={str(k): v for k, v in
                     {2026: 9.7, 2027: 10.0, 2028: 10.3, 2029: 10.6, 2030: 10.9, 2031: 11.2, 2032: 11.5}.items()},
                dpwHist={str(k): v for k, v in {2006:4.2,2007:4.5,2008:4.7,2009:4.7,2010:5.0,2011:5.2,2012:5.5,2013:6.0,
                     2014:6.5,2015:7.0,2016:7.7,2017:8.0,2018:8.2,2019:8.0,2020:8.0,2021:8.5,
                     2022:8.5,2023:9.0,2024:9.3,2025:9.5,2026:9.7}.items()},
                buckets={"rental": dict(ratio=0.8, bust=0.55), "+1": dict(ratio=0.99, bust=0.48),
                         "+2": dict(ratio=0.86, bust=0.39), "3+": dict(ratio=0.37, bust=0.71)},
                extDiscount={"predebut": 0.35, "early": 0.45, "arb": 0.60, "vet": 0.90}),
    slot=[[1, 9.9], [2, 7.5], [3, 6.7], [5, 5.5], [8, 4.6], [12, 3.6], [17, 3.0], [22, 2.6],
          [30, 2.1], [45, 1.5], [65, 1.1], [90, 0.85], [120, 0.6], [200, 0.35], [400, 0.18], [620, 0.10]],
    vrank=[[1, 8.0], [3, 7.0], [5, 6.5], [10, 5.5], [15, 4.8], [25, 4.0], [40, 3.2], [50, 2.8], [75, 2.0], [100, 1.5]],
    teams=teams,
    deals=compact,
    book=book,
    payroll=payroll,
    cbt={"2026": 244, "2027": None},  # 2027+ awaits the next CBA
)
json.dump(out, open("/home/claude/desk_data.json", "w"), separators=(",", ":"))
import os
print("desk_data.json:", round(os.path.getsize("/home/claude/desk_data.json") / 1e6, 2), "MB")
