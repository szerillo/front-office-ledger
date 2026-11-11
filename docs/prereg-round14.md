# Pre-registration, round 14: arbitration correction, better-powered test

Status: design only. Nothing below has been run. Commit time of this file is the pre-registration time.

## Why a new test

The round 13 out-of-sample test (bbdcebe, audit section 16) trained on 7 seasons and scored 2021 and later.
Its gain was +0.29 $M a season (95% interval -0.35 to +1.31, SE 0.41). The smallest gain it could detect at
80% power is about 1.16 $M a season, larger than any plausible correction. Label: **inconclusive**, not failed.

## Design

1. **Data.** Every arbitration season with a salary on file: the seasons used in round 13 plus the new
   arbitration seasons from the 344-player BRef pull, after the valid-row rules A1 to A5 and B (d4be855).
   Target: 200 or more seasons. If fewer than 150 pass the rules, stop and report the count; no estimate.
2. **Split.** Leave one player out: each player's seasons are scored by a correction fit on every other player.
   No season is ever scored by a fit that saw it.
3. **Candidates (fixed now).** (a) current estimate, unchanged; (b) flat dollar offset by arbitration year
   (first, second, third and later); (c) percent offset by arbitration year. No other forms, no tuning after
   the run.
4. **Score.** Absolute error against the salary actually paid, per season, in $M. Gain = error of (a) minus
   error of the candidate, averaged over seasons, with a player-clustered bootstrap (2,000 draws, seed 20261128).
5. **Adopt rule.** A candidate is adopted only if its 95% interval excludes 0 and its mean gain is at least
   $0.25M a season. If both pass, take the larger mean gain. Target SE 0.10 $M or less; if the SE comes out
   above 0.15, report "still underpowered" and adopt nothing.
6. **Grades.** If a candidate is adopted, report the shadow first (sides moving a win or more, flips, clubs
   moving 2+ places). Live grades change only with Sean's OK.

## Not allowed after this commit

Changing the valid-row rules, the candidate list, the seed, the thresholds or dropping seasons by hand.
