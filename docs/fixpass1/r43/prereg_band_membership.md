# Pre-registration: does "Among the 20 best/worst" hold? (written before any membership run)
Round 43, Nov 12 2026. Committed with membership.js before it is run.
Draws: exactly the r42 threshold design (sim.js at 79632bb: same sample300, winter_spec, seed 20261150, 2,000 draws,
residual vectors per player as written). No new settings (Kirk: do not re-run with a new correlation setting).
Statistic: for each settled winter, the share of draws in which its simulated total is among the 20 highest
(P_top) and among the 20 lowest (P_bot) of the 697 settled winters.
Rule: a winter keeps "Among the 20 best" only if its published total ranks in the 20 best AND P_top >= 0.90;
"Among the 20 worst" only if it ranks in the 20 worst AND P_bot >= 0.90. Every other winter shows no band and no rank
(share page, preview image and the offseason explorer). Reported for published ranks 1-30 on each side; the decision
uses ranks 1-20 only. The independent-seasons column is reported, not used.
Known bias, stated before the run: the design applies one residual to all of a player's seasons (measured
season-to-season correlation 0.18), which overstates the spread of totals, so this test is strict: it can deny a
band that would hold, not grant one that would not.
