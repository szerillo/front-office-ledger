import json, sys, re, collections
sys.path.insert(0, '/tmp/sbx'); from canon import load
def leaves(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items(): yield from leaves(v, f"{p}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x): yield from leaves(v, f"{p}[{i}]")
    else: yield p, x
a, b, f = sys.argv[1], sys.argv[2], sys.argv[3]
A = dict(leaves(load(f"/tmp/sbx/runs/{a}/work/{f}"))); B = dict(leaves(load(f"/tmp/sbx/runs/{b}/work/{f}")))
d = [(k, A.get(k), B.get(k)) for k in set(A) | set(B) if A.get(k) != B.get(k)]
num = [t for t in d if isinstance(t[1], (int, float)) and isinstance(t[2], (int, float)) and not isinstance(t[1], bool)]
print(f, "leaves", len(A), "differ", len(d), "numeric", len(num), "max numeric gap", round(max((abs(x - y) for _, x, y in num), default=0), 3))
for t in sorted(d, key=lambda t: t[0])[:int(sys.argv[4]) if len(sys.argv) > 4 else 5]: print("   ", str(t)[:200])
