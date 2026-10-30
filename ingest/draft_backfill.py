"""Draft backfill 1998-2004 from the Stats API draft endpoint (verified: Pat
Burrell #1 in 1998). Inserts into draft_picks with the existing schema.
Idempotent: deletes those years first."""
import json, sqlite3, time, urllib.request

def get(u, tries=3):
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=40))
        except Exception: time.sleep(2 + 2*a)
    return {}

con = sqlite3.connect("/work/ledger.sqlite")
con.execute("delete from draft_picks where cast(year as int) between 1998 and 2004")
tot = 0
for yr in range(1998, 2005):
    d = get(f"https://statsapi.mlb.com/api/v1/draft/{yr}")
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
    con.executemany("insert into draft_picks values (?,?,?,?,?,?,?,?,?,?,?)", rows)
    tot += len(rows)
    print(yr, len(rows), "picks", flush=True)
con.commit()
print("TOTAL backfilled:", tot)
for r in con.execute("select year, round, pick_overall, person_name, team from draft_picks where cast(year as int)=2002 and cast(round as int)=1 and cast(pick_overall as int)<=3"):
    print(r)
