"""Every trade, both seats (v5.1).

The report cards carry each regime's best and worst decisions, which left most
trades in a player's career ungraded when the Trees finder walked it. This
grades EVERY trade in the feed (1998-2026) from every participating club's
seat with the exact engine math (sweep_score / hist_score val_control:
control-window value, win-curve leverage, 10%/yr discount, 6-season cap),
and cross-checks itself against every trade decision already on a card.

Writes trade_book.json:
  {"trades": [[date, [[ab, net, [[pid, v], ...in], [[pid, v], ...out]], ...]], ...],
   "names": {pid: name}, "check": {...}}
"""
from asset_rules import contract_cost, trade_window
import json, math, sqlite3, time, urllib.request
from collections import defaultdict

ROOT = "/work"
LVM = {int(k): v for k, v in json.load(open(f"{ROOT}/lvm_cache.json")).items() if not k.startswith("__")}
cfg = json.load(open(f"{ROOT}/regimes.json"))

def club_names(team):
    """v5.1: every name a club has gone by (Indians/Guardians, Oakland
    Athletics/Athletics, Marlins, Expos/Nationals...). Valuing a departed
    piece on the single name in the transaction row closed his window at the
    club's rename, so the two seats of one trade stopped mirroring."""
    for _r in cfg["regimes"]:
        _al = set(cfg["aliases"].get(str(_r["teamId"]), [])) | {_r["team"]}
        if team in _al: return _al
    return {team}
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
TID2AB = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
NAME2TID = {}
for r in cfg["regimes"]:
    NAME2TID[r["team"]] = r["teamId"]
    for al in ALIAS.get(r["teamId"], set()):
        NAME2TID[al] = r["teamId"]

def get(u, tries=4):
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
        except Exception: time.sleep(1.5 + 2 * a)
    return {}

wl = {}
for yr in range(1998, 2027):
    d = get(f"https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season={yr}&standingsTypes=regularSeason")
    for g in d.get("records", []):
        for t in g.get("teamRecords", []):
            wl[(t["team"]["id"], yr)] = [t.get("wins", 0), t.get("losses", 0)]

def lev(teams, yr):
    tids = {NAME2TID.get(n) for n in teams} - {None}
    tid = next(iter(tids), None)
    rec = wl.get((tid, yr)) if tid else None
    if not rec or (rec[0] + rec[1]) < 100: return 1.0
    w = rec[0] * 162 / (rec[0] + rec[1])
    return 0.5 + 1.3 * math.exp(-((w - 89) ** 2) / 200.0)

def val_control(pid, teams, y0, cap=6, date=None, sender=None):
    """v5.8: asset accounting (asset_rules.trade_window), the same function
    every scorer uses"""
    return trade_window(pid, teams, date or f"{y0}-07-01", lev=lev, cap=cap, sender=sender)[0]

con = sqlite3.connect(f"{ROOT}/ledger.sqlite"); con.row_factory = sqlite3.Row
from tradegroup import dedupe_rows, group_trades
names = {}
names_arch = {}
names_feedonly = {}
seat_groups = []     # (tid, d, rows, base keys)
for r in cfg["regimes"]:
    tid = r["teamId"]
    nm = ALIAS.get(tid, set()) | {r["team"]}
    rows = dedupe_rows([dict(x) for x in con.execute(
        "select * from sweep_tx where team_id=? and date>='1998-01-01' and type_desc='Trade' "
        "order by date, tx_id, person_id, description, from_team, to_team", (tid,))], tid, "1998-01-01")   # fix pass 1: later rows win, so the name is the latest one
    for x in rows:   # rule 12b (amendment 3): the Retrosheet archive spelling when an archive row exists, else the latest feed name
        if not x["person_id"]: continue
        _arch = str(x.get("tx_id") or "").startswith("retro-") or (x.get("description") or "").endswith("(Retrosheet archive)")
        (names if _arch else names_feedonly)[str(x["person_id"])] = x["person_name"]
    for (d, desc, rs) in group_trades(rows, nm):
        seat_groups.append((tid, d, rs, {(x["date"], x["description"]) for x in rs}))
# a trade = every seat group linked through a shared (date, description) filing
parent = {}
def find(k):
    parent.setdefault(k, k)
    while parent[k] != k:
        parent[k] = parent[parent[k]]; k = parent[k]
    return k
for (_, _, _, keys) in seat_groups:
    ks = list(keys)
    for k in ks[1:]: parent[find(ks[0])] = find(k)
    find(ks[0])
# v5.8: also link seat groups of different clubs that exchange the same
# player within three days (a three-team deal or a flip filed as separate
# transactions), so no club's half of a deal stands alone
from datetime import date as _date
def _dd(a, b): return abs((_date.fromisoformat(a[:10]) - _date.fromisoformat(b[:10])).days)
_by_pid = defaultdict(list)
for i, (tid, d, rs, keys) in enumerate(seat_groups):
    for x in rs:
        if x["person_id"] and str(x["person_id"]) != "0": _by_pid[str(x["person_id"])].append((x["date"], tid, next(iter(keys))))
for pid, occ in _by_pid.items():
    for i in range(len(occ)):
        for j in range(i + 1, len(occ)):
            if occ[i][1] != occ[j][1] and _dd(occ[i][0], occ[j][0]) <= 3:
                parent[find(occ[i][2])] = find(occ[j][2])
trades = defaultdict(list)
for sg in seat_groups:
    trades[find(next(iter(sg[3])))].append(sg)
out = []
for root, sgs in trades.items():
    d = min(sg[1] for sg in sgs if sg[1])
    yr = int(d[:4])
    row = []
    for tid, _, rs, _ in sgs:
        nm = ALIAS.get(tid, set()) | {next(r["team"] for r in cfg["regimes"] if r["teamId"] == tid)}
        ins = {x["person_id"] for x in rs if x["to_team"] in nm and x["person_id"] and str(x["person_id"]) != "0"}
        outs = {x["person_id"]: x["to_team"] for x in rs if x["from_team"] in nm and x["person_id"] and str(x["person_id"]) != "0" and x["to_team"]}
        ins_from = {x["person_id"]: x["from_team"] for x in rs if x["to_team"] in nm and x["person_id"]}
        idet = [[str(p), round(val_control(p, nm, yr, date=d, sender=club_names(ins_from.get(p, ""))), 1)] for p in sorted(ins, key=str)]
        odet = [[str(p), round(val_control(p, club_names(dest), yr, date=d, sender=nm), 1)] for p, dest in sorted(outs.items(), key=lambda kv: str(kv[0]))]
        if not idet and not odet: continue
        idet.sort(key=lambda t: (-t[1], -int(t[0]))); odet.sort(key=lambda t: (-t[1], -int(t[0])))   # rule 12a: value, then higher id
        net = sum(v for _, v in idet) - sum(v for _, v in odet)
        row.append([TID2AB.get(tid, "?"), round(net, 1), idet, odet])
    row.sort(key=lambda s: s[0])
    if row: out.append([d, row])
out.sort(key=lambda t: (t[0], json.dumps(t[1])))   # fix pass 1: same-day trades in a fixed order

# self-check against every trade decision already graded on a card
def card_trades():
    rows = []
    for fn in ("sweep_results.json", "hist_results.json"):
        for r in json.load(open(f"{ROOT}/{fn}")):
            ab = r.get("abbr") or TID2AB.get(r.get("teamId"))
            for side in ("best", "worst"):
                for x in (r.get("led", {}).get("trade", {}) or {}).get(side, []):
                    rows.append((ab, x["d"][:10], x["net"], fn))
            for x in r.get("top", []):
                if x.get("ch") == "trade": rows.append((ab, x["d"][:10], x["net"], fn))
    return rows
idx = defaultdict(list)
for d, row in out:
    for ab, net, _, _ in row: idx[(ab, d)].append(net)
chk = card_trades(); match = miss = 0; bad = []
for ab, d, net, fn in chk:
    cands = idx.get((ab, d), [])
    if any(abs(c - net) <= 0.15 for c in cands): match += 1
    else:
        miss += 1
        if len(bad) < 15: bad.append((ab, d, net, cands, fn))
print(f"trades graded: {len(out)} | card cross-check: {match} match, {miss} differ")
for b in bad: print("  differ:", b)
# rule 12b (amendment 5): the name the live site shows today (names_pinned.json), else the latest feed name, else the archive spelling
import os as _os
_PIN = json.load(open("/work/names_pinned.json", encoding="utf-8")) if _os.path.exists("/work/names_pinned.json") else {}
names = {_k: (_PIN.get(_k) or names_feedonly.get(_k) or names[_k]) for _k in names} | {_k: (_PIN.get(_k) or _v) for _k, _v in names_feedonly.items() if _k not in names}
json.dump({"trades": out, "names": names, "check": {"match": match, "differ": miss}},
          open(f"{ROOT}/trade_book.json", "w"), separators=(",", ":"))
import os
print("trade_book.json:", round(os.path.getsize(f"{ROOT}/trade_book.json") / 1e6, 2), "MB")
