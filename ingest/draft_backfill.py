"""Draft backfill 1998-2004 from the Stats API draft endpoint (verified: Pat
Burrell #1 in 1998). Inserts into draft_picks with the existing schema.
Idempotent: replaces those years.

Nov 11 fix: every year is fetched first. If any fetch fails or a year comes back with
no picks, the script exits with an error and the ledger is not touched. Only when all
seven years are in hand are the old rows deleted and the new ones inserted, in one
transaction (a failure part way rolls back)."""
import json, sqlite3, sys, time, urllib.request

DB = sys.argv[1] if len(sys.argv) > 1 else "/work/ledger.sqlite"
API = "https://statsapi.mlb.com/api/v1/draft/{}"

def get(u, tries=3):
    last = None
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
        except Exception as e:
            last = e; time.sleep(2 + 2 * a)
    raise RuntimeError(f"fetch failed after {tries} tries: {u}: {last}")

def year_rows(yr):
    d = get(API.format(yr))
    rows = []
    for rnd in d.get("drafts", {}).get("rounds", []):
        for p in rnd.get("picks", []):
            per = p.get("person") or {}
            tm = (p.get("team") or {}).get("name")
            if not tm: continue
            rows.append((str(yr), str(p.get("pickRound", rnd.get("round", ""))),
                         str(p.get("pickNumber", "")), str(p.get("roundPickNumber", "")),
                         str(per.get("id")) if per.get("id") else None, per.get("fullName"),
                         tm, str(p.get("isDrafted", "")), str(p.get("signingBonus", "") or ""),
                         str(p.get("pickValue", "") or ""), (p.get("school") or {}).get("name", "")))
    return rows

# 1. fetch everything first; any failure stops here with the ledger untouched
fetched = {}
try:
    for yr in range(1998, 2005):
        rows = year_rows(yr)
        if not rows: raise RuntimeError(f"draft {yr}: the API returned no picks")
        fetched[yr] = rows
        print(yr, len(rows), "picks fetched", flush=True)
except Exception as e:
    print("DRAFT BACKFILL FAILED, ledger not changed:", e, file=sys.stderr, flush=True)
    sys.exit(2)

# 2. replace the seven years in one transaction
con = sqlite3.connect(DB)
try:
    with con:
        con.execute("delete from draft_picks where cast(year as int) between 1998 and 2004")
        for yr in sorted(fetched):
            con.executemany("insert into draft_picks values (?,?,?,?,?,?,?,?,?,?,?)", fetched[yr])
except Exception as e:
    print("DRAFT BACKFILL FAILED in the write, rolled back:", e, file=sys.stderr, flush=True)
    sys.exit(3)
print("TOTAL backfilled:", sum(len(v) for v in fetched.values()))
for r in con.execute("select year, round, pick_overall, person_name, team from draft_picks where cast(year as int)=2002 and cast(round as int)=1 and cast(pick_overall as int)<=3"):
    print(r)
