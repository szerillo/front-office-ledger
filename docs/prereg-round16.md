# Pre-registration, round 16 (two salary-row checks)

Written and committed before either draw is run. Commit time of this file is the pre-registration time.
Script: `tests/tools/prereg16_draw.py` (committed with this file). Fixtures as of commit 27277cd.

## A. Does Baseball-Reference store the full 2020 rate for traded and minimum-deal players?

- Population: distinct 2020 salary rows in the three Nov 11 fixtures, excluding the ten players checked post hoc in
  round 16, where the player had stints with two or more clubs in 2020 or the row is $600K or less. There are 9
  such rows, fewer than the 10 asked for, so all 9 are checked (no seed).
- Second source: Spotrac, Cot's, AP or a club announcement giving the 2020 full-season salary. For a minimum deal
  the full rate is $563,500.
- Pass: the row is within 5% of the full-season rate. Fail: it matches the prorated amount, or neither.
- Report: passes out of 9 with a Wilson 95% interval, and each fail with its source.

## B. Is Diaz 2023 the only large row with no outside match?

- Population: distinct salary rows of $15M or more in the same fixtures (70 rows, 19 players).
- Draw: 20 rows, `random.Random(20261131).sample`, as in the script.
- Second source: Spotrac's season figure for that player and year (base salary, and base plus the season's share
  of any signing bonus); Cot's or a contemporary report if Spotrac does not show it.
- Mismatch: the row differs by more than $500K from every figure the source gives for that season.
- Report: mismatches out of 20 with a Wilson 95% interval, each with the figures found.

## Not allowed after this commit

Changing the populations, the seed, the tolerances, or dropping rows by hand.
