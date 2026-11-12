# Prereg (round 52): Kinley rule re-score with truth v2. Written before any re-score.

Why: round 51 found the truth used in round 50 counted neither DFA limbo nor retroactive injured-list days, both of
which earn service (Anderson 2023 was a truth error, not a counter error).

Truth v2 (truth_v2.py): a season day counts if the player is on an MLB club's active roster (daily roster service),
on the MLB injured list (from the retroactive date when the filing states one, else the filing date, to activation),
in DFA limbo after a designation by an MLB club (to the outright, release, claim, trade, option, recall or free-agent
election), or on optional assignment when his option days that season total fewer than 20. Scaled to 186 days and
capped at 172, as the counter is. Simplifications stated now: the September and post-Labor-Day option rules are not
modelled.

Re-score: the same rule v1 (round 49 prereg b2477dc), the same 19 player-seasons (frame.json, round 50), the same
counters (old, and new with rule v1). No change to the rule.
Bar (unchanged): at least 19 of 19 within 10 days of truth; Kinley 2026 counted 172; existing plants pass.
Also reported, not a bar: how many of the 184 frame player-seasons have 1 to 19 option days, and the largest
service change if those days were credited.
Fail: report and stop; no rule change in this round.
