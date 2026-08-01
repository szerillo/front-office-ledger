"""
METHODOLOGY v0.3: the empirical rental market.

Question: what does a deadline buyer actually pay per win of rental
production? With that ratio, the trade lens stack consolidates: a deal is
graded 'paid vs the market at the time' plus 'realized vs paid', and
'the seller lost the player' stops being a gotcha because the market price
of a rental already embeds his departure.

Classification (exact, from the feed): a RENTAL is a player acquired in a
midseason deal (Jun 1 - Aug 31) who 'Declared Free Agency' in the feed
within 5 months of the deal. No service-time guessing.

Measures per rental deal, from the buyer's seat:
  received = LVM on the buyer in the deal season (season splits are
             per-team, so this is rest-of-season production only)
  paid     = surrendered players' unweighted control-window value realized
             on the seller (what the prospects actually became there)

Market ratio = paid / received, pooled by era. Fitted on deals where the
rental delivered at least 0.3 wins (junk swaps price near zero and only
add noise); the no-delivery pool is reported separately as the bust rate.

Sample caveat (disclosed): the archive covers current regime windows, so
early-era deals only appear for long-tenured regimes; 2015+ is dense.
Output: data/rental_market.json + printed study for the methodology doc.
"""
import json, sqlite3
from collections import defaultdict

cfg = json.load(open("/home/claude/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
LVM = {int(k): v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}
con = sqlite3.connect("/home/claude/ledger.sqlite"); con.row_factory = sqlite3.Row

# FA declarations: pid -> [dates]
fa_dates = defaultdict(list)
for r in con.execute("select person_id, date from sweep_tx where type_desc='Declared Free Agency' and person_id is not null"):
    fa_dates[int(r["person_id"])].append(r["date"])

def declared_fa_within(pid, deal_date, months=5):
    y, m = int(deal_date[:4]), int(deal_date[5:7])
    lim = f"{y + (m + months - 1) // 12}-{(m + months - 1) % 12 + 1:02d}-31"
    return any(deal_date < d <= lim for d in fa_dates.get(pid, []))

def val_year(pid, teams, yr):
    rec = LVM.get(pid)
    if not rec: return 0.0
    return sum(v for (y, tm, v) in rec["rows"] if y == yr and tm in teams)

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

# walk every regime's trades from the BUYER seat
deals = []
seen_deal = set()
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    start = max(reg["start"], "2005-01-01")
    rows = [dict(r) for r in con.execute(
        "select * from sweep_tx where team_id=? and date>=? and type_desc='Trade'", (tid, start))]
    trades = defaultdict(list)
    for r in rows: trades[(r["date"], r["description"])].append(r)
    for (d, desc), rs in trades.items():
        mo = int(d[5:7])
        if not (6 <= mo <= 8): continue                    # deadline season
        key = (d, desc)
        if key in seen_deal: continue
        yr = int(d[:4])
        acquired = [x for x in rs if x["to_team"] in names and x["person_id"]]
        rentals = [x for x in acquired if declared_fa_within(int(x["person_id"]), d)]
        if not rentals: continue
        seen_deal.add(key)
        outs = {x["person_id"]: x["to_team"] for x in rs
                if x["from_team"] in names and x["person_id"] and x["to_team"]}
        received = sum(val_year(int(x["person_id"]), names, yr) for x in rentals)
        # non-rental pieces also received in the same deal dilute the price;
        # count their control value as received too (package accounting)
        others = [x for x in acquired if x not in rentals]
        received_ctrl = sum(val_control(int(x["person_id"]), names, yr) for x in others)
        paid = sum(val_control(int(p), {dest}, yr) for p, dest in outs.items())
        deals.append(dict(d=d, buyer=reg["abbr"], yr=yr,
                          rental=", ".join(x["person_name"] for x in rentals),
                          received=round(received, 2), extra=round(received_ctrl, 2),
                          paid=round(paid, 2), desc=(desc or "")[:120]))

print(f"deadline rental deals classified: {len(deals)}")

ERAS = [(2005, 2011), (2012, 2016), (2017, 2021), (2022, 2025)]
study = dict(n=len(deals), eras=[])
for a, b in ERAS:
    sub = [x for x in deals if a <= x["yr"] <= b]
    good = [x for x in sub if x["received"] >= 0.3 and x["extra"] < 1.0]
    busts = [x for x in sub if x["received"] < 0.3 and x["extra"] < 1.0]
    if not good:
        study["eras"].append(dict(era=f"{a}-{b}", n=len(sub))); continue
    tot_r = sum(x["received"] for x in good); tot_p = sum(x["paid"] for x in good)
    ratios = sorted((x["paid"] / x["received"]) for x in good)
    med = ratios[len(ratios)//2]
    era = dict(era=f"{a}-{b}", n=len(sub), n_fit=len(good),
               pooled_ratio=round(tot_p / tot_r, 3), median_ratio=round(med, 3),
               bust_rate=round(len(busts) / max(1, len(busts) + len(good)), 3),
               avg_received=round(tot_r / len(good), 2),
               avg_paid=round(tot_p / len(good), 2))
    study["eras"].append(era)
    print(era)

# the big-ticket end of the market (received >= 1.5 wins): what stars cost
stars = [x for x in deals if x["received"] >= 1.5 and x["extra"] < 1.0]
if stars:
    tr = sum(x["received"] for x in stars); tp = sum(x["paid"] for x in stars)
    study["star_market"] = dict(n=len(stars), pooled_ratio=round(tp / tr, 3),
                                avg_received=round(tr / len(stars), 2),
                                avg_paid=round(tp / len(stars), 2))
    print("star rentals (>=1.5 wins delivered):", study["star_market"])
    stars.sort(key=lambda x: -x["received"])
    print("\nbiggest rentals in the archive:")
    for x in stars[:12]:
        print(f"  {x['yr']} {x['buyer']:<4} {x['rental'][:32]:<34} recv {x['received']:>4.1f}  paid {x['paid']:>5.1f}")

study["deals"] = deals
json.dump(study, open("/home/claude/rental_market.json", "w"), indent=1)
print("\nwrote rental_market.json")
