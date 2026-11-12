# which build step changes each piece of public Desk text: L (live) -> RV3 (data) -> W3 (fix pass rules 1-14)
# -> E3 (2020 fix) -> X0 (re-sign rule, tie-break, page fix) -> G5 (pinned names + split, the candidate)
import json, re, difflib
from bs4 import BeautifulSoup
from collections import Counter, defaultdict
ST = ['L', 'RV3', 'W3', 'E3', 'X0', 'G5']; CAUSE = {'RV3': 'data (feed after Nov 1)', 'W3': 'fix pass rules 1-14', 'E3': '2020 fix', 'X0': 're-sign rule / tie-break', 'G5': 'pinned names'}
R = {k: json.load(open(f'r_{k}.json')) for k in ST}
def sec(h):
    s = BeautifulSoup(h or '', 'html.parser')
    comps = [re.sub(r'\s+', ' ', e.get_text(' ', strip=True)) for e in s.select('.lens-box')]
    gm = [re.sub(r'\s+', ' ', e.get_text(' ', strip=True)) for e in s.select('.agm-list')]
    for e in s.select('.lens-box, .agm-list'): e.decompose()
    return {'comps': comps, 'gm': gm, 'core': re.sub(r'\s+', ' ', s.get_text(' ', strip=True)), 'letters': R}
P = {k: {i: sec(R[k][i].get('html')) for i in R['L']} for k in ST}
tot = Counter(); bydeal = defaultdict(set); frag = defaultdict(list)
for i in R['L']:
    for part in ['comps', 'gm', 'core']:
        for a, b in zip(ST, ST[1:]):
            if P[a][i][part] != P[b][i][part]:
                tot[(part, b)] += 1; bydeal[i].add((part, CAUSE[b]))
                x, y = ' | '.join(P[a][i][part]) if part != 'core' else P[a][i][part], ' | '.join(P[b][i][part]) if part != 'core' else P[b][i][part]
                ops = [(' '.join(x.split()[i1:i2]), ' '.join(y.split()[j1:j2])) for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, x.split(), y.split(), autojunk=False).get_opcodes() if t != 'equal']
                frag[(part, b)] += [(i, o) for o in ops]
print('deals whose public text changes L to G5:', sum(1 for i in R['L'] if any(P['L'][i][p] != P['G5'][i][p] for p in ['comps', 'gm', 'core'])))
for (part, b), n in sorted(tot.items()): print(f'{part:5} {CAUSE[b]:28} {n} deals')
json.dump({f'{p}|{CAUSE[b]}': v for (p, b), v in frag.items()}, open('attrib_frags.json', 'w'), indent=0)
for k, v in frag.items():
    print('\n==', k[0], CAUSE[k[1]], len(v), 'edits'); [print('  ', i, repr(o[0][:110]), '->', repr(o[1][:110])) for i, o in v[:7]]
