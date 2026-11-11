"""Found in round 13: the engine charges 2020 salaries at the full-season rate (dpw 2020 = 2019) while 2020
value is a 60-game season, and 2020 pay was prorated to 60/162. Size it on trades: every acquired piece's
2020 charge in its trade window scaled by 60/162. Report only."""
import sys, io, contextlib, runpy
from collections import defaultdict
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ['x']; A = runpy.run_path('tests/tools/arb_shadow.py')
AR, tb, AB = A['AR'], A['tb'], A['AB']
delta = defaultdict(float); n = 0; tot = 0.0
for i, (d, seats) in enumerate(tb['trades']):
    if d > '2020-12-31' or d < '2014-10-01': continue
    for ab, net, ins, outs in seats:
        acq = AB.get(ab, {ab})
        for pid, v in ins:
            pid = int(pid); t, ser = AR.trade_window(pid, acq, d)
            if 2020 not in ser: continue
            c = AR.contract_cost(pid, 2020, after=d, acq=acq, played=True)
            if not c: continue
            y0 = int(d[:4]) + (1 if int(d[5:7]) >= 10 else 0)
            fix = c * (1 - 60 / 162) * 0.9 ** (2020 - y0) * A['share'](pid, 2020, d, acq)
            giver = next((s[0] for s in seats if any(int(q[0]) == pid for q in s[3])), None)
            delta[(i, ab)] += fix; n += 1; tot += fix
            if giver: delta[(i, giver)] -= fix
print('acquired 2020 seasons with a charge:', n, '| charge removed: %.1f wins' % tot)
print('sides 1+ win, flips, top/bottom-25, clubs 2+ ranks, largest:', A['counts'](delta))
for (i, ab), v in sorted(delta.items(), key=lambda kv: -abs(kv[1]))[:6]: print(' ', tb['trades'][i][0], ab, '%+.2f' % v)
