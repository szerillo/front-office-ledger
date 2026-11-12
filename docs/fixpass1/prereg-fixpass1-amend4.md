# Fix pass 1, amendment 4 (Nov 11, 2026, before the final-engine runs on ledger_v3)

Bar and fail conditions unchanged (one md5 per published file across X0 to X6; any guard abort fails).

## Why
Building the deploy candidate on ledger_v2 showed a second shape difference from production: production's
draft_picks table has every column declared TEXT (`ingest/ingest_transactions.py:89`), so `signed` holds '1'/'0'.
ledger_v2 copied the Step 0 table, which has untyped columns and integer 1/0. `archetype.py:202` filters
`signed='1'`, which never matches an integer, so every report card's draft-room line was empty (n 33 to 0 on live
cards) and t_fun's reportDnaBeforeLedgers failed.

## Change
ledger_v3 (md5 f3f56eba) = ledger_v2 with draft_picks recreated with TEXT columns, same rows in the same order
(signed: 7,206 '1', 27,233 '0'). sweep_tx unchanged. Shuffles: the same five seeds applied to ledger_v3.
Engine: round 8 engine + 2020 held rates (a449800) + engine re-sign rule (0f98a54, None-safe event sort) + the
regen_v3 AUTO_REGIMES swap fix (its old end marker deleted 339 lines of page code). Patch: deploy-candidate.diff.
