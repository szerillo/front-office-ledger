"""Nov 9: context for the daily trade game. For every two-club trade the game can draw
(through 2023, a 4+ win gap), each player's position, age that season and Ledger WAR in his
last full season before the deal; and a pool of finished free-agent contracts for the
"did he earn it?" questions: platform seasons, terms, what he produced on the deal against
what a typical club gets for that money (the same yardstick as the free-agency grades).
Writes quiz_ctx.json; regen_v3 splices it into the page as QUIZ_CTX."""
import json
from collections import defaultdict
TB = json.load(open("/work/trade_book.json"))
LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
AGES = json.load(open("/work/ages.json"))
POS = json.load(open("/work/positions.json")); POS.update(json.load(open("/work/positions2.json")))
CB = json.load(open("/work/repo/data/contract_book.json"))
WAR = {}
for pid, rec in LVM.items():
    d = defaultdict(float)
    for y, t, v in rec["rows"]: d[y] += v
    WAR[pid] = d
def pos(pid):
    p = POS.get(str(pid)) or ""
    return {"RHP": "P", "LHP": "P", "TWP": "DH"}.get(p, p)
trades = {}
for d, sides in TB["trades"]:
    if len(sides) != 2 or d[:4] > "2023": continue
    win = max(s[1] for s in sides)
    if win < 4: continue
    y, m = int(d[:4]), int(d[5:7])
    last = y - 1 if m <= 9 else y
    for ab, net, got, gave in sides:
        for pid, w in got:
            pid = int(pid); by = AGES.get(str(pid))
            wr = WAR.get(pid, {}); lw = wr.get(last)
            prior = [v for k, v in wr.items() if int(k) <= last]
            trades[f"{d}|{pid}"] = [pos(pid), (y - by) if by else None, None if lw is None else round(lw, 1), last,
                                    round(sum(prior), 1) if prior else None, 1 if 6 <= m <= 8 else 0]
names = {**{int(k): v for k, v in (TB.get("names") or {}).items()}}
for pid, rec in LVM.items(): names.setdefault(pid, rec.get("name"))
dpw, typ = CB["dpw"], CB["typical_fa"]
fa = []
for b in CB["book"]:
    if b["kind"] != "fa" or b["aav"] < 8 or b["yrs"] < 2: continue
    held = b.get("held") or []
    if not held or max(h[1] for h in held) > 2025 or b["start"] + b["yrs"] - 1 > 2025 or b["start"] < 2003: continue
    prod = sum(h[2] * h[3] for h in held)
    exp = sum(b["aav"] * h[3] / dpw.get(str(h[1]), 9.7) * typ.get(str(min(h[0], 5)), 0.84) for h in held)
    if abs(prod - exp) < 2.0: continue
    pid = b["pid"]; by = AGES.get(str(pid)); s0 = b["start"] - 1
    fa.append([b["name"], pid, b["club"], b["sign"], b["yrs"], round(b["tot"], 1), (s0 - by) if by else None, pos(pid),
               [round(WAR.get(pid, {}).get(s0 - k, 0.0), 1) for k in (2, 1, 0)], round(prod, 1), round(exp, 1),
               [round(h[2] * h[3], 1) for h in held], [h[1] for h in held]])
fa.sort(key=lambda x: x[3])
json.dump({"trades": trades, "fa": fa}, open("/work/quiz_ctx.json", "w"), separators=(",", ":"))
print("trade players with context:", len(trades), "| contract questions:", len(fa), "| earned:", sum(1 for x in fa if x[9] >= x[10]))
