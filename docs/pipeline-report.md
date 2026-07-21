# Pipeline Report: From Raw Feed to Decision Ledger
### Ingestion + decision assembly + entity resolution, all running · July 2026

## What now exists, end to end

The three-stage pipeline from the design doc is no longer theoretical. Stage 1 (**ingest**) pulls the MLB Stats API transaction and draft feeds into SQLite: 4,561 Orioles rows (Nov 2018 to present), 2,432 Brewers rows (Oct 2022 to present), 4,449 draft picks (2019 to 2025) with bonuses and slot values. Stage 2 (**assemble**) turns rows into the ledger's unit of account: **1,073 decisions for the Elias regime and 524 for the Arnold regime**, classified by channel. Stage 3 (**resolve**) joins every MLBAM id to the Chadwick Bureau register: **5,488 of 5,505 ids matched, 99.7%**, giving each person their B-Ref, FanGraphs, and Retrosheet keys so any WAR source can attach in the valuation pass.

## The decision counts (real, assembled automatically)

| Channel | Elias (BAL, 7.6 yrs) | Arnold (MIL, 3.7 yrs) |
|---|---|---|
| Trades | 120 | 74 |
| FA, major league | 45 | 28 |
| FA, minor league | 498 | 284 |
| Waiver claims / losses | 121 / 61 | 8 / 20 |
| Rule 5 (+ minors phase) | 3 | 9 |
| Passive losses (walks, releases) | 79 | 45 |
| Extensions & other signings (review queue) | 146 | 56 |

Two regime signatures pop out of nothing but counts: Elias claims off waivers 15x more often than Arnold (121 vs 8), which is the found-money A+ channel visible in raw behavior, while Arnold trades at nearly double Elias's per-season rate. Channel behavior alone is a fingerprint.

## The two-sided test: one deal, both ledgers

The assembler groups trade rows by (date, description) and splits assets by direction relative to the focal team. The Burnes trade assembles automatically and symmetrically:

**[BAL] 2024-02-01** · IN: Corbin Burnes · OUT: DL Hall, Joey Ortiz · flag: 2 unresolved rows
**[MIL] 2024-02-01** · IN: DL Hall, Joey Ortiz · OUT: Corbin Burnes · flag: 2 unresolved rows

The unresolved rows are the traded Competitive Balance pick, exactly the case the design doc predicted: picks, PTBNLs, and cash arrive as person-less rows and route to a human review queue (70 of 120 Elias trades and 41 of 74 Arnold trades contain at least one). That queue is the real curation cost of the product, now measured: on the order of a few hundred rows per franchise-decade, not thousands.

## What the feed taught us

Coverage is reliable from about 2005 forward (roughly 6,000 rows per month league-wide), thin 2000 to 2004, empty 1985 to 2000; Retrosheet's transaction file covers 1870s to 2020, making 2005 to 2020 the cross-validation overlap. A few feed quirks are now handled in code: departures ("elected free agency") carry the losing club in `to_team`, not `from_team`; FA signings appear as duplicate rows (signing + status change) needing dedupe; each trade appears once per club side. The register join also quantified a known truth: only about 1,050 of the 5,488 matched persons have a B-Ref key, because most drafted players never reach MLB. That is not a gap, it is the draft channel's survival curve visible in the identity data.

## What unlocks next

The missing stage is **valuation**: per-person, per-season WAR keyed off the crosswalk we just built. The moment that feed exists (FanGraphs license, or self-computed from Retrosheet/Statcast), the Arnold card, the leaderboard, and every transaction tree generate from queries. Everything else about the second team's card is already automated. Interim option: hand-curate WAR for just the ~40 highest-consequence Arnold decisions the assembler surfaced, the same way we did Elias, and ship the two-sided Burnes tree with live data on both ledgers.

*Scripts: `ingest_transactions.py`, `assemble_decisions.py`. Outputs: `ledger.sqlite` (transactions, draft_picks, crosswalk), `decisions_orioles.csv`, `decisions_brewers.csv`.*
