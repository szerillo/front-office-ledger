# deploy assembly: wrap the data blocks the live page parses with JSON.parse, then split_book.py, then copy data files
import json, sys, subprocess, shutil, os
src, run, out = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
def wrap(s, name):
    k = s.index('\nconst ' + name + ' = ') + 1; e = s.index('\n', k); body = s[k:e][len('const ' + name + ' = '):].rstrip()
    if body.startswith('JSON.parse('): return s
    obj = json.loads(body[:-1])
    t = json.dumps(obj, separators=(',', ':'), ensure_ascii=False).replace('\\', '\\\\').replace("'", "\\'").replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    return s[:k] + 'const ' + name + " = JSON.parse('" + t + "');" + s[e:]
# page fix (Nov 11, t_winter holmesPiecesCurrent): a free-agency filing after the 2026 season is not a departure and
# return; keep "Finished 2026 with X" instead of rewriting it to "Back with X by 2026" (Tyrone Taylor, filed Oct 29)
OLD = "node.kids = [{nm: f.nm.replace(/^Finished 2026 with ([A-Z]+)/, 'Back with $1 by 2026'), wv: null, status: f.status}];"
NEW = "const winterFA = m[1] === 'Declared Free Agency' && m[0] >= '2026-10-01';   // filed after the season: he finished it here\n    node.kids = [{nm: winterFA ? f.nm : f.nm.replace(/^Finished 2026 with ([A-Z]+)/, 'Back with $1 by 2026'), wv: null, status: f.status}];"
assert s.count(OLD) == 1, 'holmes fix anchor'
s = s.replace(OLD, NEW)
for n in ['AUTO_REGIMES', 'DESK', 'FA_SKILL', 'LB_HIST', 'PLAYER_NAMES', 'TEAM_WL', 'TRADE_STAR', 'TRADE_BOOK', 'PLAYER_FATE', 'QUIZ_CTX']: s = wrap(s, n)
os.makedirs(out, exist_ok=True); tmp = out + '/_page.html'; open(tmp, 'w', encoding='utf-8').write(s)
subprocess.run(['python3', '/home/claude/fol-main/engine/split_book.py', tmp, out], check=True); os.remove(tmp)
for f in ['cards.js', 'moves.js', 'offseasons.json', 'trade_parts.json']: shutil.copy(f'{run}/{f}', out)
# Nov 12: offseasons.json and trade_parts.json were fetched as ?v=1, so a returning visitor (Pages max-age=600) could
# get the new page with the old winter data; stamp them with their content hash like cards.js
import hashlib
pg = open(out + '/index.html', encoding='utf-8').read()
for f in ['offseasons.json', 'trade_parts.json']:
    h = hashlib.md5(open(f'{out}/{f}', 'rb').read()).hexdigest()[:10]
    assert pg.count(f + '?v=1') == 1, f
    pg = pg.replace(f + '?v=1', f + '?v=' + h)
open(out + '/index.html', 'w', encoding='utf-8').write(pg)
