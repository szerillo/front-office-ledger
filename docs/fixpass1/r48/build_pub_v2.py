# Round 48: same as round 46, plus a same-name tie broken by the team heading the row sits under.
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
NICK = {108: "Angels", 109: "Diamondbacks", 110: "Orioles", 111: "Red Sox", 112: "Cubs", 113: "Reds", 114: "Indians Guardians",
        115: "Rockies", 116: "Tigers", 117: "Astros", 118: "Royals", 119: "Dodgers", 120: "Nationals", 121: "Mets", 133: "Athletics",
        134: "Pirates", 135: "Padres", 136: "Mariners", 137: "Giants", 138: "Cardinals", 139: "Rays", 140: "Rangers", 141: "Blue Jays",
        142: "Twins", 143: "Phillies", 144: "Braves", 145: "White Sox", 146: "Marlins", 147: "Yankees", 158: "Brewers"}
def club_of(head):                                                       # "Astros" or "Houston Astros" -> 117
    h = (head or "").strip()
    for cid, nk in NICK.items():
        if any(h == n or h.endswith(" " + n) for n in ([nk] if cid != 114 else nk.split())): return cid
LAST = collections.defaultdict(list)                                    # id -> [(date, club id)] from the feed
for pid, tid, d, to in db.execute("select person_id, team_id, date, to_team from sweep_tx where person_id is not null"):
    if pid and d: LAST[int(pid)].append((d, club_of(to) or tid))
for v in LAST.values(): v.sort()
def last_club(i, y):                                                     # club at the time of the post (Jan 31 of y)
    v = [c for d, c in LAST.get(i, []) if d <= f"{y}-01-31" and c]; return v[-1] if v else None
tie_broken = []
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
        if len(c) > 1 and club_of(r.get('team')):                         # r48: same name, so keep the candidate who
            t = {i for i in c if last_club(i, y) == club_of(r['team'])}     # was last with that club
            if len(t) == 1: c = {i: c[i] for i in t}; tie_broken.append((y, r['name'], r['team'], next(iter(t))))
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
import os
json.dump(PUB, open(os.environ.get('OUT', 'published_service.json'), 'w'), indent=0, ensure_ascii=False)
print('rows', sum(len(v) for v in R.values()), 'matched', len(rows), 'unmatched', len(miss), 'ambiguous', len(amb), '| players', len(PUB))
print('tie broken by team heading', len(tie_broken)); json.dump(tie_broken, open('tie_broken.json', 'w'))
print('unmatched sample', miss[:8]); print('ambiguous sample', amb[:4])
