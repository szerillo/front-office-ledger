"""Round 14: how big a difference could the round-13 out-of-sample test (bbdcebe) have detected?
Paired player-level bootstrap of the test seasons (2,000 draws, seed 20261126) for the difference in median
absolute error between the dollar offset and the current model, plus the spread of the fitted offsets when the
7 training seasons are themselves resampled."""
import sys, random, statistics as st
sys.argv = ['x', 'tests/fixtures/arb_br_2026-11-11.txt']
g = {}; exec(open('tests/tools/arb_calib_holdout.py').read().split("print('arbitration seasons'")[0], g); rows = g['rows']
STEP0 = {0: 0.7, 1: 1.0, 2: 1.5, 3: 3.1}
for r in rows: r['m'] = max(0.75, (0.6 + r['basis']) * STEP0[r['k']] * r['dpw'] / 9.7)
tr = [r for r in rows if r['y'] <= 2020]; te = [r for r in rows if r['y'] >= 2021]
s = sorted(r['m'] for r in tr); cut = [s[len(s) // 3], s[2 * len(s) // 3]]
b = lambda r: 0 if r['m'] < cut[0] else 1 if r['m'] < cut[1] else 2
def offsets(t):
    out = []
    for j in range(3):
        x = [r['sal'] - r['m'] for r in t if b(r) == j]
        out.append(st.mean(x) if x else 0.0)
    return out
D = offsets(tr)
dol = lambda r, D=D: max(0.75, r['m'] + D[b(r)])
random.seed(20261126); players = sorted({r['pid'] for r in te}); diffs = []
for _ in range(2000):
    pick = [random.choice(players) for _ in players]; rs = [r for p in pick for r in te if r['pid'] == p]
    diffs.append(st.median(abs(dol(r) - r['sal']) for r in rs) - st.median(abs(r['m'] - r['sal']) for r in rs))
diffs.sort(); se = st.pstdev(diffs)
print('test seasons', len(te), 'players', len(players))
print('dollar minus current, median abs error: point %+.2f, 95%% %+.2f to %+.2f, SE %.2f' % (st.median(diffs), diffs[50], diffs[1950], se))
print('smallest difference detectable at 80%% power, two-sided 5%%: about $%.2fM a season (2.8 x SE)' % (2.8 * se))
fit = []
for _ in range(2000):
    t = [random.choice(tr) for _ in tr]; fit.append(offsets(t))
for j in range(3):
    x = sorted(f[j] for f in fit); print(f'third {j+1} offset fitted on 7 seasons: 95% {x[50]:+.2f} to {x[1950]:+.2f} ($M)')
