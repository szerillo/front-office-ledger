# Prereg (round 49): grades on published control end, calibration frozen

Written Nov 12, 2026, before any build or run. Committed to docs/fixpass1/r49 before any engine output exists.
Status: written only. Not run. Run needs a separate GO.

## Why
Run I1 (round 47) failed its untraced bars. Round 48 traced 12 of the 13 untraced changes to the engine re-fitting
its calibration from the outcomes the change touched (ext_class_rate, draft_calib, trade_calib, the grading spread),
and 1 to the tracer missing an accented name. This design removes the first cause by holding every fitted quantity at
the live version, and treats any re-fit as its own path that is measured and attributed separately.

## Inputs fixed now
- Engine: the live engine (run Z_X6) plus exactly one change, asset_rules_i.diff from round 47 (control end from
  published_service.json where a figure exists). No other code change except the freeze below.
- Frozen at the live version (copied byte for byte from runs/Z_X6/work, md5 listed in the run log before the run):
  trade_calib.json, draft_calib.json, ext_class_rate.json, calib_blend.json, calib_results.json, arb_calib_rows.json,
  calib_chart.json, and the grading constants (letter cutoffs Z and the per-channel spread used to turn nets into
  letters, read from the live grade table, not recomputed).
- Freeze mechanism: the fit steps are skipped and the files above are read. The run fails loudly if any fit step
  writes a file (each frozen file is chmod read-only; a write is an error, not a warning).
- Tracer: round 49 tracer (eval_i1_v2.py: names folded with NFKD, accents and case stripped; ids where the entry has
  one). Plant plant_tracer.py must pass before the run.

## Order (stop at the first failure, report, no variants)
1. Freeze check: rerun Z_X6 with the freeze and no rule change. Bar: every graded letter, overall grade, channel net,
   trade-side net and winter value byte-identical to live (0 differences).
2. Spread plant (see D in round49.md): with the freeze, add +5.0 to one extension entry of one front office. Bar: that
   front office's ext net moves by exactly 5.0 and no other front office's letter, net or rank moves.
3. Run F1: freeze plus the published control end. Then run R1: the same change with the fit steps on. R1 is the
   re-fit path; it is measured, never deployed.
4. Evaluate F1 against live.

## Bars for F1 (all must pass)
- Untraced channel letters: 0.
- Untraced overall grade moves greater than 0: 0.
- Every changed number attributed. A changed entry is attributed if it names or carries the id of a changed-control
  player, or sits in a trade seat with one; a changed aggregate (channel net, total, overall grade, rank, winter
  value) is attributed if every entry that moved inside it is attributed. Anything else counts as untraced.
- From round 47, unchanged: channel letters changed at most 150; overall grades changed at most 40; TOR 2012-13 stays
  in the top 2 with at least 90% of its live margin.
- Pages: every changed page traced; stop if more than 50 pages change in a way this prereg did not predict.

## Re-fit path (reported, not deployed)
R1 minus F1, per front office: letters, overall grades and nets that move only because the fit moved. Reported as
its own table. If the re-fit path is ever deployed, it needs its own prereg and a corrections entry.

## Deploy
Only if every F1 bar passes: same gates as every deploy (serial suites 19/19 before and after, staged md5 equals
live md5, every change traced, rollback on red), corrections entry for every letter or grade that moves.
