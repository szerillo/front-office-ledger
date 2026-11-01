"""Trade repair from the daily transaction feed (v5.1).

The team-level ingest only kept rows filed under the 30 MLB clubs. When a
trade's return was filed as minor-league affiliate moves ("Lakewood
BlueClaws traded C Travis d'Arnaud to Lansing Lugnuts; Toronto Blue Jays
traded RHP Roy Halladay to Philadelphia Phillies"), the return never reached
the ledger, and the seat that sent a star away read as getting nothing back.

For every trade seat in trade_book.json that has only an outflow or only an
inflow of material value, this pulls that day's full transaction list,
collects every row filed under the same trade description, maps each
affiliate to its parent club for that season (affiliates.json, from the
teams endpoint), and writes the missing rows to trade_repairs.json in the
sweep_tx row shape. tradegroup.dedupe_rows merges them per club and window.
"""
import json, os, time, urllib.request

ROOT = "/work"
CACHE = f"{ROOT}/tx_day_cache"
os.makedirs(CACHE, exist_ok=True)
cfg = json.load(open(f"{ROOT}/regimes.json"))
AFF = json.load(open(f"{ROOT}/affiliates.json"))
MLB_NAMES = set()
for r in cfg["regimes"]:
    MLB_NAMES.add(r["team"]); MLB_NAMES |= set(cfg["aliases"].get(str(r["teamId"]), []))
AB2NAMES = {r["abbr"]: ({r["team"]} | set(cfg["aliases"].get(str(r["teamId"]), []))) for r in cfg["regimes"]}

def parent(name, year):
    if not name: return None
    if name in MLB_NAMES: return name
    yrs = AFF.get(name)
    if not yrs: return None
    if str(year) in yrs: return yrs[str(year)]
    best = min(yrs, key=lambda y: abs(int(y) - year))
    return yrs[best]

def day(d):
    fn = f"{CACHE}/{d}.json"
    if os.path.exists(fn): return json.load(open(fn))
    for a in range(4):
        try:
            x = json.load(urllib.request.urlopen(urllib.request.Request(
                f"https://statsapi.mlb.com/api/v1/transactions?startDate={d}&endDate={d}",
                headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
            rows = [t for t in x.get("transactions", []) if t.get("typeCode") == "TR"]
            json.dump(rows, open(fn, "w")); time.sleep(0.15)
            return rows
        except Exception:
            time.sleep(1.5 + 2 * a)
    return []

tb = json.load(open(f"{ROOT}/trade_book.json"))
cands = []
for d, seats in tb["trades"]:
    for ab, net, ins, outs in seats:
        vin = sum(v for _, v in ins); vout = sum(v for _, v in outs)
        if (not ins and abs(vout) >= 0.5) or (not outs and abs(vin) >= 0.5):
            cands.append((d, ab, [p for p, _ in ins + outs]))
print("candidate seats:", len(cands))

repairs, seen = [], set()
for k, (d, ab, pids) in enumerate(cands):
    rows = day(d)
    descs = {t.get("description") for t in rows if str((t.get("person") or {}).get("id")) in pids}
    descs.discard(None)
    yr = int(d[:4])
    for t in rows:
        if t.get("description") not in descs: continue
        pid = str((t.get("person") or {}).get("id") or "")
        if not pid: continue
        fr = parent((t.get("fromTeam") or {}).get("name"), yr)
        to = parent((t.get("toTeam") or {}).get("name"), yr)
        if not fr or not to or fr == to: continue
        key = (d, pid, fr, to)
        if key in seen: continue
        seen.add(key)
        repairs.append(dict(date=d, person_id=pid, person_name=(t.get("person") or {}).get("fullName"),
                            from_team=fr, to_team=to, type_desc="Trade", description=t.get("description"),
                            repaired=True))
    if k % 200 == 0: print(" ", k, len(repairs), flush=True)
# cumulative: seats repaired by an earlier pass no longer show as candidates,
# so never drop rows an earlier pass found
old = json.load(open(f"{ROOT}/trade_repairs.json")) if os.path.exists(f"{ROOT}/trade_repairs.json") else []
keys = {(r["date"], r["person_id"], r["from_team"], r["to_team"]) for r in repairs}
repairs += [r for r in old if (r["date"], r["person_id"], r["from_team"], r["to_team"]) not in keys]
json.dump(repairs, open(f"{ROOT}/trade_repairs.json", "w"))
print("repair rows:", len(repairs))
