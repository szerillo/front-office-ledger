"""Shadow run (Nov 11, pre-registered in docs/prereg-arb-shadow.md): trade grades with arbitration seasons
priced at what players were paid, where we know it, and a sensitivity draw for the rest. Report only."""
import json, re, sys, random, statistics as st, unicodedata
from collections import defaultdict
sys.path.insert(0, '/work'); import asset_rules as AR
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
tb = json.load(open('/work/trade_book.json'))
# real salaries: Baseball-Reference rows pulled Nov 11, plus the 2026 figures in arb_calib.py
real = {}
for line in open('tests/fixtures/arb_br_2026-11-11.txt'):
    pid, rest = line.strip().split('#')
    for a in rest.split(','):
        y, k = a.split(':')[:2]; real[(int(pid), int(y))] = int(k) / 1000
calib = re.search(r'REAL = \{(.*?)\n\}', open('/work/arb_calib.py').read(), re.S).group(1)
fold = lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode().lower()
D = json.load(open('/work/desk_data.json')); byname = {fold(p[0]): p[1] for p in D['players']}
for nm, sal in re.findall(r'"([^"]+)":([\d.]+)', calib):
    if fold(nm) in byname: real[(int(byname[fold(nm)]), 2026)] = float(sal)
# every priced season: (side key, pid, year, model salary, wins per $M of charge, discount)
recs = []; nets = {}
for i, (d, seats) in enumerate(tb['trades']):
    for ab, net, ins, outs in seats:
        nets[(i, ab)] = net
        for pid, v in ins:
            pid = int(pid); acq = AB.get(ab, {ab}); tot, ser = AR.trade_window(pid, acq, d)
            ce = AR.control_end(pid); y0 = int(d[:4]) + (1 if int(d[5:7]) >= 10 else 0)
            giver = next((s[0] for s in seats if any(int(q[0]) == pid for q in s[3])), None)
            for y in ser:
                if AR._book()['_own'].get(pid, {}).get(y) is not None or ce is None or not (ce - 2 <= y <= ce): continue
                a = AR.arb_salary(pid, y)
                if not a: continue
                recs.append(dict(i=i, ab=ab, giver=giver, pid=pid, y=y, a=a, k=AR.money_unit(y) / AR.dpw(y), disc=0.9 ** (y - y0)))
print('priced seasons', len(recs), 'sides', len({(r['i'], r['ab']) for r in recs}))
def charge(sal, r): return max(0.0, sal - 0.75) * r['k'] * r['disc']
def apply(newsal):
    delta = defaultdict(float)
    for r, s in zip(recs, newsal):
        dc = charge(s, r) - charge(r['a'], r)
        delta[(r['i'], r['ab'])] -= dc                     # the acquirer pays more
        if r['giver']: delta[(r['i'], r['giver'])] += dc   # the giving side's mirror
    return delta
def counts(delta):
    new = {k: nets[k] + delta.get(k, 0) for k in nets}
    moved = sum(1 for k, v in delta.items() if abs(v) >= 1.0)
    flips = sum(1 for k in delta if abs(nets[k]) >= 0.5 and (nets[k] > 0) != (new[k] > 0))
    top = lambda m: set(sorted(m, key=lambda k: -m[k])[:25]) | set(sorted(m, key=lambda k: m[k])[:25])
    topch = len(top(nets) ^ top(new)) // 2
    club = defaultdict(float); club2 = defaultdict(float)
    for (i, ab), v in nets.items(): club[ab] += v; club2[ab] += new[(i, ab)]
    rk = lambda c: {a: n for n, (a, _) in enumerate(sorted(c.items(), key=lambda x: -x[1]))}
    r1, r2 = rk(club), rk(club2)
    return moved, flips, topch, sum(1 for a in r1 if abs(r1[a] - r2[a]) >= 2), max(abs(r1[a] - r2[a]) for a in r1)
# run 1: real salaries where known
cov = [real.get((r['pid'], r['y'])) for r in recs]
print('run 1: seasons with a real salary', sum(1 for c in cov if c), 'of', len(recs))
print('  sides 1+ win, sign flips, top/bottom-25 changes, clubs moving 2+ ranks, largest rank move:', counts(apply([c if c else r['a'] for c, r in zip(cov, recs)])))
# run 2: sensitivity from the 83 held-out seasons, ratio actual / model binned by the model's prediction
sys.argv = ['x', 'tests/fixtures/arb_br_2026-11-11.txt']
exec(open('tests/tools/arb_calib_holdout.py').read().split("print('arbitration seasons'")[0])
STEP0 = {0: 0.7, 1: 1.0, 2: 1.5, 3: 3.1}
mod = lambda r: max(0.75, (0.6 + r['basis']) * STEP0[r['k']] * r['dpw'] / 9.7)
pairs = sorted((mod(r), r['sal'] / mod(r)) for r in rows)
cut = [pairs[len(pairs) // 3][0], pairs[2 * len(pairs) // 3][0]]
bins = [[q for p, q in pairs if p < cut[0]], [q for p, q in pairs if cut[0] <= p < cut[1]], [q for p, q in pairs if p >= cut[1]]]
print('bins by predicted salary: cut points $%.2fM / $%.2fM, median ratio actual/model' % tuple(cut), [round(st.median(b), 2) for b in bins])
random.seed(20261118); out = []
for _ in range(500):
    ns = [c if c else r['a'] * random.choice(bins[0 if r['a'] < cut[0] else 1 if r['a'] < cut[1] else 2]) for c, r in zip(cov, recs)]
    out.append(counts(apply(ns)))
names = ['sides 1+ win', 'sign flips', 'top/bottom-25 changes', 'clubs moving 2+ ranks', 'largest rank move']
for j, n in enumerate(names):
    xs = sorted(o[j] for o in out); print(f'run 2 {n}: median {xs[250]}, 5th-95th {xs[25]} to {xs[475]}')
