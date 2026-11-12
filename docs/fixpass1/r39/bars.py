# Bars 1-3 of the pre-registration (dd3d4a8), base Z_X6 (live engine) vs run P0, determinism P0 vs P1
import json, hashlib, os, sys
from collections import defaultdict
B, R0, R1 = '/tmp/sbx/runs/Z_X6/work', '/tmp/sbx/runs/P0/work', '/tmp/sbx/runs/P1/work'
est = json.load(open('/tmp/prereg/estimate.json'))
want = {f'{d}|{p}|{c}' for d, p, c, e, w in est['hits']}
P0, PB = json.load(open(R0 + '/trade_parts.json')), json.load(open(B + '/trade_parts.json'))
changed = {k for k in set(P0) | set(PB) if (PB.get(k) or [None] * 4)[3] != (P0.get(k) or [None] * 4)[3]}
print(f'BAR 1: window end changed for {len(changed)} pieces; listed 52; missing {len(want - changed)}; extra {len(changed - want)}')
for k in sorted(want - changed)[:10]: print('   missing', k, PB.get(k), P0.get(k))
for k in sorted(changed - want)[:10]: print('   extra', k, PB.get(k), P0.get(k))
b1 = changed == want
def seats(path):
    s = {}
    for d, ss in json.load(open(path + '/trade_book.json'))['trades']:
        for st in ss: s[(d, st[0])] = s.get((d, st[0]), 0) + st[1]
    return s
SB, S0 = seats(B), seats(R0)
moved = {k: S0.get(k, 0) - SB.get(k, 0) for k in set(SB) | set(S0) if abs(S0.get(k, 0) - SB.get(k, 0)) >= 0.05}
estseat = {tuple(k.split('|')): v for k, v in est['seats'].items()}
unlisted = [k for k in moved if k not in estseat]
wrongdir = [(k, round(v, 2), round(estseat[k], 2)) for k, v in moved.items() if abs(v) >= 0.5 and k in estseat and (v > 0) != (estseat[k] > 0)]
print(f'BAR 2: seats moved {len(moved)} (0.5+: {sum(abs(v) >= 0.5 for v in moved.values())}); without a listed piece {len(unlisted)}; 0.5+ against the estimated direction {len(wrongdir)}')
for k in unlisted[:10]: print('   unlisted', k, round(moved[k], 2))
for w in wrongdir[:10]: print('   wrong direction', w)
b2 = not unlisted and not wrongdir
PUB = ['offseasons.json', 'trade_parts.json', 'trade_book.json', 'front-office-ledger-prototype.html', 'cards.js', 'moves.js', 'desk_data.json', 'sweep_results.json', 'hist_results.json']
md = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()[:10] if os.path.exists(p) else 'missing'
diff = [(f, md(f'{R0}/{f}'), md(f'{R1}/{f}')) for f in PUB if md(f'{R0}/{f}') != md(f'{R1}/{f}')]
print(f'BAR 3: P0 vs P1, {len(PUB)} published files, differing {len(diff)}', diff)
b3 = not diff
json.dump({'changed': sorted(changed), 'moved': {f'{k[0]}|{k[1]}': v for k, v in moved.items()}}, open('/tmp/prereg/bars_out.json', 'w'))
print('BARS 1-3:', 'PASS' if b1 and b2 and b3 else 'FAIL', b1, b2, b3)
