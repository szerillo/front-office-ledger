# Amendment to prereg r51 (28d2959), round 52. Kirk GO, Nov 12 15:27 ET. Written before any run below.

Change: the two plant runs (PU, PF) skip champions_build and use the baseline championship file. The real run F2 keeps
the step. Nothing else in the prereg changes (order, bars, D sizing rule, evaluator eval_v2.py).

Guard (a), checked before running (champs_proof.json):
- Baseline championship file (Z_X6 champs_computed.json) md5 0ced72a00e3c083717defa0914a8cea5; copied into each plant
  run and md5-checked after every step.
- From the instrumented read logs and the sandbox write log, followed transitively: one step reads it (regen_v3),
  and everything downstream of it is cards.js, moves.js, the prototype page and the names cache. Graded files the
  evaluator scores (sweep_results, hist_results, trade_book, offseasons, trade_parts) downstream of it: 0.
- So in the plant runs only the championship sections of cards.js and moves.js are held at baseline, and the plant
  bars never read them.

Guard (b): PU (plant, nothing frozen) runs first and must trip (at least one untraced letter or unattributed net
against live) and reach the sizing bar (re-fit path PU minus PF at least 258 nets and 31 letters; D doubles to 2.0
and 4.0 if not). If PU does not trip: stop, grades held.
Guard (c): then PF (plant, full freeze) must pass against FZ2; then F2 once.

Innings decimals: not in this re-grade. The 712/315 prediction was measured with every fit re-fitting (round 43,
run D2), so a frozen re-grade cannot reproduce it, and adding it would mix two changes in one diff. After launch.
