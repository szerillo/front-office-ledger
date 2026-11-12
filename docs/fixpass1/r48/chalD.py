# Round 48 challenge D: does a Rule 5 pick returned in spring leave the counter "on"? 10 spring returns, seeded draw.
import json, sqlite3, random, urllib.request, importlib.util, time
spec = importlib.util.spec_from_file_location('sf', '/tmp/r48/eng/svc_fetch.py'); SF = importlib.util.module_from_spec(spec); spec.loader.exec_module(SF)
db = sqlite3.connect('/tmp/v2/ledger_v3.sqlite')
rows = db.execute("select distinct date, person_id, person_name from sweep_tx where type_desc='Returned' and substr(date,6,2) in ('03','04') and date>='2015-01-01' and date<='2025-12-31' order by date").fetchall()
random.seed(20261248); pick = random.sample(rows, 10)
get = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'FOL-audit/0.1'}), timeout=40))
out = []
for d, pid, nm in sorted(pick):
    y = int(d[:4])
    tx = get(f'https://statsapi.mlb.com/api/v1/transactions?playerId={pid}')['transactions']
    tx = [{'date': t.get('date'), 'typeCode': t.get('typeCode'), 'description': t.get('description'), 'toTeam': {'id': (t.get('toTeam') or {}).get('id')}} for t in tx]
    ret = [t for t in tx if t['date'] == d and 'returned' in (t['description'] or '').lower()]
    by = SF.service(pid, tx)
    st = get(f'https://statsapi.mlb.com/api/v1/people/{pid}/stats?stats=yearByYear&group=pitching,hitting&sportId=1')
    g = sum(s['stat'].get('gamesPlayed', 0) or s['stat'].get('gamesPitched', 0) for grp in st.get('stats', []) for s in grp.get('splits', []) if s.get('season') == str(y))
    out.append({'player': nm, 'pid': pid, 'returned': d, 'code': ret[0]['typeCode'] if ret else None, 'to_mlb': (ret[0]['toTeam']['id'] in SF.MLB) if ret else None,
                'counter_days': by.get(y, 0), 'mlb_games': g})
    time.sleep(0.3)
for o in out: print(o)
bad = [o for o in out if o['counter_days'] > 0 and o['mlb_games'] == 0]
print('counter credits days with 0 MLB games:', len(bad), 'of', len(out))
json.dump(out, open('/tmp/r48/eng/chalD.json', 'w'), indent=1)
