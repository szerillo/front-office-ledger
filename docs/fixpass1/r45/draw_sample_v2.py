# Round 45: draw the control-end retry sample (seed fixed in prereg_control_end_v2.md). Inputs: docs/fixpass1/r44
# frame.json, frame_tx.json and sample20.json. Excludes Donaldson, Olson and all 20 players of the round 44 sample
# (the 7 looked up, Moore, Archer and McMahon among them, are now training data).
import json, random, sys
d = sys.argv[1] if len(sys.argv) > 1 else '.'
F = json.load(open(f'{d}/frame.json')); T = json.load(open(f'{d}/frame_tx.json')); S44 = json.load(open(f'{d}/sample20.json'))
skip = {'518626', '621566'} | set(S44['optioned_after_debut_season']) | set(S44['random'])
ids = sorted(p for p in F if p not in skip)
late = [p for p in ids if F[p][1][5:] > '06-01']                                   # MLB debut after June 1
opt = [p for p in ids if any(t['typeCode'] == 'OPT' and int(t['date'][:4]) > int(F[p][1][:4]) for t in T.get(p, []))]
random.seed(20261145)
L = random.sample(late, 5)
O = random.sample([p for p in opt if p not in L], 5)
R = random.sample([p for p in ids if p not in L + O], 10)
used = set(L + O + R)
rep = lambda pool: [p for p in random.sample(pool, len(pool)) if p not in used][:10]
out = {'late_arrival': L, 'optioned_after_debut_season': O, 'random': R,
       'replace_late': rep(late), 'replace_opt': rep(opt), 'replace_any': rep(ids),
       'frame': len(ids), 'late_pool': len(late), 'optioned_pool': len(opt)}
out['names'] = {p: F[p][0] for k in ('late_arrival', 'optioned_after_debut_season', 'random', 'replace_late', 'replace_opt', 'replace_any') for p in out[k]}
json.dump(out, open('sample20_v2.json', 'w'), indent=1, ensure_ascii=False)
print('frame', len(ids), 'late pool', len(late), 'optioned pool', len(opt))
