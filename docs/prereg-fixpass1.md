# Pre-registration: fix pass 1 for the Step 0 order dependence

Written Nov 11 2026 before any fix is written. Committed before the first patched run.

## Target files and rules

1. `engine/ret2.py:77` (league expectation curve). The 82 Declared Free Agency filings that sit under two clubs in
   one year are two separate departures: in all 82 the two clubs filed on different dates (median 144 days apart,
   1 under a week; checked before this file). Rule: key departures by (player, club, year), so each club's departure
   counts once. Same-club duplicates (63 keys, feed and Retrosheet rows of one filing) still count once; for them the
   kept row cannot change the result, since only the club and the year are used. Read order made total with
   `ORDER BY date, team_id, tx_id, description`.
2. `engine/ret2.py:164` (per-club pass): same total `ORDER BY`, so the name used for the QO lookup is the earliest row.
3. `engine/trade_book.py:73`: total `ORDER BY date, tx_id, person_id, description, from_team, to_team`; player
   lists inside each seat sorted by player id; display name = the name on the player's latest-dated row (later rows
   win, ties broken by the ORDER BY).
4. Anything else is patched only after it is traced: a recorded difference in a published file, the read that
   causes it (file:line), and the rule chosen, written into the results before the patched run. Tracing covers
   `moves.js`, the desk data and `cards.js`.

## Runs (same sandbox, guard and frozen inputs as Step 0, `3f0018a`)

F0 unshuffled; F1 to F5 with the Step 0 shuffle seeds 20261161 to 20261165; F6 with
`PRAGMA reverse_unordered_selects=ON`. Clock frozen at 2026-11-11 12:00 UTC. Iterations allowed: patch, rerun all
seven; each iteration's patches are listed with their trace before its runs.

## Pass bar

- Primary: one md5 per published file (`cards.js`, `moves.js`, the page, `offseasons.json`, `trade_parts.json`)
  across F0 to F6.
- Secondary: every value that differs between F0 and Step 0's R0 traces to one of the rules above.

## Counts as a fail

- Any published file with more than one md5 across F0 to F6 in the final iteration.
- Any guard abort (network miss, write outside the sandbox, subprocess).
- A value change between F0 and R0 that no rule explains.
- Changing this bar, the seeds or the runs after the first patched run.

Nothing is deployed. Applying the patch is Sean's call.
