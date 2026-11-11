# Pre-registration, round 12 (Nov 11)

Committed before any result of the 344-player Baseball-Reference pull (started 17:22:46 UTC) has been read, and
before the analyses below are run. The commit time on GitHub is the record of when.

## A. What counts as a valid salary row (applies to every row of the pull)
A Baseball-Reference salary row counts for (player, season) only if all hold:
1. Season: the row's year is a four-digit year equal to the season being priced.
2. Dollars: the salary cell parses to whole dollars after removing "$", commas and footnote marks ("*"); a
   blank or non-numeric cell is not a row.
3. Team: the row's club is one the player has a major-league stint with that season in the engine's
   player-season table (`asset_rules._lvm` rows), matched by full club name or alias in `regimes.json`.
   A row for a club he never played for that season is set aside and listed.
4. Not a minor-league or settlement amount: a row below that season's major-league minimum is not a salary
   (2020 counts against the prorated minimum). Such rows are listed, not charged.
5. Two valid rows for one season: the larger is used (a release then a re-sign, or split clubs), as before.
Rows failing 3 or 4 are reported with counts. The pull keeps the club name so rule 3 can be applied.

## B. The 11 players whose MLBAM redirect lands on a minor-league page
The pull follows the first `/players/x/....shtml` link on that page (it keeps the salary rows, not the page
title). A followed page counts only if, for every season in the $0 population, its salary row's club passes
rule A3 against that player's own stints; one failing season makes the whole page suspect and the player
uncovered (a wrong page would show another player's clubs). Then the hand check below. Five of the 11 with a valid page, drawn with seed 20261124 (LCG as audit_sample.mjs, over the 11
sorted by id), are hand-checked against Spotrac or Cot's for each season in the $0 population.

## C. Closures by the release / free-agency rule, all 147
Instead of a second sample, every one of the 147 is run through the failure found in round 11 (a release or
filing followed by a re-sign with the same club within 60 days, the player still active). Report the count.
Then a second seeded 15 (seed 20261123, excluding round 11's 15), checked against the league feed plus one
outside source where the feed shows the player re-signed or still active. Report errors / 30 with a 95%
Wilson interval.

## D. Arbitration bias: dollars, percent, and flips at the bound
For each third of the model's prediction: mean dollar error and percent error. Then rerun the arbitration
shadow with a fixed actual-to-model ratio per third, once at the point estimate and once at the end of each
third's 95% interval nearest zero (the least bias the data allow). Report sides moving a win or more and sign
flips (|net| of 0.5 or more) at both.

## E. One assumption in the $0-season rerun
Assumption: a Baseball-Reference salary row for a season is money the acquirer (or the club he was flipped to)
paid for playing that season. Buyouts and option declines can appear as their own season rows (Kittredge 2026:
$1.0M buyout listed, $9M actually paid by Baltimore). Test: five covered $0 seasons whose row looks like a
buyout or settlement (a row far below the season before, or a row in a season he left the club), drawn by
listing all such rows and taking the five largest; each checked against an outside source.
