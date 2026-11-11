"""Population: every acquired player-season in a trade since 2015, inside the
trade window, after the engine's control end, with no contract in the book,
charged $0. Sample 30 with seed 20261112 (LCG as audit_sample.mjs)."""
import json, re, sys
from collections import defaultdict
sys.path.insert(0, '/work'); import asset_rules as AR
src = open('/work/moves.js').read()
types = json.loads(re.search(r'PLAYER_MOVE_TYPES = (\[.*?\]);', src).group(1))
mv = json.loads(re.search(r'PLAYER_MOVES = (\{.*?\});\n', src, re.S).group(1))
m = {'Declared Free Agency':0,'Released':0,'Signed as Free Agent':0,'Minor-league deal':'Signed as Free Agent'}
AR._EVENTS = defaultdict(list)
for p, rows in mv.items():
    for r in rows:
        t = types[r[1]]
        if t in m: AR._EVENTS[int(p)].append((r[0], m[t] or t, r[2]))
cfg = json.load(open('/work/regimes.json')); AB = {}
for r in cfg['regimes']: AB.setdefault(r['abbr'], set()).update(set(cfg['aliases'].get(str(r['teamId']), [])) | {r['team']})
tb = json.load(open('/work/trade_book.json')); NM = tb['names']
pop = []
for d, seats in tb['trades']:
    if d < '2015': continue
    for ab, net, ins, outs in seats:
        for pid, v in ins:
            ce = AR.control_end(int(pid))
            if ce is None: continue
            tot, ser = AR.trade_window(int(pid), AB.get(ab, {ab}), d)
            for y in sorted(ser):
                if y <= ce: continue
                if AR._book()['_own'].get(int(pid), {}).get(y) is not None: continue
                if AR.contract_cost(int(pid), y, after=d, acq=AB.get(ab, {ab}), played=True) == 0:
                    pop.append((d, ab, pid, NM.get(pid, pid), y, ce))
pop = sorted(set(pop))
print('population', len(pop), 'seats', len({(p[0], p[1]) for p in pop}))
seed = 20261112; pick = []; idx = list(range(len(pop)))
while len(pick) < 30:
    seed = (seed * 1103515245 + 12345) % 2147483648
    j = idx.pop(seed % len(idx)); pick.append(pop[j])
for k, p in enumerate(sorted(pick), 1): print(k, *p)
