import hashlib, os, sys, json
PUB = ["cards.js", "moves.js", "front-office-ledger-prototype.html", "offseasons.json", "trade_parts.json"]
MID = ["trade_book.json", "sweep_results.json", "hist_results.json", "desk_data.json", "lvm_cache.json", "contract_book.json"]
runs = [r for r in sys.argv[1:] if os.path.exists(f"/tmp/sbx/runs/{r}/steps.txt") and open(f"/tmp/sbx/runs/{r}/steps.txt").read().strip().endswith("DONE")]
md = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()[:8] if os.path.exists(p) else "missing"
out = {}
for f in PUB + MID:
    out[f] = {r: md(f"/tmp/sbx/runs/{r}/work/{f}") for r in runs}
    vals = set(out[f].values())
    print(f"{'PUB' if f in PUB else 'mid'} {f:38s} {'SAME' if len(vals)==1 else 'DIFFERS'}  " + " ".join(f"{r}:{v}" for r, v in out[f].items()))
json.dump(out, open("/tmp/sbx/cmp.json", "w"), indent=1)
