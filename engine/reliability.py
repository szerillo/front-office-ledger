"""v5.9 (Nov 2): split-half reliability by channel, reproducible.
For every regime (active and archive) with at least MIN graded decisions in a
channel, its decisions are sorted by date and split into alternating halves;
the mean net per decision of the two halves is correlated across regimes.
A channel whose grades reflect a repeatable skill shows a positive r."""
import json, math
MIN = 6
R = json.load(open("/work/sweep_results.json")); H = json.load(open("/work/hist_results.json"))
H = H if isinstance(H, list) else H.get("regimes", [])
REGS = R + H
TB = json.load(open("/work/trade_book.json"))["trades"]
def corr(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    c = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a); vb = sum((y - mb) ** 2 for y in b)
    return c / math.sqrt(va * vb) if va > 0 and vb > 0 else 0.0
def trades(r):
    ab = r.get("abbr"); fr = r.get("startDate") or f"{r['start']}-01-01"
    to = r.get("endDate") or (f"{r['end']}-12-31" if r.get("end") else "9999-12-31")
    out = []
    for d, seats in TB:
        if not (fr <= d <= to): continue
        for st in seats:
            if st[0] == ab: out.append((d, st[1]))
    return out
def ax(r, k): return (r.get("allx") or {}).get(k, []) or []
GET = {
    "Free agency": lambda r: [(x[0], x[6]) for x in (r.get("allx_fa") or ax(r, "fa")) if x[6] is not None],
    "Extensions": lambda r: [(x[0], x[2]) for x in (r.get("allx_ext") or ax(r, "ext")) if "OPEN" not in str(x[1])],
    "Trades": trades,
    "Draft": lambda r: [(x[0], x[6]) for x in ax(r, "draft") if x[6] is not None],
    "Waivers": lambda r: [(x[0], x[3]) for x in ax(r, "waiver") if x[3] is not None],
}
out = []
for nm, g in GET.items():
    A, B = [], []
    for r in REGS:
        xs = sorted(g(r))
        if len(xs) < MIN: continue
        a = [v for i, (_, v) in enumerate(xs) if i % 2 == 0]; b = [v for i, (_, v) in enumerate(xs) if i % 2 == 1]
        A.append(sum(a) / len(a)); B.append(sum(b) / len(b))
    out.append([nm, round(corr(A, B), 2), len(A)])
out.sort(key=lambda x: -x[1])
print("split-half reliability:", out)
json.dump(out, open("/work/reliability.json", "w"))
