# Production-shaped sweep_tx (ingest/sweep_ingest.py logic: per club, per year, rows tagged with the querying club,
# tx_id, from_team and to_team names). END matches the frozen ledger's last date. Raw responses saved for the record.
import json, sqlite3, time, urllib.request, os, hashlib
API="https://statsapi.mlb.com/api/v1"; END="2026-11-10"; UA={"User-Agent":"FrontOfficeLedger-POC/0.1"}
os.makedirs("/tmp/v2/raw", exist_ok=True)
def get(u):
    p="/tmp/v2/raw/"+hashlib.sha256(u.encode()).hexdigest()
    if os.path.exists(p): return json.load(open(p))
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40) as r: b=r.read()
            open(p,"wb").write(b); open(p+".url","w").write(u); return json.loads(b)
        except Exception as e:
            if i==3: raise
            time.sleep(3*(i+1))
con=sqlite3.connect("/tmp/v2/ledger_v2.sqlite")
con.execute("CREATE TABLE IF NOT EXISTS sweep_tx (team_id INT, tx_id TEXT, date TEXT, type_desc TEXT, person_id TEXT, person_name TEXT, from_team TEXT, to_team TEXT, description TEXT)")
con.execute("CREATE TABLE IF NOT EXISTS sweep_done (team_id INT, year INT, PRIMARY KEY(team_id, year))")
done={(r[0],r[1]) for r in con.execute("select team_id, year from sweep_done")}
cfg=json.load(open("/work/regimes.json")); fails=0
for reg in cfg["regimes"]:
    tid=reg["teamId"]; y0=2005
    for yr in range(y0,2027):
        if (tid,yr) in done: continue
        s=f"{yr}-01-01"; e=min(END,f"{yr}-12-31")
        if s>e: continue
        try: d=get(f"{API}/transactions?startDate={s}&endDate={e}&teamId={tid}")
        except Exception as ex: print("FAIL",reg["abbr"],yr,ex,flush=True); fails+=1; continue
        rows=[(tid,t.get("id"),t.get("date"),t.get("typeDesc"),(t.get("person") or {}).get("id"),(t.get("person") or {}).get("fullName"),
               (t.get("fromTeam") or {}).get("name"),(t.get("toTeam") or {}).get("name"),t.get("description")) for t in d.get("transactions",[])]
        con.executemany("INSERT INTO sweep_tx VALUES (?,?,?,?,?,?,?,?,?)",rows); con.execute("INSERT OR REPLACE INTO sweep_done VALUES (?,?)",(tid,yr)); con.commit()
        print(reg["abbr"],yr,len(rows),flush=True)
print("PULL DONE fails",fails,flush=True)
