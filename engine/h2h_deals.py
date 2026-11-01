"""Per-pair deal lists for the Head-to-Head tab: merges a 'deals' array into
each sweep_results h2h entry (date, short headline, net from this seat).
Standalone and idempotent; touches nothing else."""
import json, sqlite3
from collections import defaultdict
from tradegroup import dedupe_rows, group_trades

cfg = json.load(open("/work/regimes.json"))

def club_names(team):
    """v5.1: every name a club has gone by (Indians/Guardians, Oakland
    Athletics/Athletics, Marlins, Expos/Nationals...). Valuing a departed
    piece on the single name in the transaction row closed his window at the
    club's rename, so the two seats of one trade stopped mirroring."""
    for _r in cfg["regimes"]:
        _al = set(cfg["aliases"].get(str(_r["teamId"]), [])) | {_r["team"]}
        if team in _al: return _al
    return {team}
LVM = {k: v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
NAME2TID = {}
for r in cfg["regimes"]:
    NAME2TID[r["team"]] = r["teamId"]
    for al in cfg["aliases"].get(str(r["teamId"]), []):
        NAME2TID[al] = r["teamId"]
con = sqlite3.connect("/work/ledger.sqlite"); con.row_factory = sqlite3.Row

def val_control(pid, teams, y0, cap=6):
    rec = LVM.get(str(pid))
    if not rec: return 0.0
    byyear = defaultdict(list)
    for y, tm, v in rec["rows"]: byyear[y].append((tm, v))
    tot = 0.0
    for y in range(y0, y0 + cap):
        rows = byyear.get(y, [])
        here = [v for (tm, v) in rows if tm in teams]
        if rows and not here and y > y0: break
        tot += sum(here)
    return tot

pair_deals = defaultdict(list)   # (tid, opp) -> [{d, h, net}]
seen = set()
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    start = max(reg["start"], "2005-01-01")
    _rows = dedupe_rows([dict(r) for r in con.execute("select * from sweep_tx where team_id=? and date>=? and type_desc='Trade'", (tid, start))], tid, start)
    for (d, desc, rs) in group_trades(_rows, names):
        yr = int(d[:4])
        opps = {NAME2TID.get(x["to_team"]) for x in rs if x["from_team"] in names and x["to_team"]} | \
               {NAME2TID.get(x["from_team"]) for x in rs if x["to_team"] in names and x["from_team"]}
        opps = {o for o in opps if o and o != tid}
        for opp in opps:
            if d < REG[opp]["start"]: continue
            key = (tid, opp, d, desc)
            if key in seen: continue
            seen.add(key)
            got = [x for x in rs if x["to_team"] in names and x["person_id"] and NAME2TID.get(x["from_team"]) == opp]
            gave = [x for x in rs if x["from_team"] in names and x["person_id"] and NAME2TID.get(x["to_team"]) == opp]
            vin = sum(val_control(x["person_id"], names, yr) for x in got)
            vout = sum(val_control(x["person_id"], club_names(x["to_team"]), yr) for x in gave)
            gn = ", ".join(dict.fromkeys(x["person_name"] for x in got if x["person_name"])) or "cash/PTBNL"
            vn = ", ".join(dict.fromkeys(x["person_name"] for x in gave if x["person_name"])) or "cash/PTBNL"
            pair_deals[(tid, opp)].append(dict(d=d, h=f"Got {gn} for {vn}", net=round(vin - vout, 1)))

res = json.load(open("/work/sweep_results.json"))
AB2TID = {r["abbr"]: r["teamId"] for r in cfg["regimes"]}
merged = 0
for r in res:
    for p in r.get("h2h", []):
        key = (r["teamId"], AB2TID.get(p["opp"]))
        deals = sorted(pair_deals.get(key, []), key=lambda x: x["d"], reverse=True)[:60]
        p["deals"] = deals
        merged += len(deals)
json.dump(res, open("/work/sweep_results.json", "w"), indent=1)
print("pair deal lines merged:", merged)
