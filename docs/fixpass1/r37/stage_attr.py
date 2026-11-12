# attribute every moved trade-seat net and card-row value (t_grades population) to the build step that moved it
import json
from collections import Counter
def norm(X):
    o = {}
    for k, v in X.items():
        p = k.split('|')
        o[('t', p[1], p[3][1:], tuple(sorted(p[2].split('/')))) if p[0] == 't' else k] = v
    return o
S = ['live', 's_RV3', 's_W3', 's_E3', 's_X0', 'good7']
CAUSE = {'s_RV3': 'data', 's_W3': 'fix pass', 's_E3': '2020 fix', 's_X0': 're-sign', 'good7': 'names/page'}
D = {s: norm(json.load(open(f'/tmp/deploy/tg_{s}.json'))) for s in S}
moved = [k for k in D['live'] if k in D['good7'] and D['live'][k] != D['good7'][k]]
by = Counter()
for k in moved:
    steps = [CAUSE[b] for a, b in zip(S, S[1:]) if k in D[a] and k in D[b] and D[a][k] != D[b][k]]
    kind = 'trade' if isinstance(k, tuple) else 'card'
    by[(kind, '+'.join(steps) or 'key gap')] += 1
print('moved live vs good7:', len(moved)); [print(' ', k, v) for k, v in sorted(by.items())]
