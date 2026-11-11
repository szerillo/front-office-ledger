# For each output, is the R0-vs-Rk difference order-only (same content once every list is sorted) or a value change?
import json, sys, re, os
def canon(x):
    if isinstance(x, dict): return {k: canon(v) for k, v in sorted(x.items())}
    if isinstance(x, list): return sorted((canon(v) for v in x), key=lambda v: json.dumps(v, sort_keys=True))
    return x
def load(p):
    s = open(p, encoding="utf-8").read()
    if p.endswith(".json"): return json.loads(s)
    # JS files: pull every JSON payload after "= " up to the matching ";\n"
    out = []
    for m in re.finditer(r"=\s*(JSON\.parse\()?([\[{].*?)\)?;\s*\n", s, re.S):
        try: out.append(json.loads(m.group(2)))
        except Exception:
            try: out.append(json.loads(json.loads('"' + m.group(2).strip("'\"") + '"')))
            except Exception: pass
    return out
if __name__ == "__main__":
    base, others = sys.argv[1], sys.argv[2:]
    for f in ["cards.js", "moves.js", "offseasons.json", "trade_parts.json", "trade_book.json", "sweep_results.json", "hist_results.json", "desk_data.json"]:
        A = load(f"/tmp/sbx/runs/{base}/work/{f}"); ca = json.dumps(canon(A), sort_keys=True); ra = json.dumps(A, sort_keys=True)
        res = []
        for r in others:
            p = f"/tmp/sbx/runs/{r}/work/{f}"
            if not os.path.exists(p): res.append(f"{r}:-"); continue
            B = load(p); rb = json.dumps(B, sort_keys=True)
            res.append(f"{r}:" + ("same" if ra == rb else "order-only" if json.dumps(canon(B), sort_keys=True) == ca else "VALUES"))
        print(f"{f:20s} parsed={'yes' if A else 'NO'}  " + "  ".join(res))
