"""Round 14: the engine's same-club re-sign rule (asset_rules v6.0 _resign_skip), checked with the moves.js
stand-in for ledger.sqlite. Old: 3-field events (the rule never fires). New: 5-field events with the signing club
and the minor-league flag. Reports the trade sides that move and the Henriquez and Eli White sides."""
import sys, json, re
from collections import defaultdict
sys.path.insert(0, '/work'); import asset_rules as AR
src = open('/work/moves.js').read()
T = json.loads(re.search(r'PLAYER_MOVE_TYPES = (\[.*?\]);', src).group(1)); mv = json.loads(re.search(r'PLAYER_MOVES = (\{.*?\});\n', src, re.S).group(1))
mp = {'Declared Free Agency': 'Declared Free Agency', 'Released': 'Released', 'Signed as Free Agent': 'Signed as Free Agent', 'Minor-league deal': 'Signed as Free Agent'}
def build(new):
    ev = defaultdict(list)
    for p, rs in mv.items():
        for r in rs:
            t = T[r[1]]
            if t not in mp: continue
            held = r[2] or r[3]
            ev[int(p)].append((r[0], mp[t], held, r[3], t == 'Minor-league deal') if new else (r[0], mp[t], held))
    for v in ev.values(): v.sort()
    return ev
cfg = json.load(open('/work/regimes.json')); AB = {}
for r in cfg['regimes']: AB.setdefault(r['abbr'], set()).update(set(cfg['aliases'].get(str(r['teamId']), [])) | {r['team']})
tb = json.load(open('/work/trade_book.json')); NM = tb['names']
def run(new):
    AR._EVENTS = build(new); out = {}
    for i, (d, seats) in enumerate(tb['trades']):
        for ab, net, ins, outs in seats:
            for pid, v in ins:
                out[(i, ab, pid)] = AR.trade_window(int(pid), AB.get(ab, {ab}), d)[0]
    return out
old, new = run(False), run(True)
moved = {k: new[k] - old[k] for k in old if abs(new[k] - old[k]) > 1e-9}
side = defaultdict(float)
for (i, ab, pid), dv in moved.items():
    side[(i, ab)] += dv
    giver = next((s[0] for s in tb['trades'][i][1] if any(q[0] == pid for q in s[3])), None)
    if giver: side[(i, giver)] -= dv
print('pieces whose trade value changes:', len(moved), '| trade sides:', len({k for k in side}))
for (i, ab), dv in sorted(side.items(), key=lambda kv: -abs(kv[1])):
    net = next(s[1] for s in tb['trades'][i][1] if s[0] == ab)
    print(f"  {tb['trades'][i][0]} {ab}: net {net:+.1f} to {net + dv:+.1f} ({dv:+.2f})")
