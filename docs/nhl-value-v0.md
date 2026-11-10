# NHL value stat, first cut (v0)

Built Nov 10 2026. Step 1 of `nhl-plan.md`. Nothing here is on the site. Scripts are in `engine/nhl/`
(`fetch.py`, `assemble.py`, `value.py`, `test.py`, `movers.py`); the raw pull is not in the repo (116 MB,
re-creatable with `fetch.py` in about a minute).

## Data
The league's public stats service, regular seasons 1998-99 to 2025-26 (no 2004-05): 26,320 skater rows
(one per player, season and club, so a traded player has a row for each club), 2,641 goalie rows, 819 club
seasons. Ice time by situation exists for every season. On-ice shot attempts, on-ice goals and penalties
drawn start in 2009-10; before that the only on-ice number is plus-minus.

## What the stat is
Goals above a replacement player, converted to wins.
- **Scoring.** Each club's goals are shared among its skaters by goals plus half of assists, even strength
  and power play separately, then set against what an average forward or defenseman produces in the same
  minutes. Power-play minutes are judged against power-play rates, so a player is not paid for being handed
  the time.
- **Shot share (2009-10 on).** Shot attempts for and against at five on five with him on the ice, against
  the same club without him. A forward gets 15% of that difference on both ends; a defenseman gets 30% on the
  defensive end. Across the five skaters those shares hand out about the whole difference on defense, weighted toward
  defensemen, and three quarters of it on offense, where scoring is already counted.
- **Plus-minus (before 2009-10).** His plus-minus against the club's rate, at a weight of 0.1. It is noisy
  and the tests below wanted it small.
- **Penalties.** Drawn minus taken (taken only before 2009-10), against his position's rate, at what a
  minor was worth that season.
- **Goalies.** Saves above the league rate on the shots faced, at 70% credit; the rest is the club in front.
- **Replacement level.** Skaters outside a club's top 12 forwards and top 6 defensemen by ice time per game
  (10 games minimum), and goalies third or lower on a club in minutes. Forwards in that pool run about 0.26
  to 0.32 goals per 60 minutes below average, defensemen 0.08 to 0.09, goalies 7.4 goals per 1,000 shots.
- **Wins.** Goals per win come from the standings, three seasons at a time: 5.3 to 6.6 goals over the period.

An average club comes out 16.4 wins above replacement: 68% forwards, 14% defensemen, 18% goalies.

## Tests run
1. **Does it repeat?** Rate in one season against the next (600 minutes both years): forwards 0.59 before
   2009-10 and 0.66 after, defensemen 0.50 and 0.60. Goalies 0.19 (1,000 shots both years), which is what
   save percentage does.
2. **Does it follow a player to a new club?** This test changed the design.
   - Even-strength scoring: 0.59 for players who stayed, 0.47 to 0.52 for players who moved. It travels.
   - Shot share: 0.66 stayed and 0.54 moved on offense, 0.44 and 0.28 on defense. It travels.
   - Penalties: 0.48 to 0.70 stayed, 0.40 to 0.70 moved. It travels.
   - Power-play scoring: 0.29 to 0.34 stayed, 0.12 to 0.21 moved. Depends on the unit he lands on.
   - A share of the club's shot suppression, handed out by ice time: 0.58 to 0.69 stayed, **0.01 to 0.07
     moved**. That is the club, not the player, so it was taken out of the stat.
   - Goalies: 0.21 stayed, 0.01 moved (only 89 movers); two goalies on the same club in the same season
     correlate at 0.16. Part of a save percentage belongs to the club, hence the 70%.
3. **Do last year's values predict this year's clubs?** Each player's prior-year rate, pulled toward
   replacement when the sample is small, times this year's ice time, summed by club and set against the
   club's goal difference: 0.61 before 2009-10 and 0.56 after. Last year's club goal difference alone gives
   0.64 and 0.56. So the stat is about as good as knowing the club, no better. With the club's shot
   suppression left in it reaches 0.67 and 0.61, but that is credit the movers test says does not belong
   to players.
4. **Does it add up?** Summed by club it tracks goal difference at 0.89 and points at 0.77. It no longer
   adds up exactly, because club-level defense has no owner.

## Smell test
- 2023-24 forwards: MacKinnon 5.6, Kucherov 5.5, Matthews 5.4, McDavid 5.3, Panarin 5.2.
- 2023-24 defensemen: Q. Hughes 3.5, Makar 3.3, Bouchard 3.1, Fox 2.9, Josi 2.9.
- 2023-24 goalies: Hellebuyck 5.6, Demko 4.0, Binnington 3.9, Bobrovsky 3.8.
- Careers since 1998-99: Ovechkin 69, Crosby 68, McDavid 54; Karlsson 34, Lidstrom 29, Burns 28; Luongo 73,
  Lundqvist 55.

## What is wrong with it
- **Defensemen are squeezed.** Fourteen percent of the wins for 40% of the skater minutes. Their defensive
  work barely shows in season lines, so shutdown defensemen (Chara, Pronger, Doughty) sit far below
  scoring defensemen. Do not grade trades for defensemen on this version.
- **Goalies are mostly noise from one season to the next**, and there is no shot quality.
- **Before 2009-10 the stat is thinner**: no shot share and no penalties drawn.
- The weights on shot share were set by accounting (shares add to one player), not fitted; test 3 moves
  very little across reasonable weights, so it cannot pick them.
- No ages or aging yet. Birth dates and draft slots are pulled (4,723 players) and unused.

## Next
- **v1: the shift-level model.** The league publishes shift charts and play-by-play. With who was on the ice
  for every shot, each skater's effect can be estimated with teammates and opponents held fixed, which is
  the real fix for defensemen. Covers roughly 2010-11 on; a heavy pull.
- **Then the draft channel** (plan step 2), which only needs career value by pick: every pick since 1979 is
  in the official draft data, and forwards and goalies are usable now.
