"""Fresh audit sample (Nov 11, round 3). Uniform over every graded move, not the
report cards' best/worst rows: each trade in the trade book (one seat picked at
random) and each free-agent signing and extension in the contract book, 1998 on.
Seed 20261113, same LCG as audit_sample.mjs; moves in the two earlier samples skipped."""
import json, sys
tb = json.load(open('/work/trade_book.json')); NM = tb['names']
cb = json.load(open('/work/contract_book.json'))['book']
prev = set()
for f in ('/tmp/sample40.json', '/tmp/hi20.json'):
    try:
        for o in json.load(open(f)): prev.add(((o.get('d') or '')[:7], tuple(sorted(map(str, o.get('pids') or [])))))
    except Exception: pass
pop = [('trade', d, seats) for d, seats in tb['trades'] if d >= '1998']
pop += [(c['kind'], c['sign'], c) for c in cb if c['sign'] >= '1998']
seed = 20261113
def rnd():
    global seed; seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648
idx = list(range(len(pop))); out = []
while len(out) < 40:
    k, d, x = pop[idx.pop(int(rnd() * len(idx)))]
    if k == 'trade':
        s = x[int(rnd() * len(x))]
        pids = tuple(sorted({p for p, _ in s[2]} | {p for p, _ in s[3]}))
        if (d[:7], pids) in prev: continue
        out.append({'kind': 'trade', 'd': d, 'club': s[0], 'net': s[1], 'got': [[NM.get(p, p), p, v] for p, v in s[2]], 'gave': [[NM.get(p, p), p, v] for p, v in s[3]], 'seats': [z[0] for z in x]})
    else:
        if (d[:7], (str(x['pid']),)) in prev: continue
        out.append({'kind': k, 'd': d, 'club': x['club'], 'name': x['name'], 'pid': x['pid'], 'yrs': x['yrs'], 'tot': x['tot'], 'start': x['start'], 'src': x.get('src')})
json.dump(out, open('/tmp/sample3.json', 'w'), indent=1)
from collections import Counter
print('population', len(pop), Counter(p[0] for p in pop), 'drawn', Counter(o['kind'] for o in out), 'era', Counter('1998-2009' if o['d'] < '2010' else '2010-2019' if o['d'] < '2020' else '2020-26' for o in out))
for i, o in enumerate(out):
    print(i, o['kind'], o['d'], o['club'], (o.get('name') or '') + (f" {o['yrs']}y/${o['tot']}M" if o['kind'] != 'trade' else ' got ' + ', '.join(g[0] for g in o['got']) + ' | gave ' + ', '.join(g[0] for g in o['gave'])))
