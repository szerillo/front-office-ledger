# Every winter share page (o/<year>-<club>.html) must show the same total as the site's offseasons.json.
# Usage: winter_pages_check.py <site tree> [offseasons.json, default the tree's own]. Exit 6 on any mismatch.
import json, os, re, sys
d = sys.argv[1]; off = sys.argv[2] if len(sys.argv) > 2 else os.path.join(d, 'offseasons.json')
rows = json.load(open(off))['rows']; tot = {(r[0], r[1]): r[9] for r in rows}
alias = {'ATH': ['ATH', 'OAK'], 'OAK': ['OAK', 'ATH']}
bad, n = [], 0
for f in sorted(os.listdir(os.path.join(d, 'o'))):
    if not f.endswith('.html'): continue
    y, ab = f[:-5].split('-', 1); s = open(os.path.join(d, 'o', f), encoding='utf-8').read()
    m = re.search(r'<title>[^<]*?([+-]?\d+\.\d) wins in one winter', s)
    if not m: bad.append(f'{f}: no number in title'); continue
    n += 1; v = float(m.group(1))
    t = next((tot[(a, int(y))] for a in alias.get(ab.upper(), [ab.upper()]) if (a, int(y)) in tot), None)
    if t is None or abs(round(t, 1) - v) > 0.05: bad.append(f'{f}: page {v:+.1f}, data {t}')
print(f'winter pages: {n} checked, {len(bad)} differ from {os.path.basename(off)}')
for b in bad: print('  ', b)
sys.exit(6 if bad else 0)
