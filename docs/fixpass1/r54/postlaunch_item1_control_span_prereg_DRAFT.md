# Post-launch item 1 (queued Nov 14, NOT run before launch): control-span prereg, DRAFT

Status: draft for Kirk's review. It becomes a prereg only when committed under its own name with a GO, before any run.
Purpose: reach F2 (grades on published control end) with a plant that tests the fits the control-end change moves.
Base: prereg_r51.md (28d2959) and amendment_r52.md (55394df). Same freeze (round 50 files plus the round 51 record and
replay of the international baseline, move bands and style statistics; reliability and validation held), same
evaluator (eval_v2.py), same F2 bars.

What changes: the plant.
- Round 52's plant added +1.0 win to every season of the 846 changed-control players. It moved fits the control-end
  change never touches (contract_book typical_fa), so the frozen plant failed for reasons that say nothing about F2.
- New plant: move control spans, not wins. Draw 846 players (seed 20261116) from the players whose control end the
  rule does NOT change, matched to the changed-control players on debut decade and acquisition channel, and end
  their control one season later (the round 45 C1 change, applied to that set only). Wins, salaries and the
  changed-control players stay as live.
- Target set for attribution = the planted players. Every changed entry must carry a planted player; anything else
  is leakage.

Order (stop at the first failure, report, no variants):
1. Record run and freeze check (must reproduce live byte for byte, as rounds 51 and 52 did).
2. PU: plant, nothing frozen. Must trip (at least one untraced letter or unattributed net) and the re-fit path PU
   minus PF must be at least 258 nets and 31 letters; if smaller, plant 2 extra seasons, then 3; if 3 does not reach
   it, stop.
3. PF: plant, full freeze. Must show 0 untraced letters, 0 untraced overall moves and every changed number
   attributed against the freeze check run.
4. F2 once. Bars from prereg_r51.md.
Runs keep the championship-ledger step unless it stops on the network; if it does, the round 52 amendment applies
(baseline file, md5-checked, plant runs only).

If F2 passes: re-grade deploy with every gate (allsuites_v3 before and after, staged diff equal to the predicted
pages, the under-review labels removed only where the value changes, review_check updated, rollback tested,
corrections entry with the counts).
