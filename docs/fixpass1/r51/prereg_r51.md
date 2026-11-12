# Prereg (round 51): published control end with every in-run fit frozen, inventory from evidence

Written Nov 12, 2026 before any run below. Committed to docs/fixpass1/r51 before the first run. One run of F2.

## Inventory (evidence, not code reading)
Instrumented runs FZ0i (live engine, round 50 freeze) and F1i (published control end, round 50 freeze) logged, for
every step: each file read and its md5, every module global at exit (kind, size, value hash, numeric or not), and
every statistics/numpy estimator call (site, input hash, output hash). inventory_F1.json lists what differs.
Read as fits (a value computed from the whole population and applied to other players), each confirmed by the log:
1. ext_grade class rates (`_acc` changes): already frozen (round 50).
2. ifa_score `class_tot` / `class_n` (22 classes): the international class baseline. NOT frozen in round 50.
3. regen_v3 `MOVE_BANDS` (6 bands, read from the move_pop files): move-letter bands. NOT frozen.
4. regen_v3 style statistics (statistics.mean and pstdev at regen_v3.py:51-52, 15 traits): style tags. NOT frozen.
5. reliability.py `A`, `B` (reliability.json): the reliability weights the page uses. NOT frozen.
6. validation.py regression (validation.json): reported statistics read by regen. NOT frozen.
Read as not fits (loop leftovers or per-player values): ext_grade prior and arb, hist/sweep `ynet` `total` `dr_net`
and the like, trade_book `net` `match` `miss`, scenario_build `_out`, regen loop counters, `_EXTSAL` and `_COST`
(per-player salary schedules that follow the control end itself).

## Freeze (new in this round)
- Items 2, 3, 4: record and replay. A record run (B0: live engine, round 50 freeze, RECORD on) writes the live value
  at each site; frozen runs read it back (FREEZE2). Code change: ifa_score.py and regen_v3.py, one `_fz` call each.
- Items 5, 6: reliability.py and validation.py are skipped and the live reliability.json and validation.json are
  copied in and md5-checked after every step, with the round 50 files.
- Everything frozen in round 50 stays frozen.

## Evaluator (eval_v2.py, fixed now)
Same as round 50 with two repairs found while diagnosing round 50 (evaluator only, round 50 is not re-scored):
trades are matched by date and the set of clubs (not one seat per date and club), and a winter move is attributed
through its whole trade (the winter list names only the lead player). Letters use the live spread and cutoffs.

## Order (stop at the first failure, report, no variants)
1. B0 record run. Bar: identical to live (0 differences).
2. FZ2 freeze check: live engine, full freeze. Bar: identical to live (0 differences).
3. Sensitivity check with the plant: +D on every season value of the 846 changed-control players (lvm_cache, before
   any step), D = 1.0.
   - PU: plant, nothing frozen. PF: plant, full freeze.
   - Plant size: the re-fit path PU minus PF must be at least as large as the one measured in round 50
     (258 nets and 31 letters). If smaller, D doubles (2.0, then 4.0); the first D that reaches it is used. If 4.0
     does not, stop: the plant cannot be sized and no real run happens.
   - The plant must trip on the unfrozen run: PU against live shows at least one untraced letter or unattributed
     net. If not, stop.
   - The plant must pass on the frozen run: PF against FZ2 shows 0 untraced letters, 0 untraced overall moves and
     every changed number attributed. If not, stop.
4. F2 (once): published control end, full freeze. Instrumented.

## Bars for F2 (all must pass)
- Untraced channel letters: 0. Untraced overall moves: 0. Every changed number attributed (nets, entries, trades,
  winters).
- Inventory: no fit site in items 1 to 6 differs from live in the F2 log.
- From round 47: letters changed at most 150; overall at most 40; TOR 2012-13 in the top 2 with 90% of the live margin.
- Untraced pages: 0 (it follows from the first bar).

## Deploy
Only if all pass, under the usual gates, with the page-side spread, composite spread and reliability weights held
at their live values, and a corrections entry for every letter or grade that moves. Any change to the deploy needs
Kirk's GO after the result.
