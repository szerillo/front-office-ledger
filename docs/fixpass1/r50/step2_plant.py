import sys, json; sys.path.insert(0, '/tmp/r49/eval'); from common import *
T = 'stl-walt-jocketty'
a, b = snapshot('/tmp/sbx/runs/FZ0/work/'), snapshot('/tmp/sbx/runs/FP/work/')
d = diff(a, b)
mv = round(b['nets'][(T, 'ext')] - a['nets'][(T, 'ext')], 6)
other = {k: [str(x) for x in v if (x[0] if isinstance(x, tuple) else x) != T] for k, v in d.items() if k in ('nets', 'letters', 'overall', 'totals', 'rank_overall', 'rank_ext')}
other_n = {k: len(v) for k, v in other.items()}
ok = abs(mv - 5.0) < 1e-9 and all(v == 0 for v in other_n.values())
print(json.dumps({'step': 'FP spread plant', 'target': T, 'target_ext_net': [a['nets'][(T, 'ext')], b['nets'][(T, 'ext')]], 'moved_by': mv,
  'target_letter': [a['letters'].get((T, 'ext')), b['letters'].get((T, 'ext'))], 'target_overall': [a['overall'][T], b['overall'][T]],
  'other_front_offices_moved': other_n, 'examples': {k: v[:5] for k, v in other.items() if v},
  'seats_changed': len(d['seats']), 'winters_changed': len(d['winters']), 'bar': 'target ext net +5.0 exactly; no other front office letter, net or rank moves', 'PASS': ok}))
