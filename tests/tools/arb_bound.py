"""Round 12 D (prereg d4be855): arbitration bias per third of the model's prediction in dollars and percent,
then the arbitration shadow rerun with a fixed actual/model ratio per third at the point estimate and at the
end of each third's 95% interval nearest zero. Report only."""
import sys, io, contextlib, runpy, statistics as st
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ['x']; A = runpy.run_path('tests/tools/arb_shadow.py')
    T = runpy.run_path('tests/tools/arb_calib_holdout.py', run_name='x') if False else None
sys.argv = ['x', 'tests/fixtures/arb_br_2026-11-11.txt']
src = open('tests/tools/arb_calib_holdout.py').read().split("print('arbitration seasons'")[0]
g = {}; exec(src, g); rows = g['rows']
STEP0 = {0: 0.7, 1: 1.0, 2: 1.5, 3: 3.1}
for r in rows: r['m'] = max(0.75, (0.6 + r['basis']) * STEP0[r['k']] * r['dpw'] / 9.7)
s = sorted(rows, key=lambda r: r['m']); n = len(s); th = [s[:n // 3], s[n // 3: 2 * n // 3], s[2 * n // 3:]]
cut = [th[1][0]['m'], th[2][0]['m']]
print('cut points (model $M):', round(cut[0], 2), round(cut[1], 2))
for j, t in enumerate(th):
    d = [r['m'] - r['sal'] for r in t]
    print(f"third {j+1}: n {len(t)}; model ${st.mean(r['m'] for r in t):.2f}M vs paid ${st.mean(r['sal'] for r in t):.2f}M; "
          f"mean $ error {st.mean(d):+.2f}M, median {st.median(d):+.2f}M; % error {100*(sum(r['m'] for r in t)/sum(r['sal'] for r in t)-1):+.0f}%")
# err = model/paid - 1 ; ratio actual/model = 1/(1+err)
POINT = [-0.51, -0.25, -0.07]; NEAR0 = [-0.33, -0.07, 0.0]   # 95% bounds nearest zero; third 3's interval spans 0
for lab, errs in (('point', POINT), ('bound nearest zero', NEAR0)):
    ratio = [1 / (1 + e) for e in errs]
    ns = []
    for r in A['recs']:
        b = 0 if r['a'] < cut[0] else 1 if r['a'] < cut[1] else 2
        ns.append(r['a'] * ratio[b])
    print(lab, [round(x, 2) for x in ratio], 'sides 1+ win, flips, top/bottom-25, clubs 2+ ranks, largest:', A['counts'](A['apply'](ns)))
