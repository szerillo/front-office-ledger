# Round 48 dry run: service counts on the 184-player frame with the old and new counter. No regrade.
import json, sys, importlib.util
def load(p):
    spec = importlib.util.spec_from_file_location(p.split('/')[-1][:-3], p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
O, N = load('/tmp/r48/eng/svc_fetch_old.py'), load('/tmp/r48/eng/svc_fetch.py')
C = json.load(open('/tmp/r45/svc/frame_tx.json'))
ch = []
for pid, txs in C.items():
    a, b = O.service(pid, txs), N.service(pid, txs)
    if a != b:
        ta, tb = sum(a.values()), sum(b.values())
        ch.append({'pid': pid, 'old_total': O.to_years(ta), 'new_total': N.to_years(tb), 'years_changed': {y: [a.get(y, 0), b.get(y, 0)] for y in sorted(set(a) | set(b)) if a.get(y, 0) != b.get(y, 0)}})
print('frame', len(C), 'players whose count changes', len(ch))
for c in ch: print(c)
json.dump(ch, open('/tmp/r48/eng/dry_efa.json', 'w'), indent=1)
