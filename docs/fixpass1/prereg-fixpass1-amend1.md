# Fix pass 1, amendment 1 (Nov 11, 2026, before any run on the new ledger)

Amends `docs/prereg-fixpass1.md` (5e81190). The pass bar and the fail conditions are unchanged.

## Why
Rounds 1 to 4 ran on the Step 0 frozen ledger. That ledger is not shaped like production: its feed rows were built
from the league-wide transactions feed with team_id set to the receiving club only, and with tx_id, from_team and
to_team empty. 7,661 of 7,661 trade rows from 2009 on have no clubs, so the trade grader keeps 1,443 trades
against 4,172 in production (2009 to 2026: 13 to 32 a year against 96 to 240). Every live-vs-sandbox comparison is
dominated by that. Determinism found on that input does not cover the 2009+ trade paths.

## Change
- New input: `ledger_v2.sqlite` (md5 d192a2bd), built the way production is: `ingest/hist_ingest.py` logic (each
  club, each year 2005 to 2026, rows tagged with the querying club, tx_id, from_team, to_team), end date 2026-11-10
  (the frozen ledger's last date), then `ingest/retro_backfill.py` for 1985 to 2008, then the frozen ledger's
  draft_picks (content md5 b834d37d). 282,564 rows; 15,265 trade rows from 2009 on, 32 without a from_team.
- Network: one record pass on ledger_v2 with the patched engine (cache seeded from the Step 0 cache, new calls
  recorded). All later runs replay only and abort on any miss.
- Shuffles: the same seeds (20261161 to 20261165) applied to ledger_v2.
- Engine: rules 1 to 11 as traced in `docs/fixpass1/traces.md`, rule 6 as amended (sourced Bello override).
- Runs: W0 unshuffled, W1 to W5 shuffled, W6 reversed reads. Plus one unpatched baseline (RV0) on ledger_v2 for the
  secondary bar.

## Unchanged
Primary bar: one md5 per published file across W0 to W6. Fail: more than one md5 in the final round, any guard abort,
any value change between W0 and RV0 not traced to a rule, or a change to the bar after the first run.

## Known limit
Production's ledger is not available (the /work copy is a 0-byte file). The partial-first-year behaviour of
`sweep_ingest.py` and the order the two ingest scripts ran in are unknown, so ledger_v2 can still differ from
production. The live comparison will report every difference.
