# Plan: launch items 5 and 6, plus the order check (paper only, Nov 11 evening)

Nothing here is deployed. Each step names how it is verified. Deploys need Sean's OK.

## 0. Before either item: shuffle test of the trade pipeline

Why first: items 5 and 6 both regrade trades, and the trade grader has unordered reads (44 listed in
`tests/tools/r22_unordered_selects.txt`; `sweep_score.py` and `hist_score.py` 4 each, `trade_book.py` 1).
Regrading on an order-dependent build would mix the fix with order noise.

1. Sandbox copies of `sweep_score.py`, `hist_score.py`, `trade_book.py` with only I/O paths changed (the
   `tests/tools` runner pattern used for `fa_grade.py`; `/work` mtimes checked before and after).
2. Run them on 5 shuffled `sweep_tx` tables and with `PRAGMA reverse_unordered_selects=ON`.
Blocker found tonight: `sweep_score.py` and `hist_score.py` fetch from the network (`ledger_war.get`, `API`),
   `trade_book.py` imports `urllib`, both score scripts rewrite `/work/lvm_cache.json`, and `asset_rules.py`
   hardcodes `/work/ledger.sqlite`. A safe sandbox needs those paths redirected and the network calls served
   from cache (fail closed if a fetch is attempted). Not started; first job of the next session (size M).
3. **Verified when:** the trade book and both result files have one md5 across all runs. If not: list each
   differing trade side, find the read that causes it, and patch it the same way (ORDER BY or an explicit sort),
   then repeat.

**Status (Nov 11, 23:40 UTC): built and run; FAIL.** See `tests/tools/step0_results.json` and audit section 28.
Items 5 and 6 wait until the order fixes pass Step 0.

## Item 5: engine side of the same-club re-sign rule

Patch exists: `docs/patches/engine-resign-rule.diff` (applies cleanly to `engine/asset_rules.py` at main, checked
tonight). It sorts each player's events, so it does not depend on read order.

1. Apply in the sandbox to the repo copy of `asset_rules.py` (not `/work/asset_rules.py`, which already carries a
   different unreleased version).
2. Regrade trades in the sandbox (after step 0 passes).
3. **Verified when:**
   - Henriquez 2022 MIN moves -1.2 to about +0.3 and Eli White 2023 ATL -0.1 to about +1.1 (round 15 sizing);
   - exactly the 36 pieces / 72 sides from `tests/tools/engine_resign_check.py` change, nothing else;
   - every changed side's two seats still add to zero;
   - `t_grades` diff lists only those sides, written to `docs/grade-changes.md` with a REASON.
4. Depends on item 4 (the page rule) for the OPEN labels to agree; ship both together.

## Item 6: service-time control end

1. Replace the debut-year control end with the service-time end (last season starting under 6.000 years), from
   the engine's service data, falling back to Baseball-Reference starting service for the 7 players with holes
   (deGrom and others), then to the debut rule.
2. Regrade extensions and trades in the sandbox (after step 0).
3. **Verified when:**
   - `tests/tools/control_end_check.py` reproduces today's grades exactly with the old rule (baseline);
   - with the new rule, the 6 hand-checked players (Olson, Polanco, Díaz, Taylor, Glasnow, deGrom) get the ends
     Baseball-Reference service time gives;
   - the change matches the round 7 sizing (about 71 grades by a win or more, Olson extension +12.0 to about
     +3.8) or every difference is explained;
   - a seeded 10 of the changed grades are hand-checked against service time, plus 10 unchanged ones;
   - `t_grades` diff logged with a REASON.
4. Ships only with Sean's OK, after item 5 or with it.
