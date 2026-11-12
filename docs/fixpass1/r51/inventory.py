# Round 51: fit inventory from evidence. A fitted quantity = a global that is a number or a small container of numbers
# (or an estimator call) whose value differs between the frozen baseline (FZ0i) and the frozen rule run (F1i).
import json, os, sys
A, B = sys.argv[1], sys.argv[2]
out = {'globals_changed_numeric': [], 'globals_changed_other': [], 'estimator_calls_changed': [], 'reads_changed': {}}
for f in sorted(os.listdir(A)):
    a = json.load(open(os.path.join(A, f))); bp = os.path.join(B, f)
    if not os.path.exists(bp): continue
    b = json.load(open(bp)); step = a['step']
    rc = sorted(p.replace('/work/', '') for p in set(a['reads']) & set(b['reads']) if a['reads'][p] != b['reads'][p])
    out['reads_changed'][step] = rc
    for g, va in a['globals'].items():
        vb = b['globals'].get(g)
        if vb and va[2] != vb[2]:
            (out['globals_changed_numeric'] if (va[3] and vb[3]) else out['globals_changed_other']).append([step, g, va[0], va[1]])
    ca = {}; [ca.setdefault((c[0], c[1]), []).append(c[3]) for c in a['calls']]
    cb = {}; [cb.setdefault((c[0], c[1]), []).append(c[3]) for c in b['calls']]
    for k in ca:
        if k in cb and ca[k] != cb[k]: out['estimator_calls_changed'].append([step, k[0], k[1], len(ca[k])])
json.dump(out, open(sys.argv[3], 'w'), indent=1)
print('numeric globals changed:', len(out['globals_changed_numeric']))
for x in out['globals_changed_numeric']: print('  ', x)
print('estimator call sites changed:', len(out['estimator_calls_changed']))
for x in out['estimator_calls_changed']: print('  ', x)
print('other globals changed:', len(out['globals_changed_other']))
