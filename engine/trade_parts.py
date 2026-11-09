"""The deal ledger behind every graded trade (Nov 2026): for each player in
each trade, what he produced over the window the trade bought (Ledger WAR,
discounted like the grade) and what his salary cost in wins, so a card can
say "Santana: +13.3 WAR, -13.3 wins of salary" instead of a bare 0.0.
Same window rules as asset_rules.trade_window (it is copied, not changed).
Reads trade_book.json; writes trade_parts.json:
  {"d|pid|receiverAb": [war, salaryWins, firstSeason, lastSeason, openExpectation, newContractOwnsIt]}"""
import json
from collections import defaultdict as _dd
import asset_rules as A
ROOT = "/work"
cfg = json.load(open(f"{ROOT}/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
AB2NAMES = {}
for r in cfg["regimes"]:
    AB2NAMES.setdefault(r["abbr"], set()).update(ALIAS.get(r["teamId"], set()) | {r["team"]})
def parts(pid, teams, date, sender, cap=6):
    rec = A._lvm().get(int(pid)) if pid else None
    opn = A.open_expectation(pid, date) if pid else 0.0
    if not rec: return [0.0, 0.0, None, None, round(opn, 1)]
    yd, md = int(str(date)[:4]), int(str(date)[5:7] or 7)
    off = md >= 10; y0 = yd + 1 if off else yd; end = y0 + cap - 1
    ce = A.control_end(pid)
    if ce is not None and ce >= y0: end = max(end, ce)
    nc = A.new_contract_season(pid, date, acq=teams)
    if nc is not None: end = min(end, nc - 1)
    newc = nc is not None and nc <= y0
    end = min(end, A.asset_end(pid, date), 2026)
    byyear = _dd(list)
    for yr, tm, v in rec["rows"]: byyear[yr].append((tm, v))
    war = cost = 0.0; seasons = []
    for yr in range(y0, end + 1):
        rows = byyear.get(yr, [])
        if yr == yd and not off:
            if not rows: continue
            if sender:
                last = max([i for i, (tm, v) in enumerate(rows) if tm in sender], default=None)
                use = [v for tm, v in rows[last + 1:]] if last is not None else [v for tm, v in rows if tm in teams]
            else: use = [v for tm, v in rows if tm in teams]
            share = len([1 for tm, v in rows if tm in teams]) / len(rows)
        else:
            use = [v for tm, v in rows]; share = 1.0
        disc = 0.9 ** (yr - y0)
        c = A.contract_cost(pid, yr, after=date, acq=teams, played=bool(rows)) * share
        if not use and c == 0: continue
        war += sum(use) * disc; cost += c * disc; seasons.append(yr)
    return [round(war, 1), round(cost, 1), seasons[0] if seasons else None, seasons[-1] if seasons else None, round(opn, 1), 1 if newc else 0]
tb = json.load(open(f"{ROOT}/trade_book.json"))
out = {}
for d, sides in tb["trades"]:
    recv = {}
    for ab, net, got, gave in sides:
        for pid, v in got: recv[pid] = ab
    for ab, net, got, gave in sides:
        for pid, v in gave:
            r = recv.get(pid)
            if not r: continue
            key = f"{d}|{pid}|{r}"
            if key in out: continue
            out[key] = parts(pid, AB2NAMES.get(r, {r}), d, AB2NAMES.get(ab, {ab}))
json.dump(out, open(f"{ROOT}/trade_parts.json", "w"), separators=(",", ":"))
import os; print(len(out), round(os.path.getsize(f"{ROOT}/trade_parts.json") / 1e6, 2), "MB")
