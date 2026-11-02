"""Test-like check (v5.9): same-name contract merges.

Lists every contract row, in the engine book (contract_book.json) and the
page's book (desk_data.json -> DESK.book), whose player id never played for
the contract's club in or around its seasons WHILE another player with the
same name exists. Those are the Will Smith (C) carrying Will Smith (LHP)'s
Rangers deal cases. Exit status 1 when any remain.

Rows where neither namesake played for the club (a pre-debut extension, a
contract voided before he played) are listed separately as "unverifiable"
and do not fail the check."""
import json, sys, unicodedata
from collections import defaultdict
ROOT = "/work"
LVM = {int(k): v for k, v in json.load(open(f"{ROOT}/lvm_cache.json")).items() if not k.startswith("__")}
cfg = json.load(open(f"{ROOT}/regimes.json"))
NAMES = {r["abbr"]: set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in cfg["regimes"]}
def norm(nm):
    x = unicodedata.normalize("NFKD", nm or "").encode("ascii", "ignore").decode()
    return x.lower().replace(".", "").replace(" jr", "").replace(" sr", "").replace(" ii", "").replace(" iii", "").strip()
N2P = defaultdict(set)
for pid, rec in LVM.items(): N2P[norm(rec.get("name", ""))].add(pid)
desk = json.load(open(f"{ROOT}/desk_data.json"))
for p in desk["players"]: N2P[norm(p[0])].add(p[1])
def played(pid, ab, y0, y1):
    rows = (LVM.get(pid) or {}).get("rows", [])
    return any(y0 <= r[0] <= y1 and r[1] in NAMES.get(ab, ()) for r in rows)
def prior(pid, start):
    return len({r[0] for r in (LVM.get(pid) or {}).get("rows", []) if r[0] < start})
def check(rows, label):
    bad, unk = [], []
    for row in rows:
        name, pid, ab, start, yrs = row[:5]; kind = row[5] if len(row) > 5 else "fa"
        if not pid or ab not in NAMES: continue
        others = N2P.get(norm(name), set()) - {pid}
        if not others: continue
        y0, y1 = start - 1, start + max(yrs, 1)
        if played(pid, ab, y0, y1):
            # career stage: a free-agent deal on a namesake with no MLB career
            # before it, while a veteran namesake played for the club then
            # (Roberto Hernandez's 2007 Cleveland deal on Fausto Carmona)
            if kind == "fa" and prior(pid, start) <= 1:
                vet = [o for o in others if played(o, ab, y0, y1) and prior(o, start) >= 3]
                if vet: bad.append((label, name, ab, start, yrs, pid, sorted(vet)))
            continue
        alt = [o for o in others if played(o, ab, y0, y1)]
        (bad if alt else unk).append((label, name, ab, start, yrs, pid, sorted(alt)))
    return bad, unk
eng = json.load(open(f"{ROOT}/contract_book.json"))["book"]
b1, u1 = check([(c["name"], c["pid"], c["club"], c["start"], c["yrs"], c["kind"]) for c in eng], "engine")
drows = []
for r in desk["book"]:
    start = r[1] + 1
    drows.append((r[0], r[11], r[2], start, r[3], "fa" if r[12] == 0 else "ext"))
b2, u2 = check(drows, "page")
for x in b1 + b2: print("COLLISION", *x)
print(f"\n{len(b1)} engine + {len(b2)} page rows sit on the wrong namesake")
if "-v" in sys.argv:
    for x in u1 + u2: print("unverifiable", *x)
print(f"{len(u1) + len(u2)} rows unverifiable (no namesake played for the club then)")
sys.exit(1 if (b1 or b2) else 0)
