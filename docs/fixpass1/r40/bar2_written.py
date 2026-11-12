# Bar 2 as written in dd3d4a8: a seat that moves 0.05+ in a trade that holds no listed piece fails the bar.
# (bars.py's "unlisted" line used the estimate's seat list instead; that gave 24 and is withdrawn.)
# Also answers round 40 item 2: how many public numbers the rule would change.
import json
B, R0 = '/tmp/sbx/runs/Z_X6/work', '/tmp/sbx/runs/P0/work'
est = json.load(open('/tmp/prereg/estimate.json'))
listed = {f'{d}|{p}|{c}' for d, p, c, e, w in est['hits']}
def book(path):
    out = {}
    for d, ss in json.load(open(path + '/trade_book.json'))['trades']:
        pids = {x[0] for st in ss for x in st[2] + st[3]}
        for st in ss: out.setdefault((d, st[0]), [0, set()]); out[(d, st[0])][0] += st[1]; out[(d, st[0])][1] |= pids
    return out
SB, S0 = book(B), book(R0)
lp = {(k.split('|')[0], k.split('|')[1]) for k in listed}
moved = {k: S0.get(k, [0])[0] - SB.get(k, [0])[0] for k in set(SB) | set(S0) if abs(S0.get(k, [0])[0] - SB.get(k, [0])[0]) >= 0.05}
nolisted = sorted((k, round(v, 2)) for k, v in moved.items() if not any((k[0], p) in lp for p in (SB.get(k) or S0[k])[1]))
print('BAR 2 (as written): seats moved', len(moved), '; in a trade with no listed piece', len(nolisted), nolisted, '->', 'FAIL' if nolisted else 'PASS')
# public numbers: trade seat nets as shown (1 decimal) and winter totals as shown
shown = sum(1 for k in set(SB) | set(S0) if round(SB.get(k, [0])[0], 1) != round(S0.get(k, [0])[0], 1))
rows = lambda p: {(r[0], r[1], r[3]): r for r in json.load(open(p + '/offseasons.json'))['rows']}   # [ab, winter, exec, id, tradeNet, nT, faNet, nFA, faM, total, ...]
ob, o0 = rows(B), rows(R0)
wint = [(k[0], k[1], ob[k][9], o0[k][9]) for k in ob if k in o0 and (ob[k][4], ob[k][6], ob[k][9]) != (o0[k][4], o0[k][6], o0[k][9])]
print('PUBLIC: trade seat nets that change at 1 decimal:', shown)
print('PUBLIC: winter totals that change:', len(wint), 'largest', max(abs(c[3] - c[2]) for c in wint), [c for c in wint if c[0] == 'ATH' and c[1] == 2011])
