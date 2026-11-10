import csv, json, collections, math, random, sys
# Remember Some Dudes: career WAR from Baseball-Reference's public WAR files
# (https://www.baseball-reference.com/data/war_daily_bat.txt and war_daily_pitch.txt, saved under <dir>/bref/).
# Usage: python3 engine/dudes_build.py <dir>; writes <dir>/dudes.json
S = sys.argv[1]
P = collections.defaultdict(lambda: {'nm': '', 'yrs': set(), 'war': 0.0, 'teams': collections.Counter(), 'pa': 0, 'g': 0, 'ipo': 0, 'gp': 0, 'best': (-99, 0), 'sw': collections.defaultdict(float), 'mlb': ''})
def num(x):
    try: return float(x)
    except: return 0.0
with open(f'{S}/bref/war_daily_bat.txt', newline='', encoding='utf-8', errors='replace') as f:
    for r in csv.DictReader(f):
        p = P[r['player_ID']]; p['nm'] = r['name_common']; y = int(r['year_ID']); p['yrs'].add(y)
        w = num(r['WAR']); p['war'] += w; p['sw'][y] += w
        p['mlb'] = r['mlb_ID'] or p['mlb']
        if r['pitcher'] != 'Y':
            p['pa'] += int(num(r['PA'])); p['g'] += int(num(r['G'])); p['teams'][r['team_ID']] += int(num(r['G']))
with open(f'{S}/bref/war_daily_pitch.txt', newline='', encoding='utf-8', errors='replace') as f:
    for r in csv.DictReader(f):
        p = P[r['player_ID']]; p['nm'] = r['name_common']; y = int(r['year_ID']); p['yrs'].add(y)
        w = num(r['WAR']); p['war'] += w; p['sw'][y] += w
        p['ipo'] += int(num(r['IPouts'])); p['gp'] += int(num(r['G'])); p['teams'][r['team_ID']] += int(num(r['G']))
        p['mlb'] = r['mlb_ID'] or p['mlb']
out = []
for pid, p in P.items():
    if not p['yrs']: continue
    y0, y1 = min(p['yrs']), max(p['yrs'])
    pit = p['ipo'] / 3 >= 100 and p['ipo'] / 3 * 3 > p['pa']
    if y1 > 2024: continue                       # retired or long gone: no one active
    if y1 - y0 + 1 < 4: continue
    if pit and p['ipo'] / 3 < 300: continue
    if not pit and p['pa'] < 1200: continue
    if p['war'] > 40 or p['war'] < -3: continue  # dudes, not legends or disasters
    if y0 < 1901: continue
    bs = max(p['sw'].items(), key=lambda kv: kv[1])
    teams = [t for t, _ in p['teams'].most_common(4)]
    out.append({'id': pid, 'n': p['nm'], 'y0': y0, 'y1': y1, 'p': 1 if pit else 0, 'w': round(p['war'], 1),
                'pa': p['pa'], 'ip': round(p['ipo'] / 3), 'g': p['g'] if not pit else p['gp'], 't': teams, 'b': [bs[0], round(bs[1], 1)], 'm': p['mlb']})
# the line: what players with about his playing time, in his era, usually produced
def key(d): return (d['p'], (d['y0'] + d['y1']) // 2 // 20, int(math.log((d['ip'] if d['p'] else d['pa']) + 1) * 4))
grp = collections.defaultdict(list)
for d in out: grp[key(d)].append(d['w'])
for d in out:
    xs = sorted(grp[key(d)]); m = xs[len(xs) // 2] if xs else 5
    d['L'] = round(m * 2) / 2 if abs(round(m * 2) / 2 - d['w']) >= 0.3 else round(m * 2) / 2 + (0.5 if d['w'] < m else -0.5)
random.seed(7)
print(len(out), sum(1 for d in out if d['w'] > d['L']) / len(out))
print(collections.Counter((d['y0'] // 10 * 10) for d in out).most_common())
# the shipped set (Nov 10): regulars whose careers centered on 1991-2014 (began 1984 or later, ended by 2020),
# 2,500+ PA or 700+ IP; the line re-cut within that pool (5-year era band, playing-time band)
def mid(x): return (x['y0'] + x['y1']) / 2
pool = [x for x in out if x['y0'] >= 1984 and x['y1'] <= 2020 and 1991 <= mid(x) <= 2014 and ((not x['p'] and x['pa'] >= 2500) or (x['p'] and x['ip'] >= 700))]
def k2(x): return (x['p'], int(mid(x)) // 5, int(math.log((x['ip'] if x['p'] else x['pa']) + 1) * 5))
g2 = collections.defaultdict(list)
for x in pool: g2[k2(x)].append(x['w'])
for x in pool:
    xs = sorted(g2[k2(x)])
    if len(xs) < 5: xs = sorted(y['w'] for y in pool if y['p'] == x['p'] and abs(math.log((y['ip'] if y['p'] else y['pa']) + 1) - math.log((x['ip'] if x['p'] else x['pa']) + 1)) < 0.15)
    L = round(xs[len(xs) // 2] * 2) / 2
    if abs(L - x['w']) < 0.3: L += 0.5 if x['w'] <= L else -0.5
    x['L'] = L
rows = [[x['id'], x['n'], x['y0'], x['y1'], x['p'], x['w'], x['ip'] if x['p'] else x['pa'], '/'.join(x['t'][:3]), x['b'][0], x['b'][1], x['L']] for x in pool]
json.dump({'v': 2, 'src': 'Career WAR: Baseball-Reference', 'cols': ['id', 'name', 'first', 'last', 'pitcher', 'war', 'pa_or_ip', 'teams', 'best_year', 'best_war', 'line'], 'rows': rows}, open(f'{S}/dudes.json', 'w'), separators=(',', ':'), ensure_ascii=False)
