"""Arbitration award model against actual salaries (the 83 held-out seasons of arb_calib_holdout.py), by
thirds of the model's prediction and of the actual salary. Player-level bootstrap (2,000 draws, seed
20261119): 90% and 95% intervals, with seasons and players per third."""
import sys, random
sys.argv = ['x', 'tests/fixtures/arb_br_2026-11-11.txt']
exec(open('tests/tools/arb_calib_holdout.py').read().split("print('arbitration seasons'")[0])
STEP0 = {0: 0.7, 1: 1.0, 2: 1.5, 3: 3.1}
for r in rows: r['m'] = max(0.75, (0.6 + r['basis']) * STEP0[r['k']] * r['dpw'] / 9.7)
def thirds(key):
    s = sorted(rows, key=lambda r: r[key]); n = len(s)
    return [s[:n // 3], s[n // 3: 2 * n // 3], s[2 * n // 3:]]
def err(rs): return sum(r['m'] for r in rs) / sum(r['sal'] for r in rs) - 1
for key, lab in (('m', 'model prediction'), ('sal', 'actual salary')):
    print('split on', lab)
    for j, t in enumerate(thirds(key)):
        players = sorted({r['pid'] for r in t}); random.seed(20261119); bs = []
        for _ in range(2000):
            pick = [random.choice(players) for _ in players]
            rs = [r for p in pick for r in t if r['pid'] == p]
            bs.append(err(rs))
        bs.sort(); q = lambda x: bs[int(x * 2000)]
        print(f'  third {j + 1}: {len(t)} seasons, {len(players)} players; model vs paid {100 * err(t):+.0f}%; '
              f'90% {100 * q(.05):+.0f}% to {100 * q(.95):+.0f}%; 95% {100 * q(.025):+.0f}% to {100 * q(.975):+.0f}%')
