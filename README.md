# Front Office Ledger

A decision-level accounting system for sports front offices. Every draft pick, trade, signing, and waiver claim, graded against the market expectation for that transaction type and attributed to the executive regime that made it. Inspired by OOTP's Decision History screen; built for real MLB data first, schema designed to extend to other leagues.

## Current state (July 2026)

**Working today**
- `ingest/ingest_transactions.py` pulls the MLB Stats API transaction and draft feeds into SQLite/CSV. Verified coverage: reliable 2005 to present; Retrosheet's transaction file (1870s to 2020) is the planned historical backfill.
- `ingest/assemble_decisions.py` turns raw rows into decisions: trades grouped into deals, FA split major/minor, waiver claims vs losses, Rule 5, passive losses. 1,073 decisions assembled for the Elias regime (BAL), 524 for the Arnold regime (MIL). Person-less rows (picks, PTBNL, cash) route to a review queue.
- Entity resolution: 99.7% of MLBAM ids joined to the Chadwick Bureau register (`data/crosswalk.csv`), carrying B-Ref / FanGraphs / Retrosheet keys for the valuation pass.
- `engine/` holds the scoring methodology, proven on two proofs of concept: the Betts trade (three-lens scoring with retention rights) and the full Elias regime (draft slot curve, maturity schedule, all four channels).
- `prototype/index.html` is the product prototype: leaderboard, regime report cards, transaction trees, lens matrices, dark/light themes. Orioles card is scored end-to-end with real data; most other values are labeled sample data.

**THE 30-REGIME SWEEP (new):** every active MLB front office scored automatically. `ingest/sweep_ingest.py` pulls all 30 clubs' transactions from each regime's start (108k rows, floor 2005), `engine/sweep_score.py` values 13k players with Ledger WAR v0 and grades trades / drafts / waivers per regime (FA pending a contracts feed), and `ingest/integrate_sweep.py` splices the results into the prototype leaderboard. Regime table: `data/regimes.json`; results: `data/sweep_results.json`.

**IFA CHANNEL (new, sweep v1.2):** international amateur signings graded as their own channel. Signings auto-classified from the feed (minor-league deal, age <= 23 at signing, born outside draft territory, first pro appearance); realized value on the signing org graded against the league's realized value per signing class among observed regimes, which works because bonus pools are near-equal since 2017 (pre-2017 classes flagged uncapped). `engine/ifa_score.py`.

**FA CHANNEL GRADED (sweep v1.3):** 1,594 real contracts (ESPN free-agent tables 2006-2021, parsed by `engine/fa_grade.py` from `data/contracts_espn.csv`, plus curated majors for the 2022-2024 winters in `engine/contracts_recent.py`; verify pass complete, 58/58 exact matches against offseason trackers for the two fully-checked winters). Signings graded as realized LVM on the signing org minus contract-implied wins; regimes with fewer than 8 matched deals stay pending. All five channels now grade.

**DEV PILLAR (sweep v1.5):** player development is now its own top-level grade alongside FOR and Success. The archive: MLB Pipeline preseason top-100s, 2011-2026 (1,548 rank-rows, 823 players), pulled from MLB's data-graph GraphQL endpoint (`ingest/pull_ranks.py`); holding org per list derived from minor-league season rosters mapped to parent orgs (`ingest/dev_ingest.py`), so attribution is ours, not Pipeline's. Prospects are marked to market on a rank-to-surplus-wins curve; entry credit is net of acquisition cost (own draft pick vs the pick-value curve, own international signing, or acquired-as-prospect) with an inherited screen (a prospect developed to the list under a predecessor regime earns the new regime nothing at entry); year-over-year rank moves accrue to the org holding the player; graduation to MLB is a neutral exit; falling off without debuting is charged. Grades are league-relative because development is positive-sum (league rate: about +2.5 wins of prospect value per club-season). `engine/dev_score.py`; per-regime farm flows and current farm value included. Development credit stays home even when the prospect is later traded, which is the point.

**EXTENSIONS CHANNEL (sweep v1.6):** contract extensions graded as their own decision type, against the extension market for the player's service class rather than FA prices (the pre-arb discount is structural; picking which player to lock up, and at what price, is the skill). Class discounts of open-market $/win: pre-debut 0.35, early 0.45, arb 0.60, veteran 0.90 (documented assumptions, tunable when the book supports empirical fits). Curated book of ~60 major extensions inside current regime windows (`engine/contracts_ext.py`; the 2025-26 wave verified by web search: Guerrero 14/500, Crochet, Raleigh, Basallo, Anthony, Baz, Emerson, Griffin, Crow-Armstrong, Luzardo, Soderstrom, Wilson, Pratt). Deferral-heavy deals are costed at CBT/present value (Betts $306.7M PV, Ohtani $460.8M in the FA channel), and qualifying-offer signings now carry a draft-compensation charge on the FA ledger (confident QO list, flat second-round-pick value). Same-name collisions (two Jose Ramirezes, two Will Smiths) resolved by club fit. `engine/ext_grade.py`.

**RETROSHEET BACKFILL INGESTED:** the full 1873-2022 transaction archive (101,594 rows) is loaded as `retro_tx` and shipped in `data/retrosheet_tranDB.zip`. The information used here was obtained free of charge from and is copyrighted by Retrosheet. Interested parties may contact Retrosheet at www.retrosheet.org.

**SWEEP v2:** three rigor upgrades to every number on the site. (1) Trades now use control windows: value counts while the player stays with the club (6-season cap) and the window closes the first season he logs MLB time only elsewhere, so a re-signing is a new decision instead of leaking into the trade grade. (2) Win-curve leverage and time discounting apply sweep-wide on trades: each delivered season is weighted by L(w) at the receiving club's win total (wins delivered to a contender count up to ~1.8x, wins to a 70-win club ~0.65x) and discounted 10%/yr back to the deal date. (3) The Success grade now includes real postseason detail ingested from the league schedule feed 2005-2025 (`engine/postseason.py`, `data/postseason.json`): berths, series wins, pennants, and titles blend with W% and division titles. FA and waiver channels stay unweighted (cost and value accrue in the same seasons, so leverage cancels to first order).

**Methodology version: v0.2** (win-curve leverage, time discounting, retention rights, net-of-cost contracts, perspective rule). See `docs/methodology-v02-addendum.md`. The v0.3 target: empirical market-price baselines for trades (the rental-return curve) that consolidate the lens stack; see `docs/design.md` section 3.4b.

**The one missing stage: valuation.** Per-person per-season WAR keyed off the crosswalk. Paths: a FanGraphs data license, or self-computed open WAR from Retrosheet event files. B-Ref and FanGraphs block unlicensed programmatic access (verified); do not build on scraping.

## Repository layout

    docs/       design doc, proofs of concept, methodology addenda, pipeline report
    engine/     scoring methodology (Betts scorer, Elias full-regime ledger, v0.2 leverage+discounting)
    ingest/     MLB Stats API ingestion + decision assembler
    prototype/  self-contained HTML product prototype
    data/       ingested transactions, draft picks, assembled decisions, Chadwick crosswalk

## Quickstart

    # refresh a team's transaction log (Orioles = 110)
    python3 ingest/ingest_transactions.py --team 110 --start 2018-11-01 --end 2026-07-21

    # pull draft classes
    python3 ingest/ingest_transactions.py --draft 2019 2020 2021 2022 2023 2024 2025

    # assemble decisions and show a deal from both sides
    python3 ingest/assemble_decisions.py --show "Corbin Burnes to Baltimore"

    # run the proofs of concept
    python3 engine/score_betts_trade.py
    python3 engine/elias_ledger.py
    python3 engine/methodology_v02.py

## Roadmap (short form)

1. ~~Valuation feed → auto-generated cards for all 30 teams~~ DONE (Ledger WAR v0 + 30-regime sweep)
2. ~~Historical prospect-rank archive → development credit, farm-system flows~~ DONE (DEV pillar, sweep v1.5); still to come from the same archive: the v0.3 rental-market baseline
3. ~~Extensions channel~~ DONE (sweep v1.6, class-market baselines + QO charges + CBT deferral costing)
4. Regime table curation 2000 to present (the moat: nobody maintains this publicly)
5. Retrosheet backfill for pre-2005 history; NBA schema pilot; v0.3 rental-market baseline from the prospect archive

Full detail: `docs/design.md`.
