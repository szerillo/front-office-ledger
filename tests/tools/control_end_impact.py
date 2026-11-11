"""Size the control-end bug on trades: re-value every traded player whose
service-time control end (data/service.json) differs from the engine's
debut-year rule, once with each end, in separate processes so no cache
carries over.

  python3 tests/tools/control_end_impact.py old > /tmp/ce_old.json
  python3 tests/tools/control_end_impact.py new > /tmp/ce_new.json
Needs the engine dir (/work) with asset_rules.py and the data files."""
import json, math, sys
sys.path.insert(0, '/work')
import asset_rules as AR
MODE = sys.argv[1]
SV = json.load(open('/work/service.json'))
cfg = json.load(open('/work/regimes.json'))
AB = {}
for r in cfg['regimes']:
    AB.setdefault(r['abbr'], set()).update(set(cfg['aliases'].get(str(r['teamId']), [])) | {r['team']})

def true_end(pid):
    s = SV.get(str(pid))
    if not s: return None
    by = {int(k): v for k, v in s['by'].items()}; tot = 0
    for y in sorted(by):
        tot += by[y]
        if tot >= 1032: return y
    left = 1032 - tot; last = max(by) if by else 2026
    return last + math.ceil(left / 172)

# ledger.sqlite is not in the repo: rebuild the engine's event list (FA filings,
# releases, free-agent signings) from the page's own moves feed (moves.js)
import re
from collections import defaultdict
_src = open('/work/moves.js').read()
_types = json.loads(re.search(r'PLAYER_MOVE_TYPES = (\[.*?\]);', _src).group(1))
_mv = json.loads(re.search(r'PLAYER_MOVES = (\{.*?\});\n', _src, re.S).group(1))
_map = {'Declared Free Agency': 'Declared Free Agency', 'Released': 'Released',
        'Signed as Free Agent': 'Signed as Free Agent', 'Minor-league deal': 'Signed as Free Agent'}
AR._EVENTS = defaultdict(list)
for _p, _rows in _mv.items():
    for _r in _rows:
        _t = _types[_r[1]]
        if _t in _map: AR._EVENTS[int(_p)].append((_r[0], _map[_t], _r[2]))
old_ce = AR.control_end
diff = {}
for p in SV:
    te, ee = true_end(p), old_ce(int(p))
    if te is not None and ee is not None and te != ee: diff[int(p)] = (ee, te)
if MODE == 'new':
    AR.control_end = lambda pid: diff[int(pid)][1] if pid and int(pid) in diff else old_ce(pid)

tb = json.load(open('/work/trade_book.json'))['trades']
out = []
for i, (d, seats) in enumerate(tb):
    for ab, net, ins, outs in seats:
        for pid, v in ins:
            if int(pid) not in diff: continue
            giver = next((s[0] for s in seats if any(q[0] == pid for q in s[3])), None)
            val = AR.trade_window(int(pid), AB.get(ab, {ab}), d, sender=AB.get(giver) if giver else None)[0]
            out.append([i, d, ab, giver, pid, v, round(val, 2)])
json.dump({'diff': {str(k): v for k, v in diff.items()}, 'rows': out}, sys.stdout)
