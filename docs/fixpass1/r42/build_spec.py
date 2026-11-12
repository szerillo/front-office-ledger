# Round 42: the player-seasons behind every settled winter total, with their sign (production totals are sums of WAR:
# trade seat = WAR of pieces got minus pieces given, each in the receiving club's window; signing = realized WAR minus
# a price-based cost that does not move with WAR). Inputs: the live engine run Z_X6 (= live data). Output winter_spec.json.
import json, math
W = '/tmp/sbx/runs/Z_X6/work/'
AB = {'ARI': ['Arizona Diamondbacks'], 'ATH': ['Oakland Athletics', 'Athletics'], 'ATL': ['Atlanta Braves'], 'BAL': ['Baltimore Orioles'],
 'BOS': ['Boston Red Sox'], 'CHC': ['Chicago Cubs'], 'CWS': ['Chicago White Sox'], 'CIN': ['Cincinnati Reds'], 'CLE': ['Cleveland Indians', 'Cleveland Guardians'],
 'COL': ['Colorado Rockies'], 'DET': ['Detroit Tigers'], 'HOU': ['Houston Astros'], 'KC': ['Kansas City Royals'], 'LAA': ['Anaheim Angels', 'Los Angeles Angels'],
 'LAD': ['Los Angeles Dodgers'], 'MIA': ['Florida Marlins', 'Miami Marlins'], 'MIL': ['Milwaukee Brewers'], 'MIN': ['Minnesota Twins'], 'NYM': ['New York Mets'],
 'NYY': ['New York Yankees'], 'PHI': ['Philadelphia Phillies'], 'PIT': ['Pittsburgh Pirates'], 'SD': ['San Diego Padres'], 'SF': ['San Francisco Giants'],
 'SEA': ['Seattle Mariners'], 'STL': ['St. Louis Cardinals'], 'TB': ['Tampa Bay Devil Rays', 'Tampa Bay Rays'], 'TEX': ['Texas Rangers'], 'TOR': ['Toronto Blue Jays'],
 'WSH': ['Montreal Expos', 'Washington Nationals']}
L = json.load(open(W + 'lvm_cache.json')); tp = json.load(open(W + 'trade_parts.json')); tb = json.load(open(W + 'trade_book.json'))['trades']
O = json.load(open(W + 'offseasons.json')); settled = {(r[0], r[1]): r for r in O['rows'] if r[1] < O['open_from']}
def winter_of(d):
    y, m = int(d[:4]), int(d[5:7])
    return y if m >= 10 else (y - 1 if m <= 3 else None)
def rows(pid, ab, y0, y1):
    v = L.get(str(pid)); nm = AB[ab]
    if y0 is None or y1 is None: return []
    return [[str(pid), y, t, w] for y, t, w in (v['rows'] if isinstance(v, dict) else []) if y0 <= y <= y1 and t in nm]
spec = {}; chk = []
for d, seats in tb:
    w = winter_of(d)
    if w is None or (seats[0][0], w) not in settled and all((s[0], w) not in settled for s in seats): continue
    for ab, net, got, gave in seats:
        if (ab, w) not in settled: continue
        T = spec.setdefault(f'{ab}|{w}', []); s = 0.0
        for pid, v in got:
            p = tp.get(f'{d}|{pid}|{ab}')
            if p: rr = rows(pid, ab, p[2], p[3]); T += [r + [1] for r in rr]; s += sum(r[3] for r in rr)
        others = [x[0] for x in seats if x[0] != ab]
        for pid, v in gave:
            for oc in others:
                p = tp.get(f'{d}|{pid}|{oc}')
                if p: rr = rows(pid, oc, p[2], p[3]); T += [r + [-1] for r in rr]; s -= sum(r[3] for r in rr); break
        chk.append((d, ab, net, s))
sw = json.load(open(W + 'sweep_results.json')); hs = json.load(open(W + 'hist_results.json'))
seen = set(); fchk = []
for r in (sw + hs):
    for row in r.get('allx_fa') or []:
        d, name, yrs, tot, real, cost, net, pid = row[:8]
        if net is None or tot is None: continue
        w = winter_of(d); ab = r['abbr']
        if w is None or (ab, w) not in settled or (ab, pid, d) in seen: continue
        seen.add((ab, pid, d)); rr = rows(pid, ab, w + 1, w + yrs)
        spec.setdefault(f'{ab}|{w}', []).extend(r2 + [1] for r2 in rr); fchk.append((d, ab, name, real, sum(x[3] for x in rr)))
import statistics
dt = [abs(a[2] - a[3]) for a in chk]; df = [abs(a[3] - a[4]) for a in fchk]
print('trade seats', len(chk), 'median |net - spec sum|', round(statistics.median(dt), 3), 'share within 0.15:', round(sum(x <= 0.15 for x in dt) / len(dt), 3))
print('signings', len(fchk), 'median |real - spec sum|', round(statistics.median(df), 3), 'share within 0.15:', round(sum(x <= 0.15 for x in df) / len(df), 3))
print('winters', len(spec), 'of settled', len(settled), 'terms', sum(len(v) for v in spec.values()))
for a in sorted(chk, key=lambda a: -abs(a[2] - a[3]))[:5]: print(' worst trade', a)
for a in sorted(fchk, key=lambda a: -abs(a[3] - a[4]))[:5]: print(' worst fa', a)
tot = {f'{k[0]}|{k[1]}': v[9] for k, v in settled.items()}
json.dump({'tot': tot, 'terms': spec}, open('/tmp/r42/t/winter_spec.json', 'w'), separators=(',', ':'))
