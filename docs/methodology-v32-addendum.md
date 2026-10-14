# Methodology addendum v3.2: the Retrosheet backfill, championship provenance, and trade market comps

October 14, 2026.

## 1. The feed gap, found and fixed (Retrosheet backfill 1998-2008)

While tracing the 2009 Yankees' championship roster, CC Sabathia's signing
could not be found. The reason turned out to be structural: **the MLB Stats
API transaction feed is effectively empty before 2009** (zero trade rows
2005-2008; ~170 rows in all of 2008 against ~1,000/year once coverage
starts). Every number built on "transactions from 2005" was actually built
on transactions from 2009, with 2005-2008 windows scored on drafts and
standings alone. The Beckett-for-Hanley trade was not in the book.

The fix was already sitting in the repo: the Retrosheet transaction archive
(1873-2022), ingested months ago for exactly this backfill.
`ingest/retro_backfill.py` maps Retrosheet rows 1998-2008 into the
transaction table: T/Tp to trades, F/Fo to FA signings, Fg to FA
declarations, W to waiver claims, D to Rule 5, R to releases. Players map
retro id to MLBAM via the full Chadwick Bureau register
(`data/retro2mlbam.json`, 24,622 mappings, built from
github.com/chadwickbureau/register; 94% of backfilled rows carry an MLBAM
id). Team codes map to era-correct API names (Devil Rays, Florida Marlins,
Anaheim Angels) so control-window value lookups match the value cache's
season strings. Each trade emits rows under both clubs with one shared
description, the scorer's deal-grouping key. 22,697 rows inserted; ~600
trades/year 1998-2008, consistent with the feed's own 2009+ volumes. The
feed remains the sole source from 2009.

The information used here was obtained free of charge from and is
copyrighted by Retrosheet. Interested parties may contact Retrosheet at
www.retrosheet.org.

Effects of the rescore (all disclosed on the site):

- Epstein's Boston trades fall from +23.1 to -26.5 (the Beckett deal's
  windows now count Hanley Ramirez's Florida prime; the 2007 ring is why
  the leverage lens and the Success column exist).
- Dombrowski's Detroit trades rise from +61.8 to +94.9 (the Cabrera heist
  enters the book).
- Late-era Beane's trades fall to -77.7; Sabean reaches +203.5 total.
- Cashman's active-window trades rise to +78.8 (2005-2008 now counted).
- Validation is stable (accounting r = 0.861 unchanged; predictive partial
  r 0.338 to 0.342): the backfill adds decisions, not value rows.

Windows and claims are unchanged: regime grading still floors at
2005-01-01. What changed is that 2005-2008 inside those windows is now
actually populated, and 1998-2004 rows exist for provenance tracing.

## 2. Championship provenance, computed (all 21 titles, 2005-2025)

`engine/champions_build.py`: for every World Series winner, the core
(players with >= 1.0 Ledger WAR in the title season) is traced to the
club's last acquisition event (feed + backfill) or draft pick. Channels:
FA, trade, draft, int'l/minor-league find; inherited means acquired before
the sitting regime's TRUE seat date (Cashman 1998, not his 2005 scoring
floor). The Champions tab renders every title's roster ledger plus a
21-title through-lines panel.

The through lines the data actually supports:

- The median champion was **88% built by its sitting regime** and won in
  **year 7** of the tenure. Nine of 21 titles came in year 10 or later;
  only three in the first three years. The quick-flip title is rare.
- **Free agency has been a majority channel exactly once** (2009 Yankees,
  56%), averaging 27% of core WAR across all titles.
- Only the three San Francisco titles were majority homegrown.
- Most trade-built: 2016 Cubs (44%). Most inherited: 2023 Rangers (85%,
  Chris Young winning with Jon Daniels' core two seasons after the
  handoff, the sharpest attribution case in the book).

## 3. Trade market comps

Every graded trade on an active or archive card now carries up to three
market comps (`engine/trade_comps.py`): the nearest deals by eventual value
received, same season phase (deadline / offseason / in-season), drawn from
the league-wide archive of **5,764 buyer-seat deals 1998-2023**
(`data/deal_archive.json`), with a 0.15 wins/year era-distance penalty and
one comp per counterparty-date. Each comp shows what the buyer eventually
received against what the surrendered players became for the seller, so a
verdict reads against the market for deals of that shape instead of in a
vacuum. Control buckets (rental / +1 / +2 / 3+ years) are measured from the
feed as seasons to the player's next free-agency declaration.

# v3.3 addendum: the 1998 floor, 28 championships, validation v2

October 14, 2026, same build day as v3.2. Four extensions.

## 1. The archive floor moves to 1998

Retrosheet backfill extended to 1985-2008 (provenance) with scoring windows
floored at 1998-01-01; drafts 1998-2004 backfilled from the Stats API draft
endpoint (verified: Pat Burrell #1 in 1998, Bullington #1 in 2002); park
factors extended to 1996 (pre-humidor Coors reads 1.26-1.31); the full value
cache rebuilt over 28,149 players; Montreal Expos alias joined so Expos-era
value rows land. The regime table (`data/regimes_hist.json`) now holds 110
archive regimes, including ~40 new or unclamped 1998-2004 windows (dates are
month-precise from documented GM history; 'approx' flags uncertainty, and
regimes seated before 1998 stay truncated with true start shown). Cashman's
ACTIVE window now runs from his real 1998-02-03 seat. Headline corrections
the fuller windows produce: the complete Billy Beane record is -28 net over
17.8 seasons (trades -54, waivers +14, drafts +12), Sabean's full window
reaches +226, and Cashman's draft channel drops to +17 once his barren
1999-2004 classes enter the book.

## 2. 28 championship ledgers, and the era through-line

All World Series winners 1998-2025. The strongest finding in the project:
the median title core was 48% self-built in 1998-2009 and 90% self-built in
2010-2025. The handed-down championship (1998 NYY 93% inherited, year one of
Cashman's seat; 2023 TEX 85%) is going extinct.

## 3. Validation v2: pooled design, honest intervals

The predictive study now pools 574 regime-years from 112 active and archive
regimes (futures bounded inside each regime's own window). Partial r of
decision value on future W%, controlling for record to date: 0.276, with a
cluster-bootstrap 95% interval of [0.164, 0.371] (B = 2000, resampling whole
regimes, the honest interval given overlapping regime-years). Grouped 5-fold
cross-validation (folds by regime) lifts out-of-sample R2 from 0.184 to
0.245. The effect survives on held-out regimes. Accounting check on the
full-coverage era (2015-2025): r = 0.853, MAE 5.3 wins.

## 4. Comps v2 and shareability

Trade comps now match on control bucket AND buyer posture (contender >= 85
wins pace / mid / rebuilder < 75) in addition to size, phase, and era.
The page itself gained Open Graph and Twitter cards with a generated
preview image, a favicon, a first-visit intro, and a mobile pass.

# v3.4 addendum: Ledger Projection v1 (the forward view)

October 14, 2026. Open deals now carry a projected rest-of-window and a
projected final verdict beside the realized grade. The projection is
self-built end to end; no licensed projection system is consulted.

Components (`engine/proj_v1.py`, curves in `data/proj_curves.json`):

- AGING CURVES by the delta method over the 28,149-player cache, hitters
  and pitchers separately, 3-age smoothing, n >= 30 per point. The textbook
  curve falls out: hitters peak at 27-28 and decline ~0.3 wins/yr through
  the 30s; pitchers decline flatter. Survivorship bias is the delta
  method's known weakness; the backtest is the arbiter.
- BASE SKILL: Marcel-style 5/4/3 weighting of the last three seasons,
  regressed 20% toward the population mean.
- FORECAST: base walked forward on the aging curve, zero floor, 10%/yr
  roster-uncertainty haircut beyond the first projected season. Control
  windows from the feed (free-agency declarations) bound every projection.
- PROSPECTS with no MLB track record: Pipeline-rank expectation (the same
  rank-to-surplus curve the deal marks use). Unranked traded prospects:
  the empirical mean outcome of 1,327 unranked traded pieces, 0.41 wins.
- BACKTEST: projecting each season from only prior data gives r = 0.619
  (2023, n = 1,093) and r = 0.667 (2025, n = 1,067) against actual
  next-season WAR, MAE ~0.8 wins: competitive with public systems.

Quarantine rule: the overlay is disclosed and the grades never move on a
forecast. Realized value is the ledger; the projection is the heading.
Worked example (the deal that prompted this): Cubs-Mets, Aug 3 2026,
Jefferson Rojas for Clay Holmes and Tyrone Taylor. The Mets' seat reads
-2.3 realized (Holmes and Taylor produced for Chicago immediately) with
projected final -6.4 (Rojas' rank expectation +4.3 against the veterans'
remaining windows); the Cubs' seat projects +3.2 final.
