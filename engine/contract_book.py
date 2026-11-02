"""
CONTRACT BOOK (v5.8): one table of every guaranteed contract the ledger
knows, resolved to player ids, with the seasons each contract OWNS.

Sources: free-agent deals 1997-2005 (research/fa_1997_2005.csv, news lists
and ESPN charts), 2006-21 (ESPN tables, contracts_espn.csv), 2022-25
(contracts_recent.RECENT); extensions 1998-2014 (research/ext_1998_2014.csv,
MLB Trade Rumors' extension tracker and reports) and 2015-26
(contracts_ext.EXT).

The ownership rule ("a later contract owns its seasons"): when a player
signs a new deal (an extension, a re-signing, a free-agent deal elsewhere),
the seasons it covers belong to that decision. An earlier contract stops at
the season before, and no value window from an earlier decision (a draft
pick's control years, a trade's control window) runs into them. This is
what keeps a season from being graded twice.

Also measured here, once, for every channel that prices money: the TYPICAL
RETURN on free-agent money by contract year (wins produced on the signing
club per win of cost at market $/win, pooled over every priced deal by every
club). Early contract years return more than late ones (aging), so an
in-progress deal is judged against the years it has actually played.

Writes contract_book.json; run before every scorer (chain step 0).
"""
import csv, json, sys, unicodedata
from collections import defaultdict
sys.path.insert(0, "/work")
from contracts_recent import RECENT
from contracts_ext import EXT, FA_CBT

ROOT = "/work"
LVM = {int(k): v for k, v in json.load(open(f"{ROOT}/lvm_cache.json")).items() if not k.startswith("__")}
# homegrown stars never touched by a graded transaction live in the extension cache
import os as _os
if _os.path.exists(f"{ROOT}/ext_lvm_cache.json"):
    for _k, _v in json.load(open(f"{ROOT}/ext_lvm_cache.json")).items():
        if not str(_k).startswith("__") and int(_k) not in LVM and _v.get("rows"): LVM[int(_k)] = _v
cfg = json.load(open(f"{ROOT}/regimes.json"))
NAMES = {r["abbr"]: set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in cfg["regimes"]}

# $ per win by season. 2006-26: the published curve the whole site uses.
# 1997-2005: scaled from 2006 by MLB's average opening-day payroll (about
# $42M in 1998 rising to $77M in 2006), the only consistent public series.
DPW = {2006: 4.2, 2007: 4.5, 2008: 4.7, 2009: 4.7, 2010: 5.0, 2011: 5.2, 2012: 5.5, 2013: 6.0,
       2014: 6.5, 2015: 7.0, 2016: 7.7, 2017: 8.0, 2018: 8.2, 2019: 8.0, 2020: 8.0, 2021: 8.5,
       2022: 8.5, 2023: 9.0, 2024: 9.3, 2025: 9.5, 2026: 9.7, 2027: 10.0}
_PAY = {1997: 40.0, 1998: 42.1, 1999: 48.0, 2000: 51.5, 2001: 65.4, 2002: 67.5, 2003: 70.9, 2004: 68.9, 2005: 72.8}
for _y, _p in _PAY.items(): DPW[_y] = round(4.2 * _p / 77.0, 2)
def dpw(y): return DPW.get(y, DPW[2027] if y > 2027 else DPW[1997])
LEAGUE_MIN = 0.75

def norm(nm):
    x = unicodedata.normalize("NFKD", nm or "").encode("ascii", "ignore").decode()
    return x.lower().replace(".", "").replace(" jr", "").replace(" sr", "").replace(" ii", "").replace(" iii", "").strip()

NAME2PIDS = defaultdict(list)
for pid, rec in LVM.items():
    NAME2PIDS[norm(rec.get("name", ""))].append(pid)

def resolve(name, ab, start):
    """the player id: by name, preferring the candidate who played for the
    club around the contract's start, then the one most active then"""
    c = NAME2PIDS.get(norm(name), [])
    if len(c) <= 1: return c[0] if c else None
    names = NAMES.get(ab, set())
    def score(pid):
        rows = LVM[pid]["rows"]
        near = [r for r in rows if start - 2 <= r[0] <= start + 1]
        return (sum(1 for r in near if r[1] in names), sum(abs(r[2]) for r in near))
    return max(c, key=score)

raw = []   # (kind, sign 'YYYY-MM', start season, player, abbr, yrs, total, src)
for row in csv.DictReader(open(f"{ROOT}/research/fa_1997_2005.csv")):
    o = int(row["offseason"])
    raw.append(("fa", f"{o}-12", o + 1, row["player"], row["team"], int(row["years"]), float(row["total_m"]), "fa97"))
_short = {}
for r in cfg["regimes"]:
    for nm in NAMES[r["abbr"]]: _short[nm] = r["abbr"]
def short_to_ab(short):
    for ab, nms in NAMES.items():
        if any(short and short.lower() in nm.lower() for nm in nms): return ab
    return None
for row in csv.DictReader(open(f"{ROOT}/repo/data/contracts_espn.csv")):
    ab = short_to_ab(row["to_team"])
    if ab:
        o = int(row["offseason"])
        raw.append(("fa", f"{o}-12", o + 1, row["player"], ab, int(row["years"]), float(row["total_m"]), "espn"))
for o, pl, ab, yrs, tot in RECENT:
    tot = FA_CBT.get((norm(pl), o), tot)          # present (CBT) value where deferrals diverge (Ohtani)
    raw.append(("fa", f"{o}-12", o + 1, pl, ab, yrs, float(tot), "recent"))
_ext_seen = set()
for e in EXT:
    sign, pl, ab, yrs, tot, cbt = e[:6]
    if sign >= "2026-10": continue                 # 2027 option rows: payroll only
    y, m = int(sign[:4]), int(sign[5:7])
    start = e[6] if len(e) > 6 else (y if m <= 3 else y + 1)
    raw.append(("ext", sign, start, pl, ab, yrs, float(cbt if cbt else tot), "ext"))
    _ext_seen.add((norm(pl), y))
for row in csv.DictReader(open(f"{ROOT}/research/ext_1998_2014.csv")):
    y = int(row["date"][:4])
    if (norm(row["player"]), y) in _ext_seen: continue
    raw.append(("ext", row["date"][:7], int(row["first_season"]), row["player"], row["team"],
                int(row["years"]), float(row["total_m"]), "ext98"))

# contracts signed before 1998 that still covered 1998 or later (Sheffield's
# 1997 extension, Belle, Bonds...): research/contracts_pre1998.csv
import os as _os2
if _os2.path.exists(f"{ROOT}/research/contracts_pre1998.csv"):
    for row in csv.DictReader(open(f"{ROOT}/research/contracts_pre1998.csv")):
        try:
            raw.append((row["kind"].strip(), row["date"][:7], int(row["first_season"]), row["player"], row["team"].strip(),
                        int(row["years"]), float(row["total_m"]), "pre98"))
        except Exception: pass
book = []
seen = set()
for kind, sign, start, pl, ab, yrs, tot, src in raw:
    if ab not in NAMES or yrs < 1: continue
    pid = resolve(pl, ab, start)
    if pid is None: continue
    k = (pid, start, ab, kind)
    if k in seen: continue
    seen.add(k)
    book.append(dict(pid=pid, name=pl, club=ab, kind=kind, sign=sign, start=start, yrs=yrs, tot=round(tot, 3),
                     aav=round(tot / yrs, 3), src=src))

# ownership: each season belongs to the latest-signed contract covering it
by_pid = defaultdict(list)
for c in book: by_pid[c["pid"]].append(c)
for pid, cs in by_pid.items():
    cs.sort(key=lambda c: (c["sign"], c["start"]))
    for i, c in enumerate(cs):
        later = [d for d in cs[i + 1:] if d["sign"] > c["sign"]]
        cut = min([d["start"] for d in later if d["start"] <= c["start"] + c["yrs"] - 1] or [c["start"] + c["yrs"]])
        c["own"] = list(range(c["start"], max(c["start"], cut)))

# typical return on free-agent money by contract year. A season counts on
# the signing club while he is there. If the club trades him, the contract
# leaves with him (the trade grades the rest, salary included) and the
# trade season is prorated; if the club releases him, it keeps paying and
# keeps being charged (dead money). Pooled over every priced deal by every
# club, 2006-26 seasons (the published $/win era).
import sqlite3
_con = sqlite3.connect(f"{ROOT}/ledger.sqlite")
TRADED = defaultdict(list)
for _pid, _d, _ft in _con.execute("select person_id, date, from_team from sweep_tx where type_desc='Trade' and person_id is not null"):
    TRADED[int(_pid)].append((_d, _ft))
def traded_away(pid, ab, after):
    """first season in which the club traded him away after `after` (YYYY-MM)"""
    ds = [d for d, ft in TRADED.get(pid, []) if ft in NAMES[ab] and d[:7] > after]
    return int(min(ds)[:4]) if ds else None
def season_rows(pid, ab, y):
    rows = [r for r in LVM[pid]["rows"] if r[0] == y]
    here = [r for r in rows if r[1] in NAMES[ab]]
    return sum(r[2] for r in here), (len(here) / len(rows) if rows else 0.0)
def club_seasons(c, through=2026):
    """[(contract-year k, season, wins on club, cost share)] for the seasons the
    signing club holds the contract"""
    out = []
    ty = traded_away(c["pid"], c["club"], c["sign"])
    for k, y in enumerate(c["own"], 1):
        if y > through: break
        if ty is not None and y > ty: break
        w, share = season_rows(c["pid"], c["club"], y)
        out.append((k, y, w, share if (ty is not None and y == ty) else 1.0))
    return out
for c in book:
    c["held"] = [[k, y, round(w, 2), round(sh, 2)] for k, y, w, sh in club_seasons(c)]
def ratio(pred, dp):
    acc = defaultdict(lambda: [0.0, 0.0])
    for c in book:
        if c["kind"] != "fa": continue
        for k, y, w, sh in c["held"]:
            if not pred(y): continue
            a = acc[min(k, 5)]; a[0] += w; a[1] += max(0.0, c["aav"] - LEAGUE_MIN) / dp(y) * sh
    return acc
acc = ratio(lambda y: y >= 2006, dpw)
TYPICAL_FA = {k: round(a[0] / a[1], 3) for k, a in sorted(acc.items()) if a[1] > 0}
TYPICAL_FA_ALL = round(sum(a[0] for a in acc.values()) / sum(a[1] for a in acc.values()), 3)
# pre-2006: $/win has no consistent published series (the payroll-scaled
# estimate above) and the 1997-2005 deal lists over-represent big deals, so
# those seasons are judged against their own era's typical return: the
# 2006-26 curve times the pre-2006 pooled ratio (ERA_ADJ_PRE2006).
pre = ratio(lambda y: y < 2006, dpw)
_pw, _pc = sum(a[0] for a in pre.values()), sum(a[1] for a in pre.values())
ERA_ADJ = round((_pw / _pc) / TYPICAL_FA_ALL, 3) if _pc else 1.0
print(f"pre-2006 typical return is {ERA_ADJ}x the 2006-26 curve")
def typical(k, y):
    """typical wins back per win of market cost, contract year k, season y"""
    r = TYPICAL_FA.get(min(k, 5), TYPICAL_FA_ALL)
    return r * (ERA_ADJ if y < 2006 else 1.0)

json.dump(dict(book=book, dpw={str(k): v for k, v in sorted(DPW.items())}, league_min=LEAGUE_MIN,
               typical_fa=TYPICAL_FA, typical_fa_all=TYPICAL_FA_ALL, era_adj_pre2006=ERA_ADJ,
               counts={"fa": sum(1 for c in book if c["kind"] == "fa"), "ext": sum(1 for c in book if c["kind"] == "ext")}),
          open(f"{ROOT}/contract_book.json", "w"), separators=(",", ":"))
print(f"contract book: {len(book)} contracts resolved of {len(raw)} "
      f"(fa {sum(1 for c in book if c['kind']=='fa')}, ext {sum(1 for c in book if c['kind']=='ext')})")
print("typical FA return by contract year:", TYPICAL_FA, "| pooled", TYPICAL_FA_ALL)
