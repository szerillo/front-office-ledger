"""Shadow run pre-registered in docs/prereg-zero-salary-shadow.md (commit ddc7026): the 802 $0 trade seasons
after the engine's control end, charged what the player was paid (Baseball-Reference). Report only.
Usage: python3 tests/tools/zero_salary_shadow.py tests/fixtures/zero_br_2026-11-11.txt"""
import json, sys, io, contextlib, runpy
from collections import defaultdict
fx = sys.argv[1]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):            # builds the arb shadow's recs, nets, charge, counts, real
    sys.argv = ['x']; A = runpy.run_path('tests/tools/arb_shadow.py')
    Z = runpy.run_path('tests/tools/zero_salary_sample.py')
AR, tb, AB, nets, counts, apply_arb = A['AR'], A['tb'], A['AB'], A['nets'], A['counts'], A['apply']
pay = {}
for line in open(fx):
    pid, rest = line.rstrip('\n').split('#')
    for a in rest.split(','):
        if a:  # a season listed twice (release pay, split clubs): take the larger row
            y, k = a.split(':')[:2]; pay[(int(pid), int(y))] = max(pay.get((int(pid), int(y)), 0), int(k) / 1000)
for line in open('tests/fixtures/arb_br_2026-11-11.txt'):
    pid, rest = line.strip().split('#')
    for a in rest.split(','):
        y, k = a.split(':')[:2]; pay.setdefault((int(pid), int(y)), int(k) / 1000)
# corrections (tests/fixtures/salary_overrides.csv) and 2020: Baseball-Reference lists full 2020 salaries, but
# 2020 pay was prorated to 60 of 162 games, so a 2020 row is scaled to what was paid
import csv, os
# round 18 filler rule (FILLER=1): a row below the season's major-league minimum is not a salary. If every row
# for a season is below it, the season is charged the minimum when the player had a major-league stint that
# season, and is uncovered (no salary) when he did not. Sourced overrides below still win.
if os.environ.get('FILLER'):
    MINK = {2015: 507.5, 2016: 507.5, 2017: 535, 2018: 545, 2019: 555, 2020: 563.5, 2021: 570.5, 2022: 700,
            2023: 720, 2024: 740, 2025: 760, 2026: 780}
    for k in list(pay):
        if pay[k] * 1000 < MINK.get(k[1], 500):
            stint = any(yy == k[1] for yy, tm, v in (AR._lvm().get(k[0]) or {}).get('rows', []))
            if stint: pay[k] = MINK.get(k[1], 500) / 1000
            else: del pay[k]
if not os.environ.get('NOFIX'):   # NOFIX=1 reproduces the run before the corrections
    for row in csv.DictReader(open('tests/fixtures/salary_overrides.csv')):
        pay[(int(row['pid']), int(row['season']))] = float(row['salary_m'])
    for k in list(pay):
        if k[1] == 2020: pay[k] = pay[k] * 60 / 162
zero = set((d, ab, int(pid), y) for d, ab, pid, nm, y, ce in Z['pop'])
recs = []
for i, (d, seats) in enumerate(tb['trades']):
    for ab, net, ins, outs in seats:
        for pid, v in ins:
            pid = int(pid); y0 = int(d[:4]) + (1 if int(d[5:7]) >= 10 else 0)
            giver = next((s[0] for s in seats if any(int(q[0]) == pid for q in s[3])), None)
            for (dd, aa, pp, y) in [z for z in zero if z[0] == d and z[1] == ab and z[2] == pid]:
                recs.append(dict(i=i, ab=ab, giver=giver, pid=pid, y=y, sal=pay.get((pid, y)),
                                 k=AR.money_unit(y) / AR.dpw(y), disc=0.9 ** (y - y0) * A['share'](pid, y, d, AB.get(ab, {ab}))))
cov = [r for r in recs if r['sal'] is not None]
print('seasons', len(recs), 'of', len(zero), '| with a salary row', len(cov),
      '| paid more than the $0.75M floor', sum(1 for r in cov if r['sal'] > 0.75))
delta = defaultdict(float); per = []
for r in cov:
    c = max(0.0, r['sal'] - 0.75) * r['k'] * r['disc']
    delta[(r['i'], r['ab'])] -= c
    if r['giver']: delta[(r['i'], r['giver'])] += c
    per.append((c, r))
import json as _j
_j.dump([[tb['trades'][i][0], ab, nets[(i, ab)], nets[(i, ab)] + v] for (i, ab), v in delta.items() if abs(nets[(i, ab)]) >= 0.5 and (nets[(i, ab)] > 0) != (nets[(i, ab)] + v > 0)], open('/tmp/zs_flips' + ('_nofix' if os.environ.get('NOFIX') else '') + '.json', 'w'))
print('this change: sides 1+ win, flips, top/bottom-25 changes, clubs 2+ ranks, largest rank move:', counts(delta))
arb = apply_arb([A['real'].get((r['pid'], r['y'])) or r['a'] for r in A['recs']])
both = defaultdict(float)
for dct in (delta, arb):
    for k, v in dct.items(): both[k] += v
print('combined with arb run 1:', counts(both))
NM = tb['names']
mv = sorted(delta.items(), key=lambda kv: -abs(kv[1]))[:25]
print('top 25 movers (trade date, side, net now, change):')
for (i, ab), v in mv:
    print(f"  {tb['trades'][i][0]} {ab} {nets[(i, ab)]:+.1f} {v:+.1f}")
json.dump([dict(d=tb['trades'][r['i']][0], ab=r['ab'], pid=r['pid'], name=NM.get(str(r['pid']), r['pid']),
                y=r['y'], sal=r['sal'], wins=round(c, 2)) for c, r in per], open('/tmp/zero_shadow_rows.json', 'w'))
