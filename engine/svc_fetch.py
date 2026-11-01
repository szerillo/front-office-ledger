"""Service time from the transaction feed (v5.1).

The desk pool's control math used to count MLB seasons with any appearance
(a cup of coffee read as a full year), which pushed 2022 debuts to 5 years of
service and priced their first arbitration award at the third-year ratio.
This reconstructs real MLB service (days on the active roster or the MLB
injured list during the championship season, 172 days = 1 year) from each
player's transaction history:

  on  : contract selected, recalled, claimed, MLB activation, MLB IL
        placement/transfer, major-league signing, Rule 5 selection
  off : optioned, outrighted, released, assigned to a minor-league club
        (rehab assignments excepted), minor-league signing
  keep: trades, DFA limbo (accrues), number changes, everything else

State carries across the winter, so a player who ends a season active and
is not optioned in camp starts the next season active. Each season's days
are scaled to a 186-day calendar (the 2020 60-game season and the 2022
lockout-shortened start were credited as full seasons) and capped at 172.

Writes service.json {pid: {"svc": years.days as float years, "by": {yr: days},
"arb_winters": [years the player was arbitration eligible]}} for every pool
player with MLB value since 2014. Validated against the curated SVC_FIX
truths and hand-counted cases (see tests).
"""
import json, os, time, urllib.request
from datetime import date, timedelta

ROOT = "/work"
CACHE = f"{ROOT}/svc_tx_cache.json"
MLB = {108,109,110,111,112,113,114,115,116,117,118,119,120,121,133,134,135,136,
       137,138,139,140,141,142,143,144,145,146,147,158}
SUPER2 = {2014: 2.133, 2015: 2.130, 2016: 2.131, 2017: 2.123, 2018: 2.122,
          2019: 2.115, 2020: 2.111, 2021: 2.116, 2022: 2.115, 2023: 2.128,
          2024: 2.116, 2025: 2.124, 2026: 2.124}   # approx. annual cutoffs; 2026 assumed

def get(u, tries=4):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception: time.sleep(1.5 + 2 * a)
    return None

# season calendars
SEAS = {}
for y in range(2012, 2027):
    d = get(f"https://statsapi.mlb.com/api/v1/seasons/{y}?sportId=1") or {}
    s = (d.get("seasons") or [{}])[0]
    a, b = s.get("regularSeasonStartDate"), s.get("regularSeasonEndDate")
    if a and b: SEAS[y] = (date.fromisoformat(a), date.fromisoformat(b))
print("season calendars:", len(SEAS), SEAS.get(2020), SEAS.get(2022))

# minor-league affiliates (AAA..Rookie, DSL), every season: events by these
# clubs mean the player is in the minors. Anything else that is not an MLB
# club (All-Star teams, Futures Game, WBC national teams, Fall League) is
# ignored, so an All-Star Game "activation" no longer reads as a demotion.
MINORS = set()
for y in range(2012, 2027):
    d = get(f"https://statsapi.mlb.com/api/v1/teams?sportIds=11,12,13,14,15,16&season={y}&fields=teams,id") or {}
    MINORS |= {t["id"] for t in d.get("teams", [])}
print("minor-league clubs:", len(MINORS))

def team_id(t):
    return (t or {}).get("id")

def classify(t, on):
    c = t.get("typeCode", ""); d = (t.get("description") or "").lower()
    to = team_id(t.get("toTeam")); to_mlb = to in MLB; to_minors = to in MINORS
    if c in ("NUM", "SGN"): return on            # draft/amateur signings never put a player on an MLB roster
    if "rehab" in d: return on                   # rehab assignments: still on the MLB injured list
    if c == "OPT": return False
    if c in ("OUT", "REL", "RET"): return False
    if c in ("SE", "CU"): return True
    if c in ("R5", "CLW"): return True if to_mlb else on
    if c == "SFA":
        if "minor league" in d: return False
        return True if to_mlb else on
    if c == "DES" or c == "TR": return on
    if c in ("ASG", "SC"):
        if to_minors:
            return False if (c == "ASG" or "activated" in d or "placed" in d or "injured list" in d) else on
        if not to_mlb: return on                 # All-Star, Futures, WBC, AFL: not a roster move
        if c == "ASG": return on                 # spring assignment to the big-league camp
        if "restricted list" in d and "placed" in d: return False
        if "injured list" in d and ("placed" in d or "transferred" in d): return True
        if "activated" in d or "reinstated" in d: return True
        if "reassigned" in d and "minor" in d: return False
        return on
    return on

def service(pid, txs):
    txs = sorted(txs, key=lambda t: t.get("date") or t.get("effectiveDate") or "")
    by = {}
    on = False
    i = 0
    for y in sorted(SEAS):
        a, b = SEAS[y]
        n_days = (b - a).days + 1
        days = 0
        # apply everything before opening day
        while i < len(txs) and (txs[i].get("date") or "") < a.isoformat():
            on = classify(txs[i], on); i += 1
        dd = a
        while dd <= b:
            ds = dd.isoformat()
            while i < len(txs) and (txs[i].get("date") or "") <= ds:
                on = classify(txs[i], on); i += 1
            if on: days += 1
            dd += timedelta(days=1)
        if days:
            by[y] = min(172, round(days * 186.0 / n_days))
    return by

def to_years(total_days):
    return total_days // 172 + (total_days % 172) / 1000.0

if __name__ == "__main__":
    desk = json.load(open(f"{ROOT}/desk_data.json"))
    lvm = json.load(open(f"{ROOT}/lvm_cache.json"))
    pool = []
    for p in desk["players"]:
        rec = lvm.get(str(p[1]))
        if not rec: continue
        yrs = [r[0] for r in rec["rows"]]
        if yrs and min(yrs) >= 2014: pool.append(p[1])
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [pid for pid in pool if str(pid) not in cache]
    print("pool:", len(pool), "| to fetch:", len(todo), flush=True)
    for k, pid in enumerate(todo):
        d = get(f"https://statsapi.mlb.com/api/v1/transactions?playerId={pid}")
        if d is None: continue
        cache[str(pid)] = [{"date": t.get("date"), "typeCode": t.get("typeCode"),
                            "description": t.get("description"),
                            "toTeam": {"id": team_id(t.get("toTeam"))},
                            "fromTeam": {"id": team_id(t.get("fromTeam"))}}
                           for t in d.get("transactions", [])]
        if k % 100 == 0:
            print(" ", k, flush=True); json.dump(cache, open(CACHE, "w"))
        time.sleep(0.12)
    json.dump(cache, open(CACHE, "w"))
    out = {}
    for pid in pool:
        txs = cache.get(str(pid))
        if txs is None: continue
        by = service(pid, txs)
        run = 0; arb = []
        for y in sorted(by):
            run += by[y]
            yrs = to_years(run)
            if 3.0 <= yrs < 6.0 or (2.0 <= yrs < 3.0 and yrs >= SUPER2.get(y, 2.125)):
                arb.append(y)
        out[str(pid)] = {"svc": round(to_years(run), 3), "by": by, "arb_winters": arb}
    json.dump(out, open(f"{ROOT}/service.json", "w"), separators=(",", ":"))
    print("service.json:", len(out))
