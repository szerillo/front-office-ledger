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

**RETROSHEET BACKFILL INGESTED:** the full 1873-2022 transaction archive (101,594 rows) is loaded as `retro_tx` and shipped in `data/retrosheet_tranDB.zip`. The information used here was obtained free of charge from and is copyrighted by Retrosheet. Interested parties may contact Retrosheet at www.retrosheet.org.

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

1. Valuation feed (license or self-computed WAR) → auto-generated cards for all 30 teams
2. Historical prospect-rank archive (top-100s, FV grades) → development credit, farm-system flow rankings, and the v0.3 rental-market baseline (one dataset feeds all three)
3. Regime table curation 2000 to present (the moat: nobody maintains this publicly)
4. Retrosheet backfill for pre-2005 history; NBA schema pilot

Full detail: `docs/design.md`.
