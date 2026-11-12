# Round 49 run note, written 2026-11-12T18:17:38Z before any freeze run starts
Prereg: docs/fixpass1/r49/prereg_calib_freeze.md (b2477dc). Runs, in order:
- FZ0: freeze check. Engine f (live) plus the freeze only. Bar: every graded letter, overall grade, channel net,
  trade-side net and winter value identical to Z_X6.
- FP: spread plant. FZ0 setup plus +5.0 on one extension. Target chosen now from live data only: Edgar Renteria,
  St. Louis, signed 2000-02 (pid 121074), front office stl-walt-jocketty. It is the one front office whose +5.0
  cannot carry it past anyone in the overall or the extension ordering (net per season plus 2), so any other
  front office's letter, net or rank that moves is leakage, not arithmetic. Bar as written.
- F1: engine i (published control end) plus the freeze. R1: engine i with fits on (the re-fit path, measured only).
Letters for every run use the live (Z_X6) per-channel spread and the live cutoffs.
Freeze mechanism: trade_calib and draft_calib steps skipped; ext_grade reads the live class rates; the seven frozen
files are md5-checked after every step (a change stops the run).
