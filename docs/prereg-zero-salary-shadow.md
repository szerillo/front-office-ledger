# Pre-registration: $0 seasons in trade grades, real salaries (shadow only)

Written 2026-11-11 at about 16:00 UTC (first version said 16:40 in error; the commit time, ddc7026, is the record), committed to the repo before the salaries are matched or any grade is
recomputed. The Baseball-Reference pull had started; no salary had been compared with a grade. Nothing here is
deployed.

**Question.** 802 acquired player-seasons in trades since 2015 sit after the engine's control end, have no
contract in the book, and are charged $0 (`tests/tools/zero_salary_sample.py`). A sample of 30 found 22 were
real salary seasons. How much do trade grades move if each of the 802 carries what the player was actually paid?

**Source.** Baseball-Reference salary tables for the 413 players, pulled Nov 11 in Chrome at one player every
9 seconds; saved to `tests/fixtures/zero_br_2026-11-11.txt`. A season with no salary row stays at $0 and is
counted as uncovered.

**Charge.** The engine's own: (salary minus the $0.75M floor, not below 0) times money_unit / dpw for that
season, discounted 0.9 a year from the trade, charged to the acquirer and mirrored to the giving side, exactly as
`tests/tools/arb_shadow.py` does. Nothing else changes.

**Counts reported.** Same four as the arbitration shadow (`docs/prereg-arb-shadow.md`): sides moving 1.0 win or
more; sign flips among sides with |net| of 0.5 or more; changes to the league top 25 or bottom 25; clubs whose
all-time trade rank moves 2 or more places. Plus coverage (seasons with a salary row) and the 25 largest movers.

**Material if any of these holds:**
- 42 or more trade sides move by 1.0 win or more;
- any side enters or leaves the league-wide top 25 or bottom 25;
- any club's all-time trade rank changes by 2 or more places;
- 10 or more sides with |net| of 0.5 or more flip sign.

**Also reported, combined.** The same counts with this change and run 1 of the arbitration shadow together,
since both replace a guessed charge with a paid salary.

**Hand check before any conclusion.** 10 seasons drawn with seed 20261120 from the covered set, salary compared
with a second source where one answers.
