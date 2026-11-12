# Round 49 Kinley prereg (b2477dc): frame = service-pool players with "elected free agency" followed by an assignment
# to an MLB club before the next Opening Day, seasons 2015 to 2026. Built from the ledger's transaction sweep.
import json, sqlite3, importlib.util, collections
spec = importlib.util.spec_from_file_location('sf', '/tmp/r48/eng/svc_fetch.py'); SF = importlib.util.module_from_spec(spec); spec.loader.exec_module(SF)
db = sqlite3.connect('/tmp/v2/ledger_v3.sqlite')
desk = json.load(open('/tmp/r46/pub/desk.json'))['players']; lvm = json.load(open('/work/lvm_cache.json'))
pool = {str(p[1]) for p in desk if isinstance(lvm.get(str(p[1])), dict) and lvm[str(p[1])].get('rows') and min(r[0] for r in lvm[str(p[1])]['rows']) >= 2014}
OD = {y: SF.SEAS[y][0].isoformat() for y in SF.SEAS}
rows = collections.defaultdict(list)
for pid, d, desc, tid, to in db.execute("select person_id, date, description, team_id, to_team from sweep_tx where person_id is not null and date >= '2014-10-01'"):
    if pid in pool: rows[pid].append((d, desc or '', tid, to or ''))
frame = []
for pid, L in rows.items():
    L = sorted(set(L))
    for i, (d, desc, tid, to) in enumerate(L):
        if 'elected free agency' not in desc.lower(): continue
        y = int(d[:4]) + (1 if d[5:7] >= '08' else 0)          # the season that follows
        if y not in OD or not (2015 <= y <= 2026): continue
        for d2, desc2, tid2, to2 in L[i + 1:]:
            if d2 >= OD[y]: break
            if ' assigned to ' in (' ' + desc2.lower()) and tid2 in SF.MLB and to2 and 'assigned to ' + to2.lower() in desc2.lower():
                frame.append({'pid': pid, 'efa': d, 'asg': d2, 'club': tid2, 'season': y, 'desc': desc2[:100]}); break
seen = set(); F = []
for f in frame:
    k = (f['pid'], f['season'])
    if k not in seen: seen.add(k); F.append(f)
json.dump(F, open('frame.json', 'w'), indent=0)
print('pool', len(pool), 'frame (player-seasons)', len(F), 'example', F[:2])
