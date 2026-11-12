# Nov 12 (round 40, staged, not deployed): name every build data file by its content hash, like cards2 already is.
# A deploy then only ADDS files; it never rewrites a file an older index.html still points at, so a visitor who
# gets the old page during the Pages rollout gets the old data with it (no mixed window).
# Usage: hash_names.py <site dir>. Writes <stem>.<md5[:10]><ext> beside each file (the plain-named file stays, for
# tools and for the old page), and rewrites index.html to load the hashed names. Run after split_cards.py.
# Files the daily jobs rewrite in place (rumors.json, share.json, wire.json) keep their names; the page fetches
# them with a fresh query and they carry their own stamps.
import hashlib, os, re, shutil, sys
d = sys.argv[1]
BUILD = ['cards.js', 'moves.js', 'book.js', 'deals.js', 'offseasons.json', 'trade_parts.json', 'dudes.json']
pg_path = os.path.join(d, 'index.html'); pg = open(pg_path, encoding='utf-8').read()
for f in BUILD:
    p = os.path.join(d, f); stem, ext = os.path.splitext(f)
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()[:10]; new = f'{stem}.{h}{ext}'
    shutil.copyfile(p, os.path.join(d, new))
    pat = re.compile(r"(?<![\w.])" + re.escape(f) + r"(?:\?v=[0-9a-zA-Z]+)?(?=['\"`])")
    pg, n = pat.subn(new, pg)
    if n != 1: sys.exit(f'{f}: expected 1 reference in index.html, found {n}')
    print(f'{f} -> {new}')
open(pg_path, 'w', encoding='utf-8').write(pg)
