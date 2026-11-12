# fixed 50-deal set for the Deal Desk check (PREREG.md); inputs identical on both builds
import json, random
L = json.load(open('live.json'))['DESK']; C = json.load(open('cand.json'))['DESK']
rnd = random.Random(20261112)
cp = {p[1]: p for p in C['players']}
st = lambda D, i: (D.get('status') or {}).get(str(i))
qo = lambda D, i: i in set(D.get('qoIneligible') or [])
same = [p for p in L['players'] if cp.get(p[1]) == p and st(L, p[1]) == st(C, p[1]) and qo(L, p[1]) == qo(C, p[1])
        and str(p[1]) not in (L.get('pros') or {}) and str(p[1]) not in (C.get('pros') or {})
        and (not p[2] or L['payroll'].get(p[2]) == C['payroll'].get(p[2]))]
war = lambda p: abs(p[5]) + abs(p[6]) + abs(p[7])
mlb = sorted([p for p in same if p[2] and st(L, p[1]) is None and war(p) >= 1.5], key=lambda p: p[1])
fa = sorted([p for p in same if (st(L, p[1]) or [None])[0] == 'fa' and war(p) > 1], key=lambda p: p[1])
deals = []
for n in range(30):
    a = rnd.choice(mlb); b = rnd.choice([p for p in mlb if p[2] != a[2]])
    send = [a[1]]
    if n >= 20: send.append(rnd.choice([p for p in mlb if p[2] == a[2] and p[1] != a[1]])[1])
    deals.append({'id': f'T{n+1:02d}', 'mode': 'trade', 'you': a[2], 'them': b[2], 'send': send, 'recv': [b[1]]})
for n in range(12):
    p = rnd.choice(fa); yrs = rnd.randint(1, 6); f = round(rnd.uniform(0.7, 1.4), 2)
    clubs = sorted(L['teams']); club = rnd.choice(clubs)
    deals.append({'id': f'F{n+1:02d}', 'mode': 'fa', 'pid': p[1], 'yrs': yrs, 'factor': f, 'club': club})
for n in range(8):
    side = lambda: [{'kind': 'pick', 'pick': rnd.randint(1, 620), 'year': 2027} for _ in range(rnd.randint(1, 2))]
    deals.append({'id': f'D{n+1:02d}', 'mode': 'draft', 'recv': side(), 'send': side()})
json.dump({'seed': 20261112, 'eligible_mlb': len(mlb), 'eligible_fa': len(fa), 'deals': deals}, open('deals50.json', 'w'), indent=1)
print(len(deals), 'deals;', len(mlb), 'MLB and', len(fa), 'FA players eligible')
