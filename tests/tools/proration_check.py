"""Does the engine's trade-season charge match the salary the acquirer actually owed?
The engine (asset_rules.trade_window) charges the trade season's cost times the acquirer's share of the
player's stint rows that season (1 of 2 rows = half), not the share of the season left after the deal.
Part 1: three 2017 deadline deals worked by hand (days left x salary, no cash in the deals).
Part 2: population size: every in-season (April to September) trade, the trade season re-charged at days
left / season days (assumes the player stays with the acquirer the rest of the season; a later flip would
lower it further). Report only."""
import sys, json, re
from datetime import date
from collections import defaultdict
sys.path.insert(0, '/work'); sys.path.insert(0, 'tests/tools')
import asset_rules as AR
SEASON = {y: (date(y, 3, 31), date(y, 9, 30)) for y in range(1998, 2027)}   # default: about 183 days
SEASON.update({2017: (date(2017, 4, 2), date(2017, 10, 1)), 2018: (date(2018, 3, 29), date(2018, 10, 1)),
               2019: (date(2019, 3, 28), date(2019, 9, 29)), 2020: (date(2020, 7, 23), date(2020, 9, 27)),
               2021: (date(2021, 4, 1), date(2021, 10, 3)), 2022: (date(2022, 4, 7), date(2022, 10, 5)),
               2023: (date(2023, 3, 30), date(2023, 10, 1)), 2024: (date(2024, 3, 28), date(2024, 9, 30)),
               2025: (date(2025, 3, 27), date(2025, 9, 28)), 2026: (date(2026, 3, 26), date(2026, 9, 27))})
def frac(d):
    s, e = SEASON[d.year]
    if d < s: return 1.0
    if d >= e: return 0.0
    return (e - d).days / ((e - s).days + 1)
def share(pid, y, acq):
    rows = [tm for yr, tm, v in (AR._lvm().get(int(pid)) or {}).get('rows', []) if yr == y]
    return (sum(1 for tm in rows if tm in acq) / len(rows)) if rows else 0.0

print('Part 1: 2017 deadline deals, dollars above the $0.75M minimum the acquirer is charged')
for nm, pid, d, sal in [('J.D. Martinez (DET to ARI)', 502110, date(2017, 7, 18), 11.75),
                        ('Yu Darvish (TEX to LAD)', 506433, date(2017, 7, 31), 11.0),
                        ('Justin Upton (DET to LAA)', 457708, date(2017, 8, 31), 22.125)]:
    c = AR._book()['_own'][pid][2017]; m = AR.ext_salary(c, 2017) if c['kind'] == 'ext' else c['aav']
    rows = [tm for y, tm, v in AR._lvm()[pid]['rows'] if y == 2017]; sh = share(pid, 2017, {rows[-1]})
    f = frac(d)
    print(f'  {nm}: engine ${m:.3f}M basis x {sh:.3f} of stint rows = ${sh * (m - 0.75):.2f}M; '
          f'owed ${sal}M x {f:.3f} of the season left = ${f * (sal - 0.75):.2f}M; engine/owed {sh * (m - 0.75) / (f * (sal - 0.75)):.2f}')

# Part 2
src = open('/work/moves.js').read()
types = json.loads(re.search(r'PLAYER_MOVE_TYPES = (\[.*?\]);', src).group(1)); mv = json.loads(re.search(r'PLAYER_MOVES = (\{.*?\});\n', src, re.S).group(1))
mp = {'Declared Free Agency': 'Declared Free Agency', 'Released': 'Released', 'Signed as Free Agent': 'Signed as Free Agent', 'Minor-league deal': 'Signed as Free Agent'}
AR._EVENTS = defaultdict(list)
for p, rs in mv.items():
    for r in rs:
        t = types[r[1]]
        if t in mp: AR._EVENTS[int(p)].append((r[0], mp[t], r[2]))
cfg = json.load(open('/work/regimes.json')); AB = {}
for r in cfg['regimes']: AB.setdefault(r['abbr'], set()).update(set(cfg['aliases'].get(str(r['teamId']), [])) | {r['team']})
tb = json.load(open('/work/trade_book.json')); nets = {}; delta = defaultdict(float); n = 0
for i, (d, seats) in enumerate(tb['trades']):
    dd = date(int(d[:4]), int(d[5:7]), int(d[8:10]))
    for ab, net, ins, outs in seats:
        nets[(i, ab)] = net
        if not (4 <= dd.month <= 9): continue
        acq = AB.get(ab, {ab}); f = frac(dd)
        giver = None
        for pid, v in ins:
            giver = next((s[0] for s in seats if any(int(q[0]) == int(pid) for q in s[3])), None)
            c = AR.contract_cost(int(pid), dd.year, after=d, acq=acq, played=True)
            if not c: continue
            sh = share(pid, dd.year, acq); fix = (sh - f) * c        # charge removed (+) or added (-)
            if abs(fix) < 1e-9: continue
            n += 1; delta[(i, ab)] += fix
            if giver: delta[(i, giver)] -= fix
print('Part 2: trade-season charges re-prorated by days', n)
import runpy, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ['x']; A = runpy.run_path('tests/tools/arb_shadow.py')
print('  sides 1+ win, flips, top/bottom-25 changes, clubs 2+ ranks, largest rank move:', A['counts'](delta))
print('  total charge moved to acquirers\' favour (wins): %.1f' % sum(v for (i, ab), v in delta.items() if v > 0))
for (i, ab), v in sorted(delta.items(), key=lambda kv: -abs(kv[1]))[:10]:
    print(f"  {tb['trades'][i][0]} {ab} net {nets[(i, ab)]:+.1f} change {v:+.2f}")
