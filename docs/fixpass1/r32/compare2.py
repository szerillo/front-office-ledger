# Amendment 1 (after the first run, disclosed): trade and FA verdicts render as a deal sheet, not tiles, so the
# "tile numbers" capture was empty for 42 of 50. Core = verdict with the comp boxes (.lens-box) and GM lines
# (.agm-list) removed; numbers = .sides .asset rows, .m-net, .tile .val. Both read from the saved verdict HTML.
import json, re
from bs4 import BeautifulSoup
R = {k: json.load(open(f'r_{k}.json')) for k in ['L', 'C', 'R', 'Cp', 'S']}
ids = list(R['L'])
def parts(h):
    s = BeautifulSoup(h or '', 'html.parser')
    nums = [e.get_text(' ', strip=True) for e in s.select('.sides .asset, .m-net, .tile .val')]
    for e in s.select('.lens-box, .agm-list'): e.decompose()
    return nums, re.sub(r'\s+', ' ', s.get_text(' ', strip=True))
P = {k: {i: parts(r[i].get('html')) for i in ids} for k, r in R.items()}
print('deals with numbers captured:', sum(1 for i in ids if P['L'][i][0]), 'of 50')
for a in ['R', 'C', 'Cp', 'S']:
    nd = [i for i in ids if P[a][i][0] != P['L'][i][0]]; cd = [i for i in ids if P[a][i][1] != P['L'][i][1]]
    ld = [i for i in ids if R[a][i].get('letters') != R['L'][i].get('letters')]
    print(f'{a} vs L: letters {len(ld)} {ld}; numbers {len(nd)} {nd[:10]}; core text {len(cd)} {cd[:10]}')
import difflib
for i in [i for i in ids if P['C'][i][1] != P['L'][i][1]][:8]:
    a, b = P['L'][i][1].split(), P['C'][i][1].split()
    print(' ', i, [(' '.join(a[i1:i2])[:90], ' '.join(b[j1:j2])[:90]) for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if t != 'equal'][:3])
for i in [i for i in ids if P['S'][i][0] != P['L'][i][0]][:3]: print('  seed', i, P['L'][i][0][:4], '->', P['S'][i][0][:4])
