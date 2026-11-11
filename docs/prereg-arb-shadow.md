# Pre-registration: arbitration salaries in trade grades (shadow only)

Written 2026-11-11 before the run. Nothing here is deployed.

**Question.** The engine prices arbitration seasons with no contract on file using its award model
(`asset_rules.arb_salary`). How much do trade grades move if those seasons carry what players were actually
paid?

**Population.** Every acquired player-season in a trade window that the model prices (3,919 seasons on 2,007
trade sides, Nov 11 count).

**Two runs.**
1. Real salaries where we have them (Baseball-Reference rows pulled Nov 11, the 2026 arbitration figures in
   `arb_calib.py`); everything else unchanged. Report coverage.
2. Sensitivity for the rest: each priced season's salary is multiplied by a ratio drawn from the observed
   actual / model ratios in the 83 held-out seasons, binned by the model's predicted salary (thirds), 500
   draws. Report the median and the 5th to 95th percentile of each count.

**Counts reported.** Trade sides whose net moves by 1.0 win or more; sides whose net flips sign (only sides
with |net| of 0.5 or more before); changes to the top 25 trade sides by net (league-wide, both ends); clubs
whose all-time trade-total rank changes.

**Material if any of these holds (median of run 2, or run 1 alone):**
- 42 or more trade sides (1% of 4,172 trades' sides counted once per trade) move by 1.0 win or more;
- any side enters or leaves the league-wide top 25 or bottom 25;
- any club's all-time trade-total rank changes by 2 or more places;
- 10 or more sides with |net| of 0.5 or more flip sign.
Below all four: report as immaterial and leave the model in place until the service-time fix.
