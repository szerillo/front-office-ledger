# Pre-registration (round 44, to run AFTER the regrade): do letter grades and the "#k of 30" ranks hold?
Written before the regrade and before any run. Same rule family as the winter tests (r42, r43).
## A. Report-card letters (overall and the six channels, every graded front office)
Noise: the r42 disagreement draws (sample300 residuals, player residual vectors, seed 20261150, 2,000 draws).
Each channel net moves by the sum of residuals over the player-seasons behind its graded decisions (built from the
engine's own decision lists, the same way winter_spec was built); the page's grading rule (rate = net / (seasons + 2),
z against the recomputed spread, GRADE_Z cut points, the overall composite) is rerun on every draw.
Rule: a letter is shown as is if it stays the same letter in at least 90% of draws; otherwise, if it stays within one
step either side (e.g. B to B+ ... B- to B) in at least 90%, the card shows that two-letter range; otherwise the card
shows the grade as "not firm" with the range that holds 90%. Fixed now: 90%, the draws, one step.
## B. Horizon "#k of 30" and farm "#k of 30"
These are projections, so their noise is projection error, not WAR-source disagreement: player-level residuals of
the engine's projections against what happened (its own back-test, projections made for 2018-2021 scored on
2022-2025; built before the run if no back-test file exists). 2,000 draws, seed 20261150.
Rule: a club's rank is shown only if it holds against both neighbours in 90% of draws; otherwise the club shows a
band (top 10 / middle 10 / bottom 10) if its band holds in 90%, else no rank.
Either part can only remove or widen a public claim; neither can add one.
