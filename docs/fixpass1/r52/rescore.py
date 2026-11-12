# Round 52: re-score rule v1 on the 19-case frame with truth v2 (prereg_kinley_truth_v2.md); then size the
# under-20-day option rule on the 184-player frame. Rule and counters unchanged from round 50.
import json, sys, datetime, os
os.chdir('/tmp/r49/kinley'); sys.path.insert(0, '/tmp/r52')
exec(open('score.py').read().split("F = json.load(open('frame.json'))")[0])
from truth_v2 import truth_v2, spans, days_in
def active_days(pid, y, T):
    a, b = SF.SEAS[y]; n = (b - a).days + 1; days = [a + datetime.timedelta(days=i) for i in range(n)]
    clubs = {t['toTeam']['id'] for t in T if t['toTeam']['id'] in SF.MLB and (t['date'] or '')[:4] in (str(y - 1), str(y))}
    return {d for d in days for c in clubs if int(pid) in roster(c, d.isoformat(), 'active')}
F = json.load(open('frame.json')); out = []
for f in F:
    T = txs(f['pid']); y = f['season']
    old = SF.service(f['pid'], T).get(y, 0); R, log = resolve(f['pid'], T); new = SF.service(f['pid'], R).get(y, 0)
    tr, parts = truth_v2(f['pid'], T, SF.SEAS[y], SF.MLB, active_days(f['pid'], y, T))
    out.append({'pid': f['pid'], 'name': f['desc'].split(' assigned')[0], 'season': y, 'old': old, 'new': new, 'truth_v2': tr, 'parts': parts,
                'new_ok': abs(new - tr) <= 10, 'old_ok': abs(old - tr) <= 10})
json.dump(C, open(CACHE, 'w'))
for o in out: print(o['name'][:22].ljust(23), o['season'], 'old', o['old'], 'new', o['new'], 'truth_v2', o['truth_v2'], o['parts'], 'OK' if o['new_ok'] else 'MISS')
k = [o for o in out if o['pid'] == '641755'][0]
res = {'correct_new': sum(o['new_ok'] for o in out), 'n': len(out), 'correct_old': sum(o['old_ok'] for o in out), 'kinley_2026_new': k['new']}
print(res)
# option sizing on the 184 frame (transactions only; no roster calls)
C184 = json.load(open('/tmp/r45/svc/frame_tx.json')); rows = []
for pid, T in C184.items():
    T = [dict(t, toTeam={'id': t['toTeam']['id']}) for t in T]
    by = SF.service(pid, T)
    for y in sorted(SF.SEAS):
        il, dfa, opt = spans(T, SF.MLB, SF.SEAS[y]); a, b = SF.SEAS[y]; n = (b - a).days + 1
        od = days_in(opt, a, b)
        if 0 < len(od) < 20:
            add = min(172 - by.get(y, 0), round(len(od) * 186.0 / n)) if by.get(y, 0) < 172 else 0
            rows.append([pid, y, len(od), by.get(y, 0), max(0, add)])
sz = {'player_seasons_1_19_option_days': len(rows), 'players': len({r[0] for r in rows}), 'max_service_change_days': max((r[4] for r in rows), default=0),
      'total_days_added': sum(r[4] for r in rows), 'with_any_change': sum(1 for r in rows if r[4] > 0)}
print(sz)
json.dump({'rescore': out, 'summary': res, 'option_sizing': sz, 'option_rows': rows}, open('/tmp/r52/kinley_rescore.json', 'w'), indent=1)
