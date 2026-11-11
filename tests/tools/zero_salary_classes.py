"""Classify all 802 $0 post-control trade seasons (population of
zero_salary_sample.py) without sampling:
  arb      season is at or before the service-time control end (control-end bug)
  missing  past the service-time end, and no free-agent filing, release or
           free-agent signing between the end of control and that season:
           the player must have been under some contract the book lacks
           (an option, or an extension signed earlier)
  fa       a filing or signing came first: a later free-agent or minor-league
           deal, which the book should hold if it was a major-league deal
  nosvc    no usable service record (debut rule only)
Prints counts and writes /tmp/zero_classes.json."""
import json, re, sys, runpy, io, contextlib
sys.path.insert(0, '/work'); sys.path.insert(0, 'tests/tools')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    Z = runpy.run_path('tests/tools/zero_salary_sample.py')
pop, AR = Z['pop'], Z['AR']
import math
SV = json.load(open('/work/service.json'))
def true_end(pid):  # same as control_end_impact.true_end (that module runs on import)
    s = SV.get(str(pid))
    if not s: return None
    by = {int(k): v for k, v in s['by'].items()}; tot = 0
    _rec = AR._lvm().get(int(pid)); _pl = {r[0] for r in (_rec or {}).get('rows', [])}
    if by and any(min(by) < y < max(by) and y not in by for y in _pl): return None
    for y in sorted(by):
        tot += by[y]
        if tot >= 1032: return y
    left = 1032 - tot; last = max(by) if by else 2026
    return last + math.ceil(left / 172)
EV = AR._EVENTS
book = json.load(open('/work/contract_book.json'))['book']
own = {}
for c in book:
    for y in c['own']: own.setdefault(c['pid'], {})[y] = c
out = []; cnt = {}
for d, ab, pid, nm, y, ce in pop:
    te = true_end(int(pid))
    if te is None: k = 'nosvc'
    elif y <= te: k = 'arb'
    else:
        # events from the end of control (Oct of te) to the start of season y
        evs = [e for e in EV.get(int(pid), []) if f'{te}-10-01' <= e[0] < f'{y}-03-15']
        k = 'missing' if not evs else 'fa'
    cnt[k] = cnt.get(k, 0) + 1
    out.append(dict(d=d, ab=ab, pid=pid, name=nm, y=y, ce=ce, te=te, cls=k))
print('population', len(pop)); print(cnt)
json.dump(out, open('/tmp/zero_classes.json', 'w'))
