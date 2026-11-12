# Round 49 shared readers: graded values of one run, with letters from the LIVE (Z_X6) spread and cutoffs.
import json, statistics
Z = '/tmp/sbx/runs/Z_X6/work/'
N = json.load(open('/tmp/r40/a/new.json')); ZC = N['Z']; ROWS = N['rows']
def recs(p):
    o = {}
    for f in ('sweep_results.json', 'hist_results.json'):
        for r in json.load(open(p + f)): o[r['id']] = r
    return o
def nets(R): return {(i, k): c['net'] for i, r in R.items() for k, c in (r.get('chan') or {}).items() if isinstance(c, dict) and c.get('net') is not None}
def letter(z):
    for cut, g in ZC:
        if z >= cut: return g
    return ZC[-1][1] - 5
def spread(n): return {k: statistics.pstdev([n[(r['id'], k)] / r['S'] for r in ROWS if r['k'] == k and (r['id'], k) in n]) for k in {r['k'] for r in ROWS}}
SD_LIVE = spread(nets(recs(Z)))
def letters(n, sd=None):
    sd = sd or SD_LIVE
    return {(r['id'], r['k']): letter(n[(r['id'], r['k'])] / (sd[r['k']] * r['S'])) for r in ROWS if (r['id'], r['k']) in n}
def seatnets(p):
    s = {}
    for d, seats in json.load(open(p + 'trade_book.json'))['trades']:
        for st in seats: s[(d, st[0])] = round(s.get((d, st[0]), 0) + st[1], 6)
    return s
def winters(p): return {(r[0], r[1]): r[9] for r in json.load(open(p + 'offseasons.json'))['rows']}
def ranks(R, key):
    v = sorted(((key(r), i) for i, r in R.items() if r.get('seasons') is not None), reverse=True)
    return {i: n for n, (_, i) in enumerate(v)}
def snapshot(p):
    R = recs(p); n = nets(R)
    return {'R': R, 'nets': n, 'letters': letters(n), 'overall': {i: r.get('forGrade') for i, r in R.items()},
            'totals': {i: r.get('total') for i, r in R.items()}, 'seats': seatnets(p), 'winters': winters(p),
            'rank_overall': ranks(R, lambda r: r['total'] / (r['seasons'] + 2)),
            'rank_ext': ranks(R, lambda r: (r['chan'].get('ext') or {}).get('net', 0) / (r['seasons'] + 2))}
def diff(a, b, keys=('nets', 'letters', 'overall', 'totals', 'seats', 'winters', 'rank_overall', 'rank_ext')):
    return {k: sorted([x for x in set(a[k]) | set(b[k]) if a[k].get(x) != b[k].get(x)], key=str) for k in keys}
