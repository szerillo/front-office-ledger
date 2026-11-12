# Round 46: published service-time figures (MLB Trade Rumors arbitration projection posts, service time as of the end
# of the prior season) matched to MLBAM ids, and the control end each implies.
import json, re, sqlite3, unicodedata, math, collections
R = json.load(open('/tmp/r46/mlbtr/svc_rows.json'))
def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().replace('’', "'")
    s = re.sub(r'\b(jr|sr|ii|iii|iv)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
db = sqlite3.connect('/tmp/v2/ledger_v3.sqlite')
NAMES = collections.defaultdict(lambda: collections.defaultdict(set))   # norm name -> id -> years seen
for pid, nm, d in db.execute('select person_id, person_name, date from sweep_tx where person_name is not null'):
    if pid and d: NAMES[norm(nm)][int(pid)].add(int(d[:4]))
DEB = {int(k): v for k, v in json.load(open('/work/debuts.json')).items() if v}
def days(s): w = int(s); return w * 172 + round((s - w) * 1000)
def ctrl_end(y, s):          # s = service at the end of season y-1
    need = 1032 - days(s)
    return (y - 1) if need <= 0 else (y - 1) + math.ceil(need / 172)
rows, miss, amb = [], [], []
for y, L in R.items():
    y = int(y)
    for r in L:
        c = NAMES.get(norm(r['name']), {})
        c = {i: ys for i, ys in c.items() if any(y - 8 <= q <= y for q in ys) and (i in DEB and int(DEB[i][:4]) < y)}
        if len(c) == 1: rows.append([next(iter(c)), y, r['svc'], r['name']])
        elif not c: miss.append((y, r['name']))
        else: amb.append((y, r['name'], list(c)))
by = collections.defaultdict(list)
for pid, y, s, nm in rows: by[pid].append((y, s, nm))
PUB = {}
for pid, L in by.items():
    L.sort(); y, s, nm = L[-1]
    PUB[pid] = {'name': nm, 'svc': s, 'asof_season': y - 1, 'source': f'MLB Trade Rumors, projected arbitration salaries for {y}',
                'ctrl_end': ctrl_end(y, s), 'all': [[a, b, ctrl_end(a, b)] for a, b, _ in L]}
json.dump(PUB, open('published_service.json', 'w'), indent=0, ensure_ascii=False)
print('rows', sum(len(v) for v in R.values()), 'matched', len(rows), 'unmatched', len(miss), 'ambiguous', len(amb), '| players', len(PUB))
print('unmatched sample', miss[:8]); print('ambiguous sample', amb[:4])
