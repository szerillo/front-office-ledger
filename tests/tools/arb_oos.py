"""Round 13 A (prereg bbdcebe): dollar offset vs percent factor for the arbitration award model, fit on seasons
up to 2020 and judged on 2021 and later. Thirds cut on the model's prediction using the training cut points."""
import sys, statistics as st
sys.argv = ['x', 'tests/fixtures/arb_br_2026-11-11.txt']
g = {}; exec(open('tests/tools/arb_calib_holdout.py').read().split("print('arbitration seasons'")[0], g); rows = g['rows']
STEP0 = {0: 0.7, 1: 1.0, 2: 1.5, 3: 3.1}
for r in rows: r['m'] = max(0.75, (0.6 + r['basis']) * STEP0[r['k']] * r['dpw'] / 9.7)
tr = [r for r in rows if r['y'] <= 2020]; te = [r for r in rows if r['y'] >= 2021]
s = sorted(r['m'] for r in tr); cut = [s[len(s) // 3], s[2 * len(s) // 3]]
b = lambda r: 0 if r['m'] < cut[0] else 1 if r['m'] < cut[1] else 2
T = [[r for r in tr if b(r) == j] for j in range(3)]
print('train', len(tr), 'seasons, per third', [len(t) for t in T], '| test', len(te), 'per third', [sum(1 for r in te if b(r) == j) for j in range(3)])
P = [sum(r['sal'] for r in t) / sum(r['m'] for r in t) for t in T]
D = [st.mean(r['sal'] - r['m'] for r in t) for t in T]
print('P factors', [round(x, 2) for x in P], '| D offsets $M', [round(x, 2) for x in D])
models = {'current': lambda r: r['m'], 'percent': lambda r: r['m'] * P[b(r)], 'dollars': lambda r: max(0.75, r['m'] + D[b(r)])}
for name, f in models.items():
    err = [f(r) - r['sal'] for r in te]
    print(f"{name}: test median abs error ${st.median(abs(e) for e in err):.2f}M, total {100*(sum(f(r) for r in te)/sum(r['sal'] for r in te)-1):+.0f}%")
print('underpowered (a training third under 8 seasons):', any(len(t) < 8 for t in T))
