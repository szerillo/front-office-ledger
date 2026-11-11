# Fetch draft years 1998-2026 once (network allowed here), save raw JSON, and build draft_picks in a frozen ledger
# with the tuple layout sweep_ingest.py / draft_backfill.py use.
import json, sqlite3, shutil, urllib.request, time, hashlib
shutil.copy('/tmp/sweep/ledger_r.sqlite', 'ledger_frozen.sqlite')
con = sqlite3.connect('ledger_frozen.sqlite')
con.execute("create table draft_picks (year, round, pick_overall, round_pick, person_id, person_name, team, signed, bonus, pick_value, school)")
tot = 0
for yr in range(1998, 2027):
    raw = urllib.request.urlopen(urllib.request.Request(f"https://statsapi.mlb.com/api/v1/draft/{yr}", headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    open(f'draft_{yr}.json', 'wb').write(raw); d = json.loads(raw)
    rows = []
    for rnd in d["drafts"]["rounds"]:
        for p in rnd.get("picks", []):
            per = p.get("person") or {}
            rows.append((str(yr), p.get("pickRound"), p.get("pickNumber"), p.get("roundPickNumber"),
                         per.get("id"), per.get("fullName"), (p.get("team") or {}).get("name"),
                         p.get("isPass") is False and bool(p.get("signingBonus")),
                         p.get("signingBonus"), p.get("pickValue"), (p.get("school") or {}).get("name")))
    con.executemany("insert into draft_picks values (?,?,?,?,?,?,?,?,?,?,?)", rows); tot += len(rows)
    time.sleep(0.3)
con.commit(); print("draft rows", tot)
