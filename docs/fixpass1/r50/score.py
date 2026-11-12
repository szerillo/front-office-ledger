# Round 49 Kinley dry run (prereg b2477dc): rule v1 vs truth on the full frame (19 player-seasons; the frame is smaller
# than the planned sample of 20, so it is a census and the bar is read as 19 of 19). No regrade, no deploy.
import json, urllib.request, importlib.util, concurrent.futures as cf, datetime, time, os
spec = importlib.util.spec_from_file_location('sf', '/tmp/r48/eng/svc_fetch.py'); SF = importlib.util.module_from_spec(spec); spec.loader.exec_module(SF)
CACHE = 'http_cache.json'; C = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def get(u):
    if u in C: return C[u]
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'FOL-audit/0.1'}), timeout=40) as r: C[u] = json.load(r); return C[u]
        except Exception: time.sleep(1 + i)
    return {}
def roster(club, d, kind): return {x['person']['id'] for x in get(f'https://statsapi.mlb.com/api/v1/teams/{club}/roster?rosterType={kind}&date={d}').get('roster', [])}
def txs(pid):
    return [{'date': t.get('date'), 'typeCode': t.get('typeCode'), 'description': t.get('description'), 'toTeam': {'id': (t.get('toTeam') or {}).get('id')}}
            for t in get(f'https://statsapi.mlb.com/api/v1/transactions?playerId={pid}').get('transactions', [])]
def resolve(pid, T):
    """rule v1: after electing free agency, an ASG to an MLB club between Nov 1 and Opening Day counts as a return
    (rewritten to a major league signing) only if he is on that club's 40-man roster the next day"""
    out, efa, log = [], None, []
    for t in sorted(T, key=lambda t: t['date'] or ''):
        d = (t['description'] or '').lower()
        if t['typeCode'] == 'DFA' and 'elected free agency' in d: efa = t['date']
        elif efa and t['typeCode'] == 'ASG' and t['toTeam']['id'] in SF.MLB:
            y = int(t['date'][:4]) + (1 if t['date'][5:7] >= '08' else 0)
            od = SF.SEAS.get(y, (None,))[0]
            if od and t['date'][5:7] in ('11', '12', '01', '02', '03', '04') and t['date'] < od.isoformat():
                nx = (datetime.date.fromisoformat(t['date']) + datetime.timedelta(days=1)).isoformat()
                on40 = int(pid) in roster(t['toTeam']['id'], nx, '40Man'); log.append([t['date'], t['toTeam']['id'], on40])
                if on40: t = dict(t, typeCode='SFA')
            efa = None
        elif t['typeCode'] in ('SFA', 'SE', 'CU', 'CLW', 'TR'): efa = None
        out.append(t)
    return out, log
def truth(pid, y, T):
    a, b = SF.SEAS[y]; n = (b - a).days + 1
    clubs = {t['toTeam']['id'] for t in T if t['toTeam']['id'] in SF.MLB and (t['date'] or '')[:4] in (str(y - 1), str(y))}
    days = [a + datetime.timedelta(days=i) for i in range(n)]
    with cf.ThreadPoolExecutor(8) as ex:
        act = list(ex.map(lambda dc: (dc[0], int(pid) in roster(dc[1], dc[0].isoformat(), 'active')), [(d, c) for d in days for c in clubs]))
    on = {d for d, ok in act if ok}
    il, cur = set(), None
    for t in sorted(T, key=lambda t: t['date'] or ''):
        ds = (t['description'] or '').lower()
        if t['toTeam']['id'] in SF.MLB and 'injured list' in ds and ('placed' in ds or 'transferred' in ds): cur = cur or t['date']
        elif cur and ('activated' in ds or 'reinstated' in ds or 'released' in ds or 'outright' in ds or 'optioned' in ds or 'elected free agency' in ds):
            for d in days:
                if cur <= d.isoformat() < t['date']: il.add(d)
            cur = None
    if cur:
        for d in days:
            if cur <= d.isoformat(): il.add(d)
    return min(172, round(len(on | il) * 186.0 / n))
F = json.load(open('frame.json')); out = []
for f in F:
    T = txs(f['pid']); y = f['season']
    old = SF.service(f['pid'], T).get(y, 0)
    R, log = resolve(f['pid'], T); new = SF.service(f['pid'], R).get(y, 0)
    tr = truth(f['pid'], y, T)
    out.append({'pid': f['pid'], 'name': f['desc'].split(' assigned')[0], 'season': y, 'asg': f['asg'], 'on40': log, 'old': old, 'new': new, 'truth': tr,
                'new_ok': abs(new - tr) <= 10, 'old_ok': abs(old - tr) <= 10})
    json.dump(C, open(CACHE, 'w'))
json.dump(out, open('kinley_result.json', 'w'), indent=1)
for o in out: print(o['name'][:22].ljust(23), o['season'], 'on40', [x[2] for x in o['on40']], 'old', o['old'], 'new', o['new'], 'truth', o['truth'], 'OK' if o['new_ok'] else 'MISS')
k = [o for o in out if o['pid'] == '641755']
print('correct (new rule):', sum(o['new_ok'] for o in out), 'of', len(out), '| old counter:', sum(o['old_ok'] for o in out), '| Kinley 2026 new:', k[0]['new'] if k else None)
