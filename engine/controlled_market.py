"""
METHODOLOGY v0.4: the controlled-years deadline market.

v0.3 priced rentals (acquired Jun-Aug, declared FA within 5 months of the
deal). v0.4 prices the rest of the deadline market: acquisitions that came
with CONTROL, bucketed by how many seasons of control the buyer actually
received (measured, not guessed: years from the deal to the player's first
free-agency declaration in the feed, capped at 6; players who never declared
through 2026 are right-censored and capped at observed seasons).

Per deal, buyer's seat, full 2005+ league-wide archive (not just current
regime windows, now that the full re-ingest exists):
  received = control-window value on the buyer (unweighted)
  paid     = surrendered players' control-window value realized on the seller
  control  = max over acquired pieces of measured control years

Output: appended as "controlled" to data/rental_market.json.
"""
import json, sqlite3
from collections import defaultdict

cfg = json.load(open("/home/claude/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
LVM = {int(k): v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}
con = sqlite3.connect("/home/claude/ledger.sqlite"); con.row_factory = sqlite3.Row

fa_dates = defaultdict(list)
for r in con.execute("select person_id, date from sweep_tx where type_desc='Declared Free Agency' and person_id is not null"):
    fa_dates[int(r["person_id"])].append(r["date"])
for k in fa_dates: fa_dates[k].sort()

def control_years(pid, deal_date):
    """seasons of control from the deal: deal season counts as 1."""
    y0 = int(deal_date[:4])
    for d in fa_dates.get(pid, []):
        if d > deal_date:
            return min(6, max(1, int(d[:4]) - y0 + 1))
    return None  # never declared: censored

def declared_fa_within(pid, deal_date, months=5):
    y, m = int(deal_date[:4]), int(deal_date[5:7])
    lim = f"{y + (m + months - 1) // 12}-{(m + months - 1) % 12 + 1:02d}-31"
    return any(deal_date < d <= lim for d in fa_dates.get(pid, []))

def val_control(pid, teams, y0, cap=6):
    rec = LVM.get(pid)
    if not rec: return 0.0
    byyear = defaultdict(list)
    for y, tm, v in rec["rows"]: byyear[y].append((tm, v))
    tot = 0.0
    for y in range(y0, y0 + cap):
        rows = byyear.get(y, [])
        here = [v for (tm, v) in rows if tm in teams]
        if rows and not here and y > y0: break
        tot += sum(here)
    return tot

deals = []
seen = set()
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    rows = [dict(r) for r in con.execute(
        "select * from sweep_tx where team_id=? and date>='2005-01-01' and type_desc='Trade'", (tid,))]
    trades = defaultdict(list)
    for r in rows: trades[(r["date"], r["description"])].append(r)
    for (d, desc), rs in trades.items():
        mo = int(d[5:7])
        if not (6 <= mo <= 8): continue
        yr = int(d[:4])
        if yr > 2023: continue                       # need windows to mature
        acquired = [x for x in rs if x["to_team"] in names and x["person_id"]]
        if not acquired: continue
        # exclude pure rental deals (v0.3's universe)
        if all(declared_fa_within(int(x["person_id"]), d) for x in acquired): continue
        key = (d, desc, tid)
        if key in seen: continue
        seen.add(key)
        ctrl = 0; censored = False
        for x in acquired:
            c = control_years(int(x["person_id"]), d)
            if c is None: censored = True; c = 6
            ctrl = max(ctrl, c)
        outs = {x["person_id"]: x["to_team"] for x in rs
                if x["from_team"] in names and x["person_id"] and x["to_team"]}
        received = sum(val_control(int(x["person_id"]), names, yr) for x in acquired)
        paid = sum(val_control(int(p), {dest}, yr) for p, dest in outs.items())
        deals.append(dict(d=d, buyer=reg["abbr"], yr=yr, ctrl=ctrl, cens=censored,
                          received=round(received, 2), paid=round(paid, 2),
                          who=", ".join(x["person_name"] or "?" for x in acquired)[:60]))

print(f"controlled deadline deals: {len(deals)}")
BUCKETS = [(2, 2, "deal yr + 1"), (3, 3, "deal yr + 2"), (4, 6, "deal yr + 3 or more")]
out = dict(n=len(deals), buckets=[])
for lo, hi, label in BUCKETS:
    sub = [x for x in deals if lo <= x["ctrl"] <= hi]
    good = [x for x in sub if x["received"] >= 0.3]
    busts = [x for x in sub if x["received"] < 0.3]
    if not good: continue
    tr = sum(x["received"] for x in good); tp = sum(x["paid"] for x in good)
    ratios = sorted(x["paid"] / x["received"] for x in good)
    b = dict(ctrl=label, n=len(sub), n_fit=len(good),
             pooled_ratio=round(tp / tr, 3), median_ratio=round(ratios[len(ratios)//2], 3),
             bust_rate=round(len(busts) / max(1, len(sub)), 3),
             avg_received=round(tr / len(good), 2), avg_paid=round(tp / len(good), 2))
    out["buckets"].append(b)
    print(b)

stars = [x for x in deals if x["received"] >= 3.0]
if stars:
    tr = sum(x["received"] for x in stars); tp = sum(x["paid"] for x in stars)
    out["star_controlled"] = dict(n=len(stars), pooled_ratio=round(tp / tr, 3),
                                  avg_received=round(tr / len(stars), 2),
                                  avg_paid=round(tp / len(stars), 2))
    print("star controlled buys (>=3 wins delivered):", out["star_controlled"])
    stars.sort(key=lambda x: -x["received"])
    for x in stars[:10]:
        print(f"  {x['yr']} {x['buyer']:<4} ctrl{x['ctrl']} {x['who'][:40]:<42} recv {x['received']:>5.1f}  paid {x['paid']:>5.1f}")

mkt = json.load(open("/home/claude/rental_market.json"))
mkt["controlled"] = out
json.dump(mkt, open("/home/claude/rental_market.json", "w"), indent=1)
print("appended controlled market to rental_market.json")
