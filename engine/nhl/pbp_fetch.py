# Pull play-by-play and shift charts game by game and keep only what the shift-level model needs:
# every shot attempt (with location) and every shift. One gzip file of JSON lines per season under pbp/.
# Resumable: games already written are skipped. Usage: python3 pbp_fetch.py <first season year> <last> [seconds]
import gzip, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
Y0, Y1 = int(sys.argv[1]), int(sys.argv[2]); BUDGET = float(sys.argv[3]) if len(sys.argv) > 3 else 520
T0 = time.time(); os.makedirs('pbp', exist_ok=True)
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=40) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(1 + i)
        except Exception: time.sleep(1 + i)
    return 'ERR'
sec = lambda t: int(t.split(':')[0]) * 60 + int(t.split(':')[1]) if t and ':' in t else None
KEEP = {'shot-on-goal': 's', 'missed-shot': 'm', 'blocked-shot': 'b', 'goal': 'g'}
def game(gid):
    if time.time() - T0 > BUDGET: return None
    p = get(f'https://api-web.nhle.com/v1/gamecenter/{gid}/play-by-play')
    if p is None: return {'id': gid, 'none': 1}
    if p == 'ERR' or not p.get('plays'): return None if p == 'ERR' else {'id': gid, 'none': 1}
    s = get(f'https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={gid}')
    if s in (None, 'ERR'): return None
    ev = []
    for e in p['plays']:
        k = KEEP.get(e.get('typeDescKey'))
        if not k: continue
        d = e.get('details', {})
        ev.append([k, e['periodDescriptor']['number'], sec(e.get('timeInPeriod')), d.get('eventOwnerTeamId'), d.get('shootingPlayerId') or d.get('scoringPlayerId'), d.get('xCoord'), d.get('yCoord'), d.get('shotType'), e.get('situationCode'), e.get('homeTeamDefendingSide'), d.get('goalieInNetId'), d.get('zoneCode')])
    pen = [[e['periodDescriptor']['number'], sec(e.get('timeInPeriod')), e.get('details', {}).get('eventOwnerTeamId'), e.get('details', {}).get('committedByPlayerId'), e.get('details', {}).get('drawnByPlayerId'), e.get('details', {}).get('duration')] for e in p['plays'] if e.get('typeDescKey') == 'penalty']
    sh = [[r['playerId'], r['teamId'], r['period'], sec(r.get('startTime')), sec(r.get('endTime'))] for r in s.get('data', []) if r.get('typeCode') == 517 and r.get('startTime') and r.get('endTime')]
    return {'id': gid, 'home': p['homeTeam']['id'], 'away': p['awayTeam']['id'], 'date': p.get('gameDate'), 'ev': ev, 'pen': pen, 'sh': sh}
for y in range(Y0, Y1 + 1):
    fn = f'pbp/{y}.jsonl.gz'; done = set()
    if os.path.exists(fn):
        with gzip.open(fn, 'rt') as f:
            for line in f:
                try: done.add(json.loads(line)['id'])
                except Exception: pass
    todo = [y * 1000000 + 20000 + n for n in range(1, 1313) if y * 1000000 + 20000 + n not in done]
    n = 0
    with gzip.open(fn, 'at') as out, ThreadPoolExecutor(8) as ex:
        for r in ex.map(game, todo):
            if r: out.write(json.dumps(r, separators=(',', ':')) + '\n'); n += 1
    print(y, 'had', len(done), 'wrote', n, 'elapsed', int(time.time() - T0), flush=True)
    if time.time() - T0 > BUDGET: break
