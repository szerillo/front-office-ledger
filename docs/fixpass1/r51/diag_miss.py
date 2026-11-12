# Round 51: where the counter and the truth disagree, day by day, for the two Kinley-frame misses.
import json, datetime, sys
exec(open('score.py').read().split("F = json.load(open('frame.json'))")[0])
def counter_days(pid, T, y):
    T = sorted(T, key=lambda t: t['date'] or ''); a, b = SF.SEAS[y]; on = False; i = 0; out = set()
    while i < len(T) and (T[i]['date'] or '') < a.isoformat(): on = SF.classify(T[i], on); i += 1
    d = a
    while d <= b:
        while i < len(T) and (T[i]['date'] or '') <= d.isoformat(): on = SF.classify(T[i], on); i += 1
        if on: out.add(d)
        d += datetime.timedelta(days=1)
    return out
def truth_days(pid, y, T):
    a, b = SF.SEAS[y]; n = (b - a).days + 1; days = [a + datetime.timedelta(days=i) for i in range(n)]
    clubs = {t['toTeam']['id'] for t in T if t['toTeam']['id'] in SF.MLB and (t['date'] or '')[:4] in (str(y - 1), str(y))}
    act = {d for d in days for c in clubs if int(pid) in roster(c, d.isoformat(), 'active')}
    il, cur = set(), None
    for t in sorted(T, key=lambda t: t['date'] or ''):
        ds = (t['description'] or '').lower()
        if t['toTeam']['id'] in SF.MLB and 'injured list' in ds and ('placed' in ds or 'transferred' in ds): cur = cur or t['date']
        elif cur and any(w in ds for w in ('activated', 'reinstated', 'released', 'outright', 'optioned', 'elected free agency')):
            il |= {d for d in days if cur <= d.isoformat() < t['date']}; cur = None
    if cur: il |= {d for d in days if cur <= d.isoformat()}
    return act, il
def runs(s):
    s = sorted(s); out = []
    for d in s:
        if out and (d - out[-1][1]).days == 1: out[-1][1] = d
        else: out.append([d, d])
    return [[a.isoformat(), b.isoformat(), (b - a).days + 1] for a, b in out]
for pid, y in ((sys.argv[1], int(sys.argv[2])),):
    T = txs(pid); c = counter_days(pid, T, y); act, il = truth_days(pid, y, T); tr = act | il
    print(pid, y, 'counter', len(c), 'truth', len(tr), '(active', len(act), 'IL', len(il), ')')
    print(' counter only:', runs(c - tr)); print(' truth only:', runs(tr - c))
    a, b = SF.SEAS[y]
    for t in sorted(T, key=lambda t: t['date'] or ''):
        if f'{y-1}-10-01' <= (t['date'] or '') <= b.isoformat(): print('  ', t['date'], t['typeCode'], t['toTeam']['id'], (t['description'] or '')[:90])
json.dump(C, open(CACHE, 'w'))
