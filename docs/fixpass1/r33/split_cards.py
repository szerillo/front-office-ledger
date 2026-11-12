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
# merge only when both parts ran AND every club is present (CARD_CLUBS is set by both parts)
GATE = ("\nwindow.CARD_CLUBS = " + str(len(keys)) + "; window.CARD_PARTS = (window.CARD_PARTS || 0) + 1;\n"
        "if(window.CARD_PARTS === 2 && Object.keys(window.CARD_DETAIL).length === window.CARD_CLUBS && typeof cardsMerge === 'function') cardsMerge();\n")
part = lambda o: 'window.CARD_DETAIL = Object.assign(window.CARD_DETAIL || {}, ' + dump(o) + ');' + GATE
js2 = part(p2)
h2 = hashlib.md5(js2.encode('utf-8')).hexdigest()[:10]
# Nov 12 (round 33): the second part is named by its content hash (cards2.<md5[:10]>.js), not ?v=, so a cached
# cards.js can only ever fetch the part it was built with, across a deploy or a rollback. One retry after 1.5 s;
# a second failure shows the same "did not finish loading" banner the page's loader uses, at once.
name2 = 'cards2.' + h2 + '.js'
LOADER = ("(function(){ var tries = 0; var go = function(){ var c = document.createElement('script'); c.src = '" + name2 + "' + (tries ? '?r=' + tries : '');\n"
  "  c.onerror = function(){ if(++tries < 2) return setTimeout(go, 1500); if(window.CARDS_READY || document.getElementById('cards-fail')) return;\n"
  "    var d = document.createElement('div'); d.id = 'cards-fail'; d.setAttribute('role', 'alert');\n"
  "    d.style.cssText = 'position:fixed; left:12px; right:12px; bottom:76px; z-index:95; max-width:520px; margin:0 auto; background:var(--surface); color:var(--ink); border:1.5px solid var(--ink); border-radius:8px; padding:10px 14px; box-shadow:0 8px 24px rgba(0,0,0,.2); display:flex; gap:10px; align-items:center; font-size:14px';\n"
  "    d.innerHTML = '<span style=\"flex:1\">Report cards, trees and scenarios did not finish loading.</span><button onclick=\"location.reload()\" style=\"cursor:pointer; font:700 13px var(--f-body); padding:8px 14px; border-radius:6px; border:1px solid var(--ink); background:var(--ink); color:var(--page)\">Retry</button>';\n"
  "    document.body.appendChild(d); };\n"
  "  document.body.appendChild(c); }; go(); })();\n")
js1 = LOADER + part(p1)
open(out + '/cards.js', 'w', encoding='utf-8').write(js1)
open(out + '/' + name2, 'w', encoding='utf-8').write(js2)
h1 = hashlib.md5(js1.encode('utf-8')).hexdigest()[:10]
pg = open(out + '/index.html', encoding='utf-8').read()
old = hashlib.md5(s.encode('utf-8')).hexdigest()[:10]
a = "c.src = 'cards.js?v=" + old + "'"; assert pg.count(a) == 1, 'cards.js stamp'
open(out + '/index.html', 'w', encoding='utf-8').write(pg.replace(a, "c.src = 'cards.js?v=" + h1 + "'"))
# the two halves must rebuild the original exactly
assert dump({**p1, **p2}) == body
print('cards split', cut, len(keys) - cut, len(js1.encode()), len(js2.encode()), h1, name2)
