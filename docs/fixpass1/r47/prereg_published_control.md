# Pre-registration: grades on published control end (round 47, written and committed before any engine output)

## Hypothesis
Replacing the debut rule (six seasons from MLB debut, one more for a debut after mid-April) with the control end
implied by published official service time, for the players who have one, changes grades only through those
players' decisions, and moves letters and the one winter band no more than the bars below.

## Change (engine copy i = live engine f + one edit)
engine/asset_rules.py control_span(rec, pid): if pid is in docs/fixpass1/r46/published_service.json (commit b699341;
1,366 players, MLB Trade Rumors arbitration posts 2015-2020 and 2023-2027), the last season of control is that file's
ctrl_end; the first season is unchanged. Everyone else keeps the debut rule. Nothing else changes: same caches
(ledger_v3, lvm_cache, names pinned), same steps, same order. trade_comps.py and controlled_market.py keep their own
control years (they price market comparisons, not grades). The innings fix is not included.
Changed players (CH): the published players whose ctrl_end differs from the live control_span end.

## Run
One run, I1, compared with the live engine run Z_X6. regen_v3, if its guard aborts on a cache miss, is skipped as in
rounds 43 and 45 (its outputs are not used for grades).

## Metrics
1. Channel letters (front office x channel, 662 rows) recomputed with the published letter cutoffs (docs r43 method,
   letters.py); count that change.
2. Overall front office grades (forGrade in sweep_results.json and hist_results.json); count that change.
3. Club-winter totals (offseasons.json) and the band: Toronto 2012-13's rank from the bottom and its margin over the
   21st-worst winter.
4. Trade-side nets shown to 0.1 (trade_book.json).

## Traced vs untraced
A change is traced if the front office (or trade, or winter) has at least one decision involving a CH player:
- channel letter or overall grade: a CH player appears in that front office's record for that channel (allx lists,
  allx_fa, allx_intl by id; allx_ext by name), or, for trades, in a trade_book trade by its club inside its seat dates;
- trade-side net: the trade includes a CH player;
- winter total: the club-winter has a decision involving a CH player.
Everything else that changes is untraced (it can only come through the calibration refit).

## Bar (all must hold, or the run fails)
- channel letters that change: at most 150 of 662 (a uniform one-year shift for every player moved 133, round 45);
- overall grades that change: at most 40;
- untraced channel letters or overall grades: at most 5;
- untraced trade-side nets that move by more than 0.2: at most 50;
- band: Toronto 2012-13 stays first or second from the bottom and keeps at least 90% of its live margin over the
  21st-worst winter; otherwise the band would change and the run fails.
- untraced pages (front office or club-winter pages with an untraced change): at most 50.

## If it passes
Deploy under the usual gates: data commits, index gate, all 19 suites before and after, staged = live hash, every
changed number traced as above, rollback on red. Then step 2 (mark the letters that flip under a one-year control
shift) is computed on these grades.
## If it fails
Report the numbers and stop. No variants, no retuning, nothing deployed from it. Step 2 is then computed on the
live grades.
