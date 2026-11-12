# Nov 12 (round 34): every content stamp in the built site is recomputed from the final bytes on disk.
# index.html: <file>?v=<10 hex> must be the md5 (or sha1, deals.js/book.js) prefix of that file.
# cards.js: the second part it loads, cards2.<10 hex>.js, must exist and its md5 prefix must equal the name.
# Exit 4 on any mismatch. Usage: verify_stamps.py <site dir>
import hashlib, os, re, sys
d = sys.argv[1]; bad = []; ok = []
h = lambda p: (hashlib.md5(open(p, 'rb').read()).hexdigest(), hashlib.sha1(open(p, 'rb').read()).hexdigest())
pg = open(os.path.join(d, 'index.html'), encoding='utf-8').read()
for f, v in sorted(set(re.findall(r"([\w.]+\.(?:js|json))\?v=([0-9a-f]{10})\b", pg))):
    p = os.path.join(d, f)
    if not os.path.isfile(p): bad.append(f'{f}?v={v}: file missing'); continue
    m, s = h(p)
    (ok if v in (m[:10], s[:10]) else bad).append(f'{f}?v={v} (md5 {m[:10]}, sha1 {s[:10]})')
cj = open(os.path.join(d, 'cards.js'), encoding='utf-8').read()
parts = re.findall(r"'(cards2\.([0-9a-f]{10})\.js)'", cj)
if not parts: bad.append('cards.js names no cards2.<hash>.js part')
for name, v in parts:
    p = os.path.join(d, name)
    if not os.path.isfile(p): bad.append(f'{name}: file missing'); continue
    m = h(p)[0]; (ok if m[:10] == v else bad).append(f'{name} (md5 {m[:10]})')
print('stamps checked:', len(ok) + len(bad))
if bad: print('STAMP CHECK RED:', '; '.join(bad)); sys.exit(4)
print('stamp check green:', '; '.join(ok))
