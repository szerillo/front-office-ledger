# Front Office Ledger

A decision-level accounting system for sports front offices. Every draft pick, trade, signing, and waiver claim, graded against the market expectation for that transaction type and attributed to the executive regime that made it. Inspired by OOTP's Decision History screen; built for real MLB data first, schema designed to extend to other leagues.

## Current state (July 2026)

**Working today**
- `ingest/ingest_transactions.py` pulls the MLB Stats API transaction and draft feeds into SQLite/CSV. Verified coverage: reliable 2005 to present; Retrosheet's transaction file (1870s to 2020) is the planned historical backfill.
- `ingest/assemble_decisions.py` turns raw rows into decisions: trades grouped into deals, FA split major/minor, waiver claims vs losses, Rule 5, passive losses. 1,073 decisions assembled for the Elias regime (BAL), 524 for the Arnold regime (MIL). Person-less rows (picks, PTBNL, cash) route to a review queue.
- Entity resolution: 99.7% of MLBAM ids joined to the Chadwick Bureau register (`data/crosswalk.csv`), carrying B-Ref / FanGraphs / Retrosheet keys for the valuation pass.
- `engine/` holds the scoring methodology, proven on two proofs of concept: the Betts trade (three-lens scoring with retention rights) and the full Elias regime (draft slot curve, maturity schedule, all four channels).
- `prototype/index.html` is the product prototype: leaderboard, regime report cards, transaction trees, lens matrices, dark/light themes. Orioles card is scored end-to-end with real data; most other values are labeled sample data.

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
