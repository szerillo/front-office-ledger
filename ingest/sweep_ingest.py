"""Full-league ingestion for the 30-regime sweep. Yearly chunks, resume-safe.
Writes to table `sweep_tx` (transactions tagged with the querying team_id)
and extends `draft_picks` back to 2005. Run: nohup python3 sweep_ingest.py &
"""
import json, sqlite3, sys, time, urllib.request
from datetime import date

UA = {"User-Agent": "FrontOfficeLedger-POC/0.1"}
API = "https://statsapi.mlb.com/api/v1"
END = "2026-07-21"

def get(url, retries=4):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception:
            if i == retries - 1: raise
            time.sleep(3 * (i + 1))

con = sqlite3.connect("ledger.sqlite")
con.execute("""CREATE TABLE IF NOT EXISTS sweep_tx (
  team_id INT, tx_id TEXT, date TEXT, type_desc TEXT, person_id TEXT,
  person_name TEXT, from_team TEXT, to_team TEXT, description TEXT)""")
con.execute("CREATE TABLE IF NOT EXISTS sweep_done (team_id INT, year INT, PRIMARY KEY(team_id, year))")
done = {(r[0], r[1]) for r in con.execute("select team_id, year from sweep_done")}

cfg = json.load(open("regimes.json"))
for reg in cfg["regimes"]:
    tid = reg["teamId"]
    y0 = max(int(reg["start"][:4]), 2005)
    for yr in range(y0, 2027):
        if (tid, yr) in done: continue
        s = max(reg["start"], f"{yr}-01-01") if yr == y0 else f"{yr}-01-01"
        e = min(END, f"{yr}-12-31")
        if s > e: continue
        try:
            d = get(f"{API}/transactions?startDate={s}&endDate={e}&teamId={tid}")
        except Exception as ex:
            print(f"FAIL {reg['abbr']} {yr}: {ex}", flush=True); continue
        rows = [(tid, t.get("id"), t.get("date"), t.get("typeDesc"),
                 (t.get("person") or {}).get("id"), (t.get("person") or {}).get("fullName"),
                 (t.get("fromTeam") or {}).get("name"), (t.get("toTeam") or {}).get("name"),
                 t.get("description")) for t in d.get("transactions", [])]
        con.executemany("INSERT INTO sweep_tx VALUES (?,?,?,?,?,?,?,?,?)", rows)
        con.execute("INSERT OR REPLACE INTO sweep_done VALUES (?,?)", (tid, yr))
        con.commit()
        print(f"{reg['abbr']} {yr}: {len(rows)} rows", flush=True)

# extend drafts back to 2005
have = {int(r[0]) for r in con.execute("select distinct year from draft_picks")}
for yr in range(2005, 2019):
    if yr in have: continue
    try:
        d = get(f"{API}/draft/{yr}")
    except Exception as ex:
        print(f"DRAFT FAIL {yr}: {ex}", flush=True); continue
    rows = []
    for rnd in d["drafts"]["rounds"]:
        for p in rnd.get("picks", []):
            per = p.get("person") or {}
            rows.append((str(yr), p.get("pickRound"), p.get("pickNumber"), p.get("roundPickNumber"),
                         per.get("id"), per.get("fullName"), (p.get("team") or {}).get("name"),
                         p.get("isPass") is False and bool(p.get("signingBonus")),
                         p.get("signingBonus"), p.get("pickValue"), (p.get("school") or {}).get("name")))
    con.executemany("INSERT INTO draft_picks VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    print(f"draft {yr}: {len(rows)} picks", flush=True)
print("SWEEP INGEST COMPLETE", flush=True)
