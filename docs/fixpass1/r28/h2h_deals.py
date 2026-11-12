"""Head-to-Head (v5.8): every pair record is built from the trade book, so
the tab, the report cards and the trade ledger show one valuation of every
deal (asset windows, salary, leverage, discounting). Before, the pair
headline (archetype.py) and the deal list used two other valuations and
could disagree in sign.

For each trade, the pieces club A received FROM club B (the piece appears in
B's outgoing list) count for A against B, and the pieces A sent to B count
against A. Only deals made while both current regimes held their seats.
Overwrites r["h2h"] in sweep_results.json and h2h_matrix.json. Run after
trade_book.py.
"""
import json
from collections import defaultdict

ROOT = "/work"
cfg = json.load(open(f"{ROOT}/regimes.json"))
REG = {r["abbr"]: r for r in cfg["regimes"]}
TB = json.load(open(f"{ROOT}/trade_book.json"))
NAMES = TB.get("names", {})

pair = defaultdict(list)     # (A, B) -> [dict(d, h, net)]
for d, seats in TB["trades"]:
    # v5.9: a club with two seats in one linked deal (SD in the 2014-12-19 Myers
    # deal) keeps both: merge them instead of letting the second overwrite the first
    S = {}
    for s in seats:
        if s[0] in S:
            a = S[s[0]]; S[s[0]] = [a[0], a[1] + s[1], a[2] + s[2], a[3] + s[3]]
        else: S[s[0]] = list(s)
    for a, sa in S.items():
        if a not in REG or d < REG[a]["start"]: continue
        for b, sb in S.items():
            if b == a or b not in REG or d < REG[b]["start"]: continue
            b_out = {p for p, _ in sb[3]}
            a_out = {p for p, _ in sa[3]}
            got = sorted([(p, v) for p, v in sa[2] if p in b_out], key=lambda t: (-t[1], -int(t[0])))   # rule 12a explicit
            gave = sorted([(p, v) for p, v in sa[3] if p in {q for q, _ in sb[2]}], key=lambda t: (-t[1], -int(t[0])))
            if not got and not gave: continue
            nm = lambda xs: ", ".join(NAMES.get(str(p), "?") for p, _ in xs) or "cash/PTBNL"
            net = sum(v for _, v in got) - sum(v for _, v in gave)
            pair[(a, b)].append(dict(d=d, h=f"Got {nm(got)} for {nm(gave)}", net=round(net, 1)))

res = json.load(open(f"{ROOT}/sweep_results.json"))
matrix = {}
for r in res:
    a = r["abbr"]; partners = []
    for (x, b), deals in pair.items():
        if x != a: continue
        net = round(sum(z["net"] for z in deals), 1)
        matrix[f"{a}|{b}"] = dict(n=len(deals), net=net)
        if len(deals) >= 2:
            partners.append(dict(opp=b, exec=REG[b]["exec"], n=len(deals), net=net,
                                 deals=sorted(deals, key=lambda z: z["d"], reverse=True)[:60]))
    partners.sort(key=lambda p: -abs(p["net"]))
    r["h2h"] = partners
json.dump(res, open(f"{ROOT}/sweep_results.json", "w"), indent=1)
json.dump(matrix, open(f"{ROOT}/h2h_matrix.json", "w"))
print("h2h pairs from the trade book:", len(matrix), "| listed partners:", sum(len(r["h2h"]) for r in res))
