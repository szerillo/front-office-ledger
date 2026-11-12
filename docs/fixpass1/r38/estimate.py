# Static estimate (no engine run) of the pre-season-release fix: a release in Jan-Mar ends a window with the PRIOR
# season, as a free-agent signing already does (asset_rules.py:363). For every live trade piece whose window ends in a
# season he was released before it started, take that season's Ledger WAR off the receiving club's seat and give it
# back to the club(s) that sent him; then count seat letters near a band edge, winter tier labels and regime trade nets.
import json, re, sqlite3
from collections import defaultdict
S = '/tmp/deploy/good7'   # = live since 8de35fd
TB = json.load(open('/tmp/prereg/tb.json'))   # TRADE_BOOK from the live book.js (node vm)
P = json.load(open(S + '/trade_parts.json')); lv = json.load(open('/tmp/sbx/runs/Z_X6/work/lvm_cache.json'))
c = sqlite3.connect('file:/tmp/v2/ledger_v3.sqlite?mode=ro', uri=True); rel = defaultdict(list)
for pid, d in c.execute("select person_id, date from sweep_tx where type_desc='Released' and person_id is not null"): rel[int(pid)].append(d)
hits = []
for k, v in P.items():
    if not v[3]: continue
    d0, pid, club = k.split('|'); end = v[3]
    sr = [d for d in rel.get(int(pid), []) if int(d[:4]) == end and d[5:7] <= '03' and d > d0]
    if sr: hits.append((d0, pid, club, end, sum(r[2] for r in (lv.get(pid) or {}).get('rows', []) if r[0] == end)))
seat = defaultdict(float)
trades = {d: s for d, s in TB['trades']} if isinstance(TB['trades'][0][0], str) else {}
bydate = defaultdict(list)
for d, s in TB['trades']: bydate[d].append(s)
for d0, pid, club, end, war in hits:
    seat[(d0, club)] -= war
    senders = [st[0] for ss in bydate.get(d0, []) for st in ss if any(p[0] == pid for p in st[3])]
    for snd in senders: seat[(d0, snd)] += war / len(senders)
moved = {k: v for k, v in seat.items() if abs(v) >= 0.05}
print('pieces', len(hits), '| seats moved', len(moved), '| seats moved 0.5+', sum(abs(v) >= 0.5 for v in moved.values()), '| largest', sorted(moved.items(), key=lambda x: -abs(x[1]))[:5])
# winters: a trade dated Oct-Mar belongs to the winter that starts in the autumn (rows keyed by start year)
off = json.load(open(S + '/offseasons.json'))['rows']; tot = {(r[0], r[1]): r[9] for r in off if r[9] is not None}
def wyear(d): y, m = int(d[:4]), int(d[5:7]); return y if m >= 10 else y - 1 if m <= 3 else None
wd = defaultdict(float)
for (d0, club), v in moved.items():
    y = wyear(d0)
    if y is not None and (club, y) in tot: wd[(club, y)] += v
stamp = lambda v: 'All-timer' if v >= 20 else 'Great winter' if v >= 10 else 'Good winter' if v >= 3 else 'A wash' if v > -3 else 'Bad winter' if v > -10 else 'Disaster' if v > -20 else 'Catastrophe'
tiers = [(k, round(tot[k], 1), round(tot[k] + v, 1)) for k, v in wd.items() if stamp(tot[k]) != stamp(tot[k] + v)]
print('winters moved', len(wd), '| tier labels that would change', len(tiers), tiers)
best = sorted(tot.items(), key=lambda x: -x[1])[:2]; adj = {k: tot[k] + wd.get(k, 0) for k in tot}
print('No. 1 now', best[0], '| after estimate', sorted(adj.items(), key=lambda x: -x[1])[:2])
NOTE = {'CHC', 'MIL', 'PIT', 'PHI', 'SF', 'WSH', 'SEA', 'TOR', 'LAA'}
print('seats in note clubs', sorted({(k[1]) for k in moved if k[1] in NOTE}), '| sum by club', {c_: round(sum(v for k, v in moved.items() if k[1] == c_), 2) for c_ in sorted(NOTE) if any(k[1] == c_ for k in moved)})
json.dump({'hits': hits, 'seats': {f'{k[0]}|{k[1]}': v for k, v in moved.items()}, 'tiers': tiers}, open('/tmp/prereg/estimate.json', 'w'))
