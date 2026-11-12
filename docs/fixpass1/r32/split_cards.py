# Deploy step (Nov 12, Option A): cards.js is 3.97 MB, over the 3.6 MB a single upload can carry.
# Split CARD_DETAIL into cards.js (first half of the clubs) and cards2.js (the rest). cards.js starts
# cards2.js, so the page's loader and page code do not change; only the cards.js ?v= stamp moves.
# Whichever part runs second calls cardsMerge(), so the merge always sees every club.
# Usage: python3 split_cards.py <site dir>   (rewrites cards.js, writes cards2.js, restamps index.html)
import hashlib, json, sys
out = sys.argv[1]
s = open(out + '/cards.js', encoding='utf-8').read()
HEAD, TAIL = 'window.CARD_DETAIL = ', ";\nif(typeof cardsMerge === 'function') cardsMerge();"
assert s.startswith(HEAD) and s.rstrip('\n').endswith(TAIL), 'cards.js shape'
body = s[len(HEAD):s.rindex(TAIL)]
obj = json.loads(body)
dump = lambda o: json.dumps(o, separators=(',', ':'), ensure_ascii=False)
assert dump(obj) == body, 'cards.js is not compact JSON; the split could change bytes'
keys = list(obj); half = len(body.encode('utf-8')) / 2; acc = 0; cut = len(keys)
for n, k in enumerate(keys):
    acc += len(dump({k: obj[k]}).encode('utf-8'))
    if acc >= half: cut = n + 1; break
p1, p2 = {k: obj[k] for k in keys[:cut]}, {k: obj[k] for k in keys[cut:]}
GATE = "\nwindow.CARD_PARTS = (window.CARD_PARTS || 0) + 1;\nif(window.CARD_PARTS === 2 && typeof cardsMerge === 'function') cardsMerge();\n"
part = lambda o: 'window.CARD_DETAIL = Object.assign(window.CARD_DETAIL || {}, ' + dump(o) + ');' + GATE
js2 = part(p2)
h2 = hashlib.md5(js2.encode('utf-8')).hexdigest()[:10]
js1 = ("(function(){ var c = document.createElement('script'); c.src = 'cards2.js?v=" + h2 + "'; document.body.appendChild(c); })();\n"
       + part(p1))
open(out + '/cards.js', 'w', encoding='utf-8').write(js1)
open(out + '/cards2.js', 'w', encoding='utf-8').write(js2)
h1 = hashlib.md5(js1.encode('utf-8')).hexdigest()[:10]
pg = open(out + '/index.html', encoding='utf-8').read()
old = hashlib.md5(s.encode('utf-8')).hexdigest()[:10]
a = "c.src = 'cards.js?v=" + old + "'"; assert pg.count(a) == 1, 'cards.js stamp'
open(out + '/index.html', 'w', encoding='utf-8').write(pg.replace(a, "c.src = 'cards.js?v=" + h1 + "'"))
# the two halves must rebuild the original exactly
assert dump({**p1, **p2}) == body
print('cards split', cut, len(keys) - cut, len(js1.encode()), len(js2.encode()), h1, h2)
