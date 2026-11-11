# Pre-registration: Step 0, order test of the trade pipeline

Written Nov 11 2026 before the sandbox is built or any chain step is run. Committed before the first run.

## Hypothesis

With the determinism patch deployed (`279379f`), the published files the chain writes are a function of the
input data only: shuffling the row order of `sweep_tx`, or reversing unordered reads, changes none of them.

## What runs

`run_chain.sh` order, from `r5_conduit` through `regen_v3`, with the repo engine at main (`279379f` or later,
md5 of each script recorded), on a sandbox copy of `/work` with `ledger.sqlite` replaced by the backfilled
rebuild (`/tmp/sweep/ledger_r.sqlite`, 9-column production schema). `debut_fetch` is skipped (it only fetches).
Any step that tries the network is stopped and reported as blocked, not passed.

Sandbox rules (all enforced, not assumed):
- private mount namespace: the sandbox copy is bind-mounted at `/work`, so the real `/work` cannot be written;
  real `/work` checksums are taken before and after every run and must not change;
- private network namespace (no interfaces), plus a Python audit hook that aborts on any socket connect or name
  lookup, any urllib request, and any write outside the sandbox;
- clock frozen: `time.time`, `datetime.now`, `date.today` return a fixed instant (2026-11-11 12:00 UTC);
- `PYTHONHASHSEED=0`.
The guard is shown aborting on a deliberate violation (a write to the real `/work`, a socket connect) before
the first real run.

## Runs

- R0: unshuffled table.
- R1 to R5: `sweep_tx` rows shuffled with seeds 20261161 to 20261165.
- R6: unshuffled, `PRAGMA reverse_unordered_selects=ON` on every SQLite connection.
- R7 (purity check, secondary): unshuffled, clock frozen at 2026-12-15 instead.

## Metric

md5 of each published file the chain writes: `cards.js`, `index.html`, and from it `book.js` and `deals.js`
(`split_book.py`), `offseasons.json`, `trade_parts.json`, plus the intermediates `trade_book.json`,
`sweep_results.json`, `hist_results.json` (for diagnosis only).

## Pass bar

- Primary: every published file has one md5 across R0 to R6.
- Secondary: R7 equals R0 on every published file. If not, the clock is an input; list where it enters.
- Not a pass: any step blocked by the network guard. Report which step and which call, and stop.
- If a published file differs: list the differing records, trace each to a read in
  `tests/tools/r23_select_risk.md`, and fix only after Sean's OK. No changes to the bar after the fact.
