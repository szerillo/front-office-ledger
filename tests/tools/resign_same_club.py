"""Size the 'released or non-tendered, then re-signed by the same club' gap (Nov 11 round 11).
The engine (asset_rules.trade_window) and the page's OPEN rule end a traded piece's window at his first
release or free-agent filing. When the club holding him re-signs him within 60 days (a non-tender and
minor-league re-sign: Domingo German 2015, Eli White 2023), the window should go on. Counts traded pieces
where that happens and the value he produced for that club afterwards, inside six seasons from the trade.
Report only."""
import json, re, sys
from datetime import date
sys.path.insert(0, '/work'); import asset_rules as AR
src = open('/work/moves.js').read()
T = json.loads(re.search(r'PLAYER_MOVE_TYPES = (\[.*?\]);', src).group(1)); mv = json.loads(re.search(r'PLAYER_MOVES = (\{.*?\});\n', src, re.S).group(1))
cfg = json.load(open('/work/regimes.json')); AB = {}
for r in cfg['regimes']: AB.setdefault(r['abbr'], set()).update(set(cfg['aliases'].get(str(r['teamId']), [])) | {r['team']})
tb = json.load(open('/work/trade_book.json')); NM = tb['names']
D = lambda s: date(int(s[:4]), int(s[5:7]), int(s[8:10]))
hits = []
for d, seats in tb['trades']:
    for ab, net, ins, outs in seats:
        for pid, v in ins:
            rows = [(r[0], T[r[1]], r[2], r[3]) for r in mv.get(str(pid), [])]
            later = [r for r in rows if r[0] > d]
            # stop at his next trade or claim: a flip is graded in the flip
            stop = next((k for k, r in enumerate(later) if r[1] in ('Trade', 'Claimed Off Waivers', 'Rule 5 Selection')), len(later))
            later = later[:stop]
            i = next((k for k, r in enumerate(later) if r[1] in ('Released', 'Declared Free Agency')), None)
            if i is None: continue
            e = later[i]
            nxt = next((r for r in later[i + 1:] if r[1] in ('Signed as Free Agent', 'Minor-league deal')), None)
            if not nxt or nxt[3] != ab or (D(nxt[0]) - D(e[0])).days > 60: continue
            # only a player still inside his original control (a non-tender or release and re-sign); a free
            # agent with six years who re-signs is a new signing, graded on its own
            ce = AR.control_end(int(pid))
            if ce is None or int(e[0][:4]) + (1 if int(e[0][5:7]) >= 10 else 0) > ce: continue
            y0 = int(d[:4]) + (1 if int(d[5:7]) >= 10 else 0); ye = int(e[0][:4]) + (1 if int(e[0][5:7]) >= 10 else 0)
            names = AB.get(ab, {ab})
            war = sum(val for yr, tm, val in (AR._lvm().get(int(pid)) or {}).get('rows', []) if tm in names and ye <= yr <= min(y0 + 5, 2026))
            hits.append((d, ab, pid, NM.get(str(pid), pid), e[0], e[1], nxt[0], round(war, 1)))
print('traded pieces inside club control re-signed by the same club within 60 days of a release or filing:', len(hits))
print('  trades:', len({(h[0], h[1]) for h in hits}), '| with 1.0+ value after the re-sign inside six seasons:',
      sum(1 for h in hits if h[7] >= 1.0), '| total value after re-sign: %.1f' % sum(h[7] for h in hits))
for h in sorted(hits, key=lambda h: -h[7])[:15]: print(' ', *h)
