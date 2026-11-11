"""Round 13 B and C (prereg bbdcebe): salary rows that may not be pay for playing, and pages that may belong to
another player. Over both Baseball-Reference fixtures."""
import sys, io, contextlib, runpy
from collections import defaultdict
sys.path.insert(0, '/work'); import asset_rules as AR
with contextlib.redirect_stdout(io.StringIO()): Z = runpy.run_path('tests/tools/zero_salary_sample.py')
pop = {(int(p[2]), p[4]) for p in Z['pop']}
rows = defaultdict(lambda: defaultdict(list)); src = {}
for f in ['tests/fixtures/zero_br_2026-11-11.txt', 'tests/fixtures/arb_br_2026-11-11.txt']:
    for l in open(f):
        pid, rest = l.strip().split('#'); pid = int(pid)
        for a in rest.split(','):
            if a:
                y, k = a.split(':')[:2]
                if int(k) not in rows[pid][int(y)]: rows[pid][int(y)].append(int(k))   # dedupe the same row seen in both files
MIN = lambda y: {2015: 507.5, 2016: 507.5, 2017: 535, 2018: 545, 2019: 555, 2020: 563.5, 2021: 570.5, 2022: 700, 2023: 720, 2024: 740, 2025: 760, 2026: 780}.get(y, 500)
BUY = {250, 500, 750, 1000, 1500, 2000}
flags = defaultdict(set); n = 0
for pid, ys in rows.items():
    played = {y for y, tm, v in (AR._lvm().get(pid) or {}).get('rows', [])}
    for y in sorted(ys):
        for k in ys[y]:
            n += 1; key = (pid, y, k); prev = max(ys.get(y - 1, [0]))
            if len(ys[y]) > 1: flags[1].add(key)
            if prev and MIN(y) < k < 0.4 * prev: flags[2].add(key)
            if played and y not in played and y <= 2026: flags[3].add(key)
            nxt = ys.get(y + 1)
            if k in BUY and prev > k and not (nxt and max(nxt) > k): flags[4].add(key)
allf = set().union(*flags.values())
print('salary rows', n, 'players', len(rows))
for j in (1, 2, 3, 4): print(f' rule {j}: {len(flags[j])} rows, in the $0 population {sum(1 for x in flags[j] if (x[0], x[1]) in pop)}')
print(' any rule:', len(allf), '| two or more rules:', sum(1 for x in allf if sum(x in flags[j] for j in flags) >= 2),
      '| in the $0 population:', sum(1 for x in allf if (x[0], x[1]) in pop))
inpop = sorted([x for x in allf if (x[0], x[1]) in pop and x[2] > 760], key=lambda x: -x[2])
NM = Z['tb']['names'] if 'tb' in Z else {}
print(' largest flagged in the population:', [(NM.get(str(p), p), y, k, [j for j in flags if (p, y, k) in flags[j]]) for p, y, k in inpop[:8]])
# C: identity
print('C: suspect pages')
for pid, ys in rows.items():
    played = sorted({y for y, tm, v in (AR._lvm().get(pid) or {}).get('rows', [])})
    sal = sorted(ys)
    if not played or not sal: continue
    share = sum(1 for y in sal if y in played) / len(sal)
    if share < 0.5 or sal[0] < played[0] - 3:
        print('  ', pid, NM.get(str(pid), pid), 'salary seasons', sal[0], '-', sal[-1], 'played', played[0], '-', played[-1], 'share %.2f' % share)
