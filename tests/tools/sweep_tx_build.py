"""NOTE (round 19): the MLB feed is nearly empty before 2009. After this script, run ingest/retro_backfill.py on the
same database (point its sqlite path there) or 1998-2008 signings vanish from every rerun."""
"""Rebuilds the sweep_tx table (date, team_id, person_id, person_name, type_desc, description) from the public
MLB transactions feed into /tmp/sweep/ledger.sqlite, so fa_grade.py can run without the original ledger.
Round 17: with it, fa_grade.py reproduces 646 of 646 overlapping published signing grades exactly."""
import json,sqlite3,urllib.request,sys,time
con=sqlite3.connect('/tmp/sweep/ledger.sqlite')
con.execute('create table if not exists sweep_tx(date text, team_id int, person_id int, person_name text, type_desc text, description text)')
for y in range(1997,2027):
  for a,b in ((f'{y}-01-01',f'{y}-06-30'),(f'{y}-07-01',f'{y}-12-31')):
    u=f'https://statsapi.mlb.com/api/v1/transactions?sportId=1&startDate={a}&endDate={b}'
    for t in range(3):
      try: d=json.load(urllib.request.urlopen(u,timeout=120)); break
      except Exception as e: time.sleep(3); d=None
    if not d: print('fail',a); continue
    rows=[(x.get('date') or x.get('effectiveDate'), (x.get('toTeam') or {}).get('id'), (x.get('person') or {}).get('id'), (x.get('person') or {}).get('fullName'), x.get('typeDesc'), x.get('description','')) for x in d.get('transactions',[])]
    con.executemany('insert into sweep_tx values (?,?,?,?,?,?)',rows); con.commit()
  print(y, con.execute('select count(*) from sweep_tx').fetchone()[0], flush=True)
