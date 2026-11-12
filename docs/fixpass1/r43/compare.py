# Round 43 item 3: what the innings fix changes in published numbers (Z_X6 = live engine run, D2 = same run with the fix)
import json, hashlib
B, D = '/tmp/sbx/runs/Z_X6/work/', '/tmp/sbx/runs/D2/work/'
def seats(p):
    s = {}
    for d, ss in json.load(open(p + 'trade_book.json'))['trades']:
        for st in ss: s[(d, st[0])] = s.get((d, st[0]), 0) + st[1]
    return s
sb, sd = seats(B), seats(D)
ch = [(k, round(sb.get(k, 0), 1), round(sd.get(k, 0), 1)) for k in set(sb) | set(sd) if round(sb.get(k, 0), 1) != round(sd.get(k, 0), 1)]
print('trade-side nets (shown to 0.1) that change:', len(ch), 'of', len(sb), '| largest raw change', round(max(abs(sd.get(k, 0) - sb.get(k, 0)) for k in sb), 3))
rows = lambda p: {(r[0], r[1]): r for r in json.load(open(p + 'offseasons.json'))['rows']}
ob, od = rows(B), rows(D)
wc = [(k, ob[k][9], od[k][9]) for k in ob if k in od and ob[k][9] != od[k][9]]
print('winter totals that change:', len(wc), 'of', len(ob), '| largest', max([abs(c[2] - c[1]) for c in wc] or [0]), wc[:5])
tor = [ob[k][9] for k in ob if k == ('TOR', 2012)], [od[k][9] for k in od if k == ('TOR', 2012)]; print('TOR 2012-13', tor)
def regs(p):
    out = {}
    for f in ('sweep_results.json', 'hist_results.json'):
        for r in json.load(open(p + f)):
            for k, c in (r.get('chan') or {}).items():
                if isinstance(c, dict) and c.get('net') is not None: out[(r['id'], k)] = (c['net'], c.get('n'))
    return out
rb, rd = regs(B), regs(D)
rc = [(k, rb[k][0], rd[k][0]) for k in rb if k in rd and round(rb[k][0], 1) != round(rd[k][0], 1)]
print('front office channel nets (shown to 0.1) that change:', len(rc), 'of', len(rb), '| largest', round(max(abs(rd[k][0] - rb[k][0]) for k in rb if k in rd), 3))
json.dump({'seats': ch, 'winters': wc, 'channels': rc}, open('/tmp/r43/ip/changes.json', 'w'), default=str)
