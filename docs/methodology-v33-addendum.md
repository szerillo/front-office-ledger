# Methodology v3.3 addendum (Nov 11, 2026)

Four rules Sean set on Nov 11. Each says what the engine does and what a reader sees.

## 1. Rounding of winter dollar totals: half to even

A winter's dollar total is rounded to whole millions with round half to even ("banker's rounding"): a total that
sits exactly on .5 goes to the nearest even million ($15.5M shows as $16M, $14.5M as $14M). This is Python's
`round()` and is what the published winter table already does: 132 cells sit exactly on .5, and all of them already
follow this rule. Sums are taken with `math.fsum` in a fixed order, so float noise cannot push a total off .5
(STL 2004-05, faM 15.5, now reads $16M in every build).

## 2. The 2020 season: charge prorated to 60 of 162 games, group rates held

2020 was a 60-game season. Pay was prorated, and so was the value a player could produce. The engine now charges a
2020 season at 60/162 of the contract's yearly cost (free-agent signings: `fa_grade.py`; extensions: `ext_grade.py`).

The yardsticks are not recomputed with the prorated charge. The free-agent "typical return" by contract year comes
from `contract_book.py` as before, and the extension class rates are computed from the unprorated charge exactly
as shipped (`ext_class_rate.json` is byte-identical before and after). So only deals that cover 2020 move; no other
player's grade moves because of this rule.

## 3. Placeholder salary rows below the league minimum (filler rule)

A salary row below that season's major-league minimum is a placeholder, not a salary. If every row for a season is
below the minimum, the season is charged the minimum when the player had a major-league stint that season, and
carries no salary when he did not. Sourced corrections still win. This applies wherever outside salary tables are
read (today the $0-season and arbitration checks; no published grade reads these rows yet).

## 4. Signing bonuses: spread over the guaranteed years

A signing bonus counts as part of the guarantee and is spread evenly over the guaranteed contract years, the
average-annual-value convention Cot's Contracts uses. Every contract row carries its average annual value as total
over guaranteed years (3,609 of 3,609), and a free-agent signing is charged that figure each season, so a bonus in
the reported total is already spread evenly. Extensions are charged on the rising salary schedule (v5.9) applied to
the whole total, bonus included. The contract book has no separate bonus field, so a bonus cannot yet be pulled out
of an extension's schedule or out of a per-season salary table that pays it in one year; those rows are listed as
open until a bonus field is sourced.
