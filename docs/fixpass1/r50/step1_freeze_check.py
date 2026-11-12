import sys, json; sys.path.insert(0, '/tmp/r49/eval'); from common import *
a, b = snapshot(Z), snapshot('/tmp/sbx/runs/FZ0/work/')
d = diff(a, b); cnt = {k: len(v) for k, v in d.items()}
ok = all(v == 0 for v in cnt.values())
print(json.dumps({'step': 'FZ0 freeze check', 'differences': cnt, 'bar': '0 differences', 'PASS': ok, 'examples': {k: [str(x) for x in v[:5]] for k, v in d.items() if v}}))
