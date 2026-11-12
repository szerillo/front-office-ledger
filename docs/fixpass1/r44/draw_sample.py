# Round 44: draw the control-end test sample (seed fixed in prereg_control_end.md). Inputs only: frame.json
# (extended players, MLB debut 2010-2019, extension signed within 6 seasons of debut) and their transactions.
import json, random
F = json.load(open('frame.json')); T = json.load(open('frame_tx.json'))
skip = {'518626', '621566'}                      # Donaldson and Olson are checked separately
ids = sorted(p for p in F if p not in skip)
opt = [p for p in ids if any(t['typeCode'] == 'OPT' and int(t['date'][:4]) > int(F[p][1][:4]) for t in T.get(p, []))]
rest = [p for p in ids if p not in opt]
random.seed(20261144)
A = random.sample(opt, 5); B = random.sample([p for p in ids if p not in A], 15)
order_opt = [p for p in random.sample(opt, len(opt)) if p not in A + B]        # replacements, in order
order_any = [p for p in random.sample(ids, len(ids)) if p not in A + B]
json.dump({'optioned_after_debut_season': A, 'random': B, 'replace_opt': order_opt[:10], 'replace_any': order_any[:10],
           'names': {p: F[p][0] for p in A + B + order_opt[:10] + order_any[:10]}, 'frame': len(ids), 'optioned_pool': len(opt)}, open('sample20.json', 'w'), indent=1)
print('frame', len(ids), 'optioned pool', len(opt))
