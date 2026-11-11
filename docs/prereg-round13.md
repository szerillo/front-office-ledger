# Pre-registration, round 13 (Nov 11)

Committed before the runs below. Nothing here is deployed.

## A. Arbitration correction: dollars or percent, out of sample
Data: the 83 held-out arbitration seasons (`tests/fixtures/arb_br_2026-11-11.txt`, 28 players, 2018-2026, 2020
excluded). Train on seasons up to 2020 (in practice 2018-2019); judge on 2021 and later. Thirds are cut on the
model's prediction using the training seasons' cut points.
- Model P (percent): multiply the award model by the training third's sum(paid) / sum(model).
- Model D (dollars): add the training third's mean (paid - model), in $M, floored at the $0.75M minimum.
- Baseline: the current model.
Judged on the test seasons by median absolute error per season ($M); total percent error reported too.
D "beats" P only if its median absolute error is lower by $0.10M or more. If a training third has fewer than 8
seasons, the comparison is reported as underpowered and no claim is made either way.

## B. Salary rows that may not be pay for playing (buyouts, option years, bonuses)
Over every row in the two Baseball-Reference fixtures (`zero_br_2026-11-11.txt`, `arb_br_2026-11-11.txt`), count
rows matching any of:
1. Two or more rows for the same season (a release payment, a buyout or a split).
2. A row under 40% of the season before and above the minimum (a buyout or a reduced final year).
3. A row in a season the player has no major-league stint in the engine's player-season table.
4. A row whose amount equals a common buyout value ($0.25M, $0.5M, $0.75M, $1M, $1.5M, $2M) and is the last
   row of a run of higher rows.
Report each count, the overlap, and how many fall in priced $0-population seasons. Five of the largest flagged
rows inside the population are checked against an outside source.

## C. Does a Baseball-Reference page belong to the right person?
For every player in the two fixtures: the seasons with a salary row against the seasons he played in the majors
(`asset_rules._lvm`). A page is suspect if fewer than half of its salary seasons are seasons he played, or if its
first salary season is more than 3 years before his first played season. Suspects are listed and checked by
hand (birth year or debut on the page against the league feed).

## D. The re-sign rule (rule-checklist.md on the change to `folTradeOpen`)
Already run before this file: steps 1 to 3 (the rule, tests first, full count 710 to 721 OPEN, exactly the 11 of
the census) and step 4 (the release and re-sign events of the 8 players behind the 11, checked against MLB.com,
MiLB.com, MLB Trade Rumors, Wikipedia). Step 7 (all suites) was started before this commit and is reported as it
finishes.
