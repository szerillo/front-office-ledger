# trade pieces whose window ends in a season the player was released from BEFORE it started (release Jan-Mar),
# so the whole season (played for another club, or not at all) is credited to the trade
import json, sqlite3
from collections import defaultdict
c = sqlite3.connect('file:/tmp/v2/ledger_v3.sqlite?mode=ro', uri=True)
rel = defaultdict(list)
for pid, d in c.execute("select person_id, date from sweep_tx where type_desc='Released' and person_id is not null"): rel[int(pid)].append(d)
lv = json.load(open('/tmp/sbx/runs/Z_X6/work/lvm_cache.json'))
for name, path in (('live', '/home/claude/fol-main/trade_parts.json'), ('good7', '/tmp/deploy/good7/trade_parts.json')):
    P = json.load(open(path)); hit = []
    for k, v in P.items():
        if not v[3]: continue
        pid = int(k.split('|')[1]); end = v[3]
        sr = [d for d in rel.get(pid, []) if int(d[:4]) == end and d[5:7] <= '03' and d > k.split('|')[0]]
        if not sr: continue
        val = sum(r[2] for r in (lv.get(str(pid)) or {}).get('rows', []) if r[0] == end)
        hit.append((k, end, sr[0], round(val, 2)))
    print(name, 'pieces credited a season they were released before:', len(hit), '| that season\'s WAR summed', round(sum(h[3] for h in hit), 1), '| |WAR|>=0.5:', sum(abs(h[3]) >= 0.5 for h in hit))
    if name == 'good7':
        L = json.load(open('/home/claude/fol-main/trade_parts.json'))
        new = [h for h in hit if not (h[0] in L and L[h[0]][3] == h[1])]
        print('  new in good7 (from the re-sign rule):', len(new)); [print('   ', h) for h in new]
