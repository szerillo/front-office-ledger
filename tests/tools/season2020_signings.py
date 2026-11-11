"""Checklist item 5 sizing: free-agent and extension grades charge 2020 at the full-season rate.
Realized value for 2020 is a 60-game season, so the expected-return charge for 2020 is too high by 102/162.
Uses the free-agent grade formula (fa_grade.py: (aav - minimum) / $ per win x share x typical return) for both
kinds; extension grades take another path (ext_grade.py), so their figures are an approximation.
Also maps the change onto the public winter share pages (share.json "o", id = winter start year + club).
Usage: python3 tests/tools/season2020_signings.py [share.json]"""
import json, sys
from collections import Counter
CB = json.load(open('/work/contract_book.json'))
TYP = {int(k): v for k, v in CB['typical_fa'].items()}; DPW = {int(k): v for k, v in CB['dpw'].items()}
L = CB.get('league_min', 0.75); BAND = {int(k): v for k, v in CB.get('band_mult', {}).items()}
res = []; win = {}
for c in CB['book']:
    for h in c.get('held', []):
        if h[1] != 2020: continue
        e = max(0.0, c['aav'] - L) / DPW[2020] * h[3] * TYP.get(min(h[0], 5), CB['typical_fa_all']) * BAND.get(c.get('band'), 1.0)
        d = e * 102 / 162; res.append((c['kind'], c['pid'], c['club'], c['aav'], d))
        k = f"{c['start'] - 1}-{c['club'].lower()}"; win[k] = win.get(k, 0.0) + d
for kind in ('fa', 'ext'):
    r = [x for x in res if x[0] == kind]
    print(kind, 'contracts covering 2020', len(r), '| grade up 0.5+', sum(x[4] >= 0.5 for x in r),
          '| up 1+', sum(x[4] >= 1 for x in r), '| wins', round(sum(x[4] for x in r), 1))
print('largest:', [(k, p, cl, round(d, 2)) for k, p, cl, a, d in sorted(res, key=lambda x: -x[4])[:10]])
if len(sys.argv) > 1:
    o = set(json.load(open(sys.argv[1]))['o'])
    print('public winter pages touched:', {k: round(v, 2) for k, v in sorted(win.items(), key=lambda x: -x[1]) if k in o})
