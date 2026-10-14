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
