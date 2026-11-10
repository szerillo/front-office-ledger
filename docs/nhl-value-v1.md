# NHL value stat, second cut (v1): what the shift-level data did and did not fix

Built Nov 10 2026 (night). Follows `nhl-value-v0.md`. Nothing here is on the site. Scripts in `engine/nhl/`:
`pbp_fetch.py`, `shots.py`, `xg.py`, `goalies.py`, `stints.py`, `rapm.py`, `rapm_tune.py`, `value1.py`,
`write_v1.py`.

## Short version
The shift-level work was meant to fix defensemen and goalies. It fixed neither. It did make the stat
slightly better at predicting clubs, so v1 keeps a half-weight version of it. The honest reading is that
most of a defenseman's defensive value, and most of a goalie's season, cannot be told apart from noise and
club with public data, and the edition should be built knowing that.

## What was built
- **Shot table.** 2.19 million shot attempts, 2010-11 to 2025-26, each with location, shot type, strength,
  score, and what happened just before.
- **Expected goals.** The chance that an unblocked attempt scores, fitted so that every season is scored by
  a model that never saw it. It separates goals from non-goals well (0.773 on the usual 0.5 to 1 scale;
  distance alone gets 0.70) and is calibrated in every tenth of shots (for example 0.230 expected against
  0.232 scored in the most dangerous tenth). Season totals run within 6% of actual.
- **Five-on-five stints.** Every stretch with the same ten skaters on the ice: about 5 million stints,
  roughly 1,000 hours a season.
- **Shift-level skater model.** Each skater's effect on expected goals for and against per hour with the
  other nine held fixed, one season at a time.

## What the tests said
**Goalies.** Goals saved above expected repeats no better than plain save percentage: 0.17 year to year
against 0.19 (329 pairs of 1,000-shot seasons). For the 33 goalies who changed clubs it is below zero
either way. Two goalies on the same club in the same season still move together (0.18), so shot location
does not remove the club's effect. Goalies stay at 70% credit on plain saves.

**Skaters, the shift-level effects alone.** They are real but small. For players who changed clubs the
offensive effect carries to the next year at 0.41 and the defensive effect at 0.33; for defensemen's
defense, 0.47 year to year. The spread is narrow: one standard deviation is about 0.065 expected goals
per hour on offense and 0.05 on defense, which is roughly one goal over a full season.

**As a replacement for v0's five-on-five parts** (2010-11 on, same tests as v0):

| Version | Repeats, F / D | Follows a player to a new club | Clubs next year (standings alone: 0.552) | Defensemen's share |
|---|---|---|---|---|
| v0 | 0.66 / 0.61 | 0.54 | 0.567 | 14% |
| Shift-level effects in place of v0's scoring and shot share | 0.47 / 0.41 | 0.27 | 0.557 | 14% |
| Half scoring, half shift-level | 0.57 / 0.51 | 0.38 | 0.580 | 14% |
| **v1: v0 plus half of the shift-level effects** | **0.67 / 0.60** | **0.54** | **0.595** | **14%** |

So v1 is v0 with half of each skater's shift-level effect added. It tracks v0 at 0.996 across skater
seasons; the largest changes are about 0.6 wins in a season (up: Ekholm, Vlasic, Bouchard, Matthews; down:
Lindell, Leddy).

**Defensemen.** Their share of the wins did not move in any version. The shift-level model says the gap
between a good and a poor defender, as far as shot location data can see it, is about a goal a season.
Either defensemen are closer to interchangeable than they are paid, or what separates them is not in
this data. This build cannot tell which.

## What this means for the edition
- Grade forwards on v1 with normal confidence.
- Grade defensemen against other defensemen only (the draft channel already does this), and say so on
  the page.
- Grade goalies over several seasons at a time, never one, and expect wide bands.
- The draft channel run on v1 is unchanged for practical purposes: pick-by-pick results track v0 at 0.998,
  general managers at 0.996.

## Not done
- No adjustment for score, zone starts or back-to-backs in the shift-level model.
- Special teams still come from season lines.
- Before 2010-11 there is only v0.
- Player tracking data, which is where defensive value would show if it shows anywhere, is not public.
