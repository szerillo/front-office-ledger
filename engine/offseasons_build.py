"""Best and worst offseasons (Nov 10 2026): every club-winter since 1998-99, added up.
A winter runs Nov 1 through Mar 31. For each club: the net of every trade it made (trade book, its
own seat) plus the surplus of every priced free-agent signing (fa_grade rows), in wins. Winters from
2022-23 on are flagged open: contracts and control years are still running.
Writes offseasons.json: {rows: [[ab, winter, exec, regimeId, tradeNet, nTrades, faNet, nFA, faM, total,
prevW, nextW, [[kind, date, label, value, pid], ...]]]}"""
import json
from collections import defaultdict
R = "/work/"
tb = json.load(open(R + "trade_book.json")); NM = tb["names"]
sweep = json.load(open(R + "sweep_results.json")); hist = json.load(open(R + "hist_results.json"))
gmo = json.load(open(R + "gm_offseasons.json"))
WINS = {(r["ab"], r["w"]): (r["prevW"], r["nextW"]) for r in gmo["winters"]}
def winter_of(d):
    y, m = int(d[:4]), int(d[5:7])
    if m >= 11: return y
    if m <= 3: return y - 1
    return None
# who ran the club on a given date
REG = defaultdict(list)
for r in sweep: REG[r["abbr"]].append((r.get("startDate") or f'{r["start"]}-10-01', "9999-12-31", r["exec"], r["id"]))
for r in hist: REG[r["abbr"]].append((r.get("startDate") or f'{r["start"]}-10-01', r.get("endDate") or f'{r["end"]}-10-01', r["exec"], r["id"]))
def exec_on(ab, d):
    for a, b, ex, rid in sorted(REG.get(ab, [])):
        if a <= d < b: return ex, rid
    return "", ""
W = defaultdict(lambda: dict(tr=0.0, trN=0, fa=0.0, faN=0, faM=0.0, moves=[]))
nm = lambda pid: NM.get(str(pid), "")
for d, seats in tb["trades"]:
    w = winter_of(d)
    if w is None or w < 1998 or w > 2025: continue
    for ab, net, got, gave in seats:
        k = W[(ab, w)]; k["tr"] += net; k["trN"] += 1
        g = sorted(got, key=lambda x: -x[1]); o = sorted(gave, key=lambda x: -x[1])
        gn = [nm(p) for p, _ in g[:2] if nm(p)]; on = [nm(p) for p, _ in o[:2] if nm(p)]
        if not gn and not on: continue
        label = (f'Got {" and ".join(gn)}' if gn else "Cash or a player to be named") + (f' for {" and ".join(on)}' if on else "")
        k["moves"].append(["t", d, label, round(net, 1), (g[0][0] if g else (o[0][0] if o else ""))])
seen = set()
for r in sweep + hist:
    for row in r.get("allx_fa") or []:
        d, name, yrs, tot, _real, _cost, net, pid = row[:8]
        if net is None or tot is None: continue
        w = winter_of(d)
        if w is None or w < 1998 or w > 2025 or (r["abbr"], pid, d) in seen: continue
        seen.add((r["abbr"], pid, d))
        k = W[(r["abbr"], w)]; k["fa"] += net; k["faN"] += 1; k["faM"] += tot
        k["moves"].append(["f", d, f'Signed {name}, {yrs} yr / ${tot:g}M', round(net, 1), pid])
rows = []
for (ab, w), k in sorted(W.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    if k["trN"] + k["faN"] < 2: continue
    ex, rid = exec_on(ab, f"{w}-12-15")
    pw, nw = WINS.get((ab, w), (None, None))
    mv = sorted(k["moves"], key=lambda m: -abs(m[3]))[:5]
    rows.append([ab, w, ex, rid, round(k["tr"], 1), k["trN"], round(k["fa"], 1), k["faN"], round(k["faM"]), round(k["tr"] + k["fa"], 1), pw, nw, mv])
json.dump({"v": 1, "open_from": 2022, "rows": rows}, open(R + "offseasons.json", "w"), separators=(",", ":"), ensure_ascii=False)
rs = sorted(rows, key=lambda r: -r[9])
print(len(rows), "club-winters;", sum(1 for r in rows if not r[2]), "without an exec on file")
for r in rs[:8] + rs[-8:]: print(r[1], r[0], r[2], "total", r[9], "trades", r[4], "FA", r[6], "|", r[12][0][2][:60], r[12][0][3])
