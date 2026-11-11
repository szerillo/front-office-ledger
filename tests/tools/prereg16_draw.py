"""Draws for docs/prereg-round16.md. Run only after that file is committed.
Usage: python3 tests/tools/prereg16_draw.py"""
import sys, random
sys.path.insert(0, '/work'); import asset_rules as AR
rows = set()
for f in ['tests/fixtures/zero_br_2026-11-11.txt', 'tests/fixtures/zero_br_rand40_2026-11-11.txt', 'tests/fixtures/arb_br_2026-11-11.txt']:
    for l in open(f):
        p, r = l.strip().split('#')
        for a in r.split(','):
            if a: y, k = a.split(':')[:2]; rows.add((int(p), int(y), int(k)))
rows = sorted(rows)
PREV = {435522, 596057, 592192, 493329, 456034, 607074, 621242, 516782, 605135, 593160}   # round 16 post hoc ten
clubs = lambda p, y: {tm for yy, tm, v in (AR._lvm().get(p) or {}).get('rows', []) if yy == y}
A = [x for x in rows if x[1] == 2020 and x[0] not in PREV and (len(clubs(x[0], 2020)) >= 2 or x[2] <= 600)]
print('A: 2020 traded or minimum rows (all of them, fewer than 10):', len(A))
for x in A: print('  A', x, sorted(clubs(x[0], 2020)))
B = [x for x in rows if x[2] >= 15000]
pick = random.Random(20261131).sample(B, 20)
print('B: rows of $15M or more:', len(B), '| drawn 20 with seed 20261131')
for x in sorted(pick): print('  B', x, sorted(clubs(x[0], x[1])))
