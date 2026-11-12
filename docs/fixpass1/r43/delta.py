# Round 43 item 3: exact change in each pitching row from reading innings as outs (155.1 = 155 1/3), league constants included.
import json, sys
sys.path.insert(0, '/tmp/fix/f/engine')
F = json.load(open('/tmp/r43/ip/feed.json')); PARKS = json.load(open('/work/parks.json'))['byTeamId']
pf = lambda tid, y: PARKS.get(str(tid), {}).get(str(y), 1.0)
def ip_new(x):
    x = float(x); w = int(x); return w + round((x - w) * 10) / 3.0
def consts(y, f):
    L = F['lg'][str(y)]; tot = {}
    for st in L['hit']:
        for k, v in st.items():
            if isinstance(v, int): tot[k] = tot.get(k, 0) + v
    rpw = 1.5 * tot['runs'] / tot.get('gamesPlayed', 2430) + 3
    ip = hr = bbp = k = r = 0.0
    for st in L['pit']:
        ip += f(st.get('inningsPitched', 0)); hr += st.get('homeRuns', 0); bbp += st.get('baseOnBalls', 0) + st.get('hitByPitch', 0); k += st.get('strikeOuts', 0); r += st.get('runs', 0)
    raw = (13 * hr + 3 * bbp - 2 * k) / ip; ra9 = 9 * r / ip
    return dict(rpw=rpw, cfip=ra9 - raw, lg=ra9)
CO = {y: consts(y, float) for y in range(1998, 2027)}; CN = {y: consts(y, ip_new) for y in range(1998, 2027)}
def war(row, c, f):
    y, tm, tid, ips, hr, bb, hbp, k = row
    ip = f(ips)
    if not ip: return 0.0
    p = pf(tid, y); fip = (13 * hr + 3 * (bb + hbp) - 2 * k) / ip + c['cfip']
    if p != 1.0: fip = fip / p
    return ((c['lg'] - fip) / c['rpw']) * ip / 9 + 0.105 * ip / 9
D = {}; nrow = 0
for pid, rows in F['pitch'].items():
    for row in rows:
        y = row[0]
        if y < 1998 or y > 2026: continue
        d = war(row, CN[y], ip_new) - war(row, CO[y], float); nrow += 1
        k = f'{pid}|{y}|{row[1]}'; D[k] = D.get(k, 0) + d
import statistics
v = list(D.values())
print('pitching rows', nrow, 'player-team-seasons', len(D), 'mean delta', round(statistics.mean(v), 4), 'max |delta|', round(max(map(abs, v)), 4))
for y in (1998, 2010, 2025): print(y, 'old', {k: round(x, 4) for k, x in CO[y].items()}, 'new', {k: round(x, 4) for k, x in CN[y].items()})
json.dump(D, open('/tmp/r43/ip/delta.json', 'w'))
# check: recompute old value for Hughes 2015 and compare with cache
r = [x for x in F['pitch']['461833'] if x[0] == 2015][0]; print('Hughes 2015 old', round(war(r, CO[2015], float), 4), 'new', round(war(r, CN[2015], ip_new), 4))
