import json, collections, math
P = {int(k): v for k, v in json.load(open('published_service.json')).items()}
DEB = {int(k): v for k, v in json.load(open('/work/debuts.json')).items() if v}
SV = {int(k): v for k, v in json.load(open('/work/service.json')).items()}
MV = None
import re
src = open('/tmp/r45/post/moves.js').read() if False else None
def live(pid):
    d = DEB.get(pid)
    if not d: return None
    y = int(d[:4]); return y + 5 if d[5:] <= '04-15' else y + 6
def counter(pid):
    s = SV.get(pid)
    if not s or not s.get('by'): return None
    run = 0
    for y in sorted(s['by'], key=int):
        run += s['by'][y]
        if run >= 1032: return int(y)
    last = max(map(int, s['by'])); return last + math.ceil((1032 - run) / 172)
def dist(f, ids, label):
    c = collections.Counter(); n = 0
    for i in ids:
        v = f(i)
        if v is None: continue
        c[v - P[i]['ctrl_end']] += 1; n += 1
    off = sum(v for k, v in c.items() if k != 0)
    print(f'{label}: n={n} ' + ' '.join(f'{k:+d}:{c[k]}' for k in sorted(c)) + f' | off by 1+ year {off} ({100*off/max(n,1):.1f}%)')
    return c, n
ids = sorted(P)
a = dist(live, ids, 'live grading rule (debut + 6) minus published')
b = dist(counter, ids, 'service counter (service.json) minus published')
# internal check of the projection assumption: earliest vs latest published row
ch = sum(1 for i in ids if len(P[i]['all']) > 1 and P[i]['all'][0][2] != P[i]['all'][-1][2]); m = sum(1 for i in ids if len(P[i]['all']) > 1)
print(f'players with 2+ published rows: {m}; projection from the earliest row differs from the latest: {ch} ({100*ch/m:.1f}%)')
json.dump({'live': dict(a[0]), 'counter': dict(b[0])}, open('chalA.json', 'w'))
