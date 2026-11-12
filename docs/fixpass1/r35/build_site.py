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
# Nov 12 (round 34): the Deal Desk GM line printed g2letter(null) = "F" for a GM with deals but no grade (the site
# grades a channel only at 3+ deals and never in a new seat: MIN_N, applyGradePolicy). Say "too few to grade" instead.
OLD2 = "${r.chan.trade.n ? `trade grade ${g2letter(r.chan.trade.g)} over ${pz(r.chan.trade.n,'deal','deals')}` : 'new in the seat, no trades graded yet'}"
NEW2 = "${r.chan.trade.n && r.chan.trade.g != null ? `trade grade ${g2letter(r.chan.trade.g)} over ${pz(r.chan.trade.n,'deal','deals')}` : r.chan.trade.n ? `${pz(r.chan.trade.n,'deal','deals')} so far, too few to grade` : 'new in the seat, no trades graded yet'}"
assert s.count(OLD2) == 1, 'desk GM line anchor'
s = s.replace(OLD2, NEW2)
# Nov 12 (round 35): a missing grade must never print as "F". g2letter(null) fell through every comparison to "F"
# (live today: Mozeliak's LAA report card, player development "F" with no prospects graded). Fix at the source:
# no grade -> the same middle dot the report-card chips use for "not graded", grey class, and a plain tooltip.
FIXES = [
 ("const g2letter = g => g>=80?", "const g2letter = g => (g == null || !isFinite(g)) ? '·' : g>=80?"),
 ("const gradeClass = g => g>=70?", "const gradeClass = g => (g == null || !isFinite(g)) ? 'gnone' : g>=70?"),
 ("function deskLetter(rel, cost){\n  const r = rel / Math.max(cost, 1);\n", "function deskLetter(rel, cost){\n  const r = rel / Math.max(cost, 1);\n  if(!isFinite(r)) return '·';\n"),
 ("function letterClass(g){ return /^A/.test(g) ?", "function letterClass(g){ return g === '·' || g == null ? 'gnone' : /^A/.test(g) ?"),
 ('<span class="grade ${gradeClass(s.g || 50)} pop" style="font-size:26px; padding:4px 14px">${g2letter(s.g || 50)}</span>', '<span class="grade ${gradeClass(s.g)} pop" style="font-size:26px; padding:4px 14px">${g2letter(s.g)}</span>'),
 ('title="${dv.g} on the 20–80 scouting scale">${g2letter(dv.g)}', 'title="${dv.g == null ? \'Not graded yet: no prospects to grade in this seat\' : dv.g + \' on the 20–80 scouting scale\'}">${g2letter(dv.g)}'),
]
for a, b in FIXES:
    assert s.count(a) == 1, a[:40]
    s = s.replace(a, b)
for n in ['AUTO_REGIMES', 'DESK', 'FA_SKILL', 'LB_HIST', 'PLAYER_NAMES', 'TEAM_WL', 'TRADE_STAR', 'TRADE_BOOK', 'PLAYER_FATE', 'QUIZ_CTX']: s = wrap(s, n)
os.makedirs(out, exist_ok=True); tmp = out + '/_page.html'; open(tmp, 'w', encoding='utf-8').write(s)
subprocess.run(['python3', '/home/claude/fol-main/engine/split_book.py', tmp, out], check=True); os.remove(tmp)
for f in ['cards.js', 'moves.js', 'offseasons.json', 'trade_parts.json']: shutil.copy(f'{run}/{f}', out)
# Nov 12 (Option A): cards.js is over the 3.6 MB a single upload can carry; split it in two
if os.environ.get('NO_CARD_SPLIT') != '1': subprocess.run(['python3', os.path.dirname(os.path.abspath(__file__)) + '/split_cards.py', out], check=True)
# Nov 12: offseasons.json and trade_parts.json were fetched as ?v=1, so a returning visitor (Pages max-age=600) could
# get the new page with the old winter data; stamp them with their content hash like cards.js
import hashlib
pg = open(out + '/index.html', encoding='utf-8').read()
for f in ['offseasons.json', 'trade_parts.json']:
    h = hashlib.md5(open(f'{out}/{f}', 'rb').read()).hexdigest()[:10]
    assert pg.count(f + '?v=1') == 1, f
    pg = pg.replace(f + '?v=1', f + '?v=' + h)
open(out + '/index.html', 'w', encoding='utf-8').write(pg)

# Nov 12: headroom check. Every site file must stay under 3.4 MB (the upload tool takes 3.6 MB), or the build goes red
LIMIT = int(os.environ.get('SIZE_LIMIT', 3400000))
big = [(f, os.path.getsize(os.path.join(out, f))) for f in sorted(os.listdir(out)) if os.path.isfile(os.path.join(out, f)) and os.path.getsize(os.path.join(out, f)) > LIMIT]
if big: print('SIZE CHECK RED:', ', '.join(f'{f} {n:,} bytes' for f, n in big)); sys.exit(3)
print('size check green: largest', max((os.path.getsize(os.path.join(out, f)), f) for f in os.listdir(out) if os.path.isfile(os.path.join(out, f))))
# Nov 12 (round 34): recompute every content stamp from the final bytes; red (exit 4) on any mismatch
subprocess.run(['python3', os.path.dirname(os.path.abspath(__file__)) + '/verify_stamps.py', out], check=True)
