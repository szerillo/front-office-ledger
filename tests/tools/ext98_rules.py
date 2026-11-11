"""Automatic checks on data/research/ext_1998_2014.csv (Nov 11), no hand checks:
  club rule:   the row's club must be a team the player played for in the signing season, the season before
               or the first season (the signing club; a later trade does not make it wrong: Arroyo, Peavy)
  start rule:  a deal signed June or later that starts the same season is flagged (Suzuki); first seasons
               two or more years out are tack-on deals (Votto, Cabrera) and are not flagged
Usage: python3 tests/tools/ext98_rules.py"""
import csv, json, sys
from collections import Counter
sys.path.insert(0, '/work'); import asset_rules as AR
L = AR._lvm(); cfg = json.load(open('/work/regimes.json'))
names = {}
for r in cfg['regimes']: names.setdefault(r['abbr'], set()).update(set(cfg['aliases'].get(str(r['teamId']), [])) | {r['team']})
cb = json.load(open('/work/contract_book.json'))['book']
pid = {(c['name'], c['sign']): c['pid'] for c in cb if c['src'] == 'ext98'}
rows = list(csv.DictReader(open('data/research/ext_1998_2014.csv')))
flags = Counter(); out = []
for r in rows:
    p = pid.get((r['player'], r['date'][:7])); f = int(r['first_season']); sy, sm = int(r['date'][:4]), int(r['date'][5:7])
    why = []
    if not p or int(p) not in L: flags['no player match'] += 1; continue
    teams = {}
    for y, tm, v in L[int(p)]['rows']: teams.setdefault(y, set()).add(tm)
    near = set().union(*[teams.get(y, set()) for y in (sy - 1, sy, f)])
    if not near: why.append('no season played to check club')
    elif not (near & names.get(r['team'], {r['team']})): why.append(f"club {r['team']} but played {sy - 1}-{sy} and {f} for {', '.join(sorted(near))}")
    if f < sy: why.append(f'first season {f} before signing {r["date"]}')
    elif sm >= 6 and f == sy: why.append(f'signed {r["date"]}, starts same season')
    for w in why: flags[w.split(' ')[0] + ' ' + w.split(' ')[1] if w.startswith('club') else w.split(' ')[0]] += 1
    if why: out.append((r['date'], r['player'], r['team'], r['years'], r['total_m'], r['first_season'], '; '.join(why)))
print('rows', len(rows), 'flagged', len(out), dict(flags))
for o in out: print(' ', *o)
