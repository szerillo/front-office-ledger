"""Hold-out test of the arbitration award model (Nov 11). Actual salaries: Baseball-Reference salary
tables for 40 arbitration-eligible players drawn with seed 20261115 from service.json (arb winters
2014-2025); 9 had no table. A season counts as an arbitration award when the winter before it is one
of the player's arb winters and no multi-year contract in the contract book owns it.
Usage: python3 arb_calib_holdout.py tests/fixtures/arb_br_2026-11-11.txt"""
import json, sys, math, statistics as st
sys.path.insert(0, '/work'); import asset_rules as AR
S = json.load(open('/work/service.json')); CB = json.load(open('/work/contract_book.json'))['book']
own = {}
for c in CB:
    if c['yrs'] >= 2: own.setdefault(c['pid'], set()).update(c.get('own') or [])
rows = []
for line in open(sys.argv[1]):
    pid, rest = line.strip().split('#'); pid = int(pid)
    w = S.get(str(pid), {}).get('arb_winters') or []
    sal = {int(a.split(':')[0]): int(a.split(':')[1]) / 1000 for a in rest.split(',') if a}
    for y, m in sal.items():
        if (y - 1) not in w or y in own.get(pid, set()) or y == 2020: continue
        k = w.index(y - 1) + 1 - (len(w) - 3)          # 1, 2, 3; a Super Two's extra first year is 0
        sw = AR.season_war(pid)
        basis = max(sw.get(y - 1, 0.0), 0.5 * (sw.get(y - 1, 0.0) + sw.get(y - 2, 0.0)), 0.0)
        rows.append(dict(pid=pid, y=y, k=k, basis=basis, sal=m, dpw=AR.dpw(y)))
print('arbitration seasons', len(rows), 'players', len({r['pid'] for r in rows}), 'seasons', sorted({r['y'] for r in rows}))
STEP0 = {0: 0.7, 1: 1.0, 2: 1.5, 3: 3.1}
def model(r, a, steps): return max(0.75, (a + r['basis']) * steps[r['k']] * r['dpw'] / 9.7)
def report(name, pred):
    err = [p - r['sal'] for p, r in zip(pred, rows)]
    print(f"{name}: modeled ${sum(pred):.1f}M vs paid ${sum(r['sal'] for r in rows):.1f}M ({100*(sum(pred)/sum(r['sal'] for r in rows)-1):+.0f}%), "
          f"median miss ${st.median(abs(e) for e in err):.2f}M, mean miss ${st.mean(abs(e) for e in err):.2f}M")
report('current model', [model(r, 0.6, STEP0) for r in rows])
# refit a and the four class steps by least squares on log salary (grid), leave one season out
import itertools
def fit(train):
    best = None
    for a in [x / 10 for x in range(0, 21)]:
        steps = {}
        for k in (0, 1, 2, 3):
            tr = [r for r in train if r['k'] == k]
            if not tr: steps[k] = STEP0[k]; continue
            # closed form in log space: step = exp(mean(log(sal) - log((a+basis)*dpw/9.7)))
            steps[k] = math.exp(st.mean(math.log(r['sal']) - math.log(max(1e-3, (a + r['basis']) * r['dpw'] / 9.7)) for r in tr))
        loss = sum((math.log(model(r, a, steps)) - math.log(r['sal'])) ** 2 for r in train)
        if best is None or loss < best[0]: best = (loss, a, steps)
    return best[1], best[2]
pred = [None] * len(rows)
for y in sorted({r['y'] for r in rows}):
    tr = [r for r in rows if r['y'] != y]; a, steps = fit(tr)
    for i, r in enumerate(rows):
        if r['y'] == y: pred[i] = model(r, a, steps)
report('refit, each season held out', pred)
a, steps = fit(rows); print('refit on all:', 'a', a, {k: round(v, 2) for k, v in steps.items()})
for k in (0, 1, 2, 3):
    rr = [(p, r) for p, r in zip(pred, rows) if r['k'] == k]
    if rr: print(f"  class {k}: n {len(rr)}, held-out modeled ${sum(p for p, _ in rr):.1f}M vs paid ${sum(r['sal'] for _, r in rr):.1f}M")
