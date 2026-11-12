import json, statistics, sys
sys.path.insert(0,'/tmp/r45/a')
N = json.load(open('/tmp/r40/a/new.json')); Z = N['Z']
def regs(p):
    out = {}
    for f in ('sweep_results.json', 'hist_results.json'):
        for r in json.load(open(p + f)):
            for k, c in (r.get('chan') or {}).items():
                if isinstance(c, dict) and c.get('net') is not None: out[(r['id'], k)] = c['net']
    return out
def letter(z):
    for cut, g in Z:
        if z >= cut: return g
    return Z[-1][1] - 5
def grade(nets, rows):
    sd = {}
    for k in {r['k'] for r in rows}:
        v = [nets[(r['id'], k)] / r['S'] for r in rows if r['k'] == k and (r['id'], k) in nets]
        sd[k] = statistics.pstdev(v)
    return {(r['id'], r['k']): letter(nets[(r['id'], r['k'])] / (sd[r['k']] * r['S'])) for r in rows if (r['id'], r['k']) in nets}, sd
rows = N['rows']
nb = regs('/tmp/sbx/runs/Z_X6/work/'); nc = regs('/tmp/sbx/runs/C1/work/')
print('rows matched base', sum((r['id'], r['k']) in nb for r in rows), 'of', len(rows))
gb, sdb = grade(nb, rows); gc, sdc = grade(nc, rows)
print('SD given', {k: round(v, 3) for k, v in N['SD'].items()}); print('SD base ', {k: round(v, 3) for k, v in sdb.items()}); print('SD C1   ', {k: round(v, 3) for k, v in sdc.items()})
rep = sum(gb[(r['id'], r['k'])] == r['g'] for r in rows if (r['id'], r['k']) in gb); print('base replication', rep, 'of', len(gb))
ch = [(k, gb[k], gc[k]) for k in gb if k in gc and gb[k] != gc[k]]
print('channel letters that change with control end +1:', len(ch), 'of', len(gb))
pages = sorted({k[0] for k, _, _ in ch}); print('pages (front offices/clubs) with a changed letter:', len(pages), 'of', len({r['id'] for r in rows}))
json.dump({'letters': ch, 'pages': pages}, open('/tmp/r45/a/letters.json', 'w'))
