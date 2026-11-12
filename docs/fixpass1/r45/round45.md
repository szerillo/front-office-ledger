# Round 45 (Nov 12): service-time diagnosis and retry, band-test methodology line, challenges

## 1. The three round 44 misses, day by day (counter v1, MLB Stats API transactions)
Cumulative service days per season against 1,032 (6.000 years).
- Ryan McMahon (truth: free agent after 2023; ESPN, Mar 2022). 2017 52, 2018 106, 2019-2023 172 each: 1,018, one season late.
  Lost stint: the feed has "assigned to Albuquerque Isotopes" on 2018-06-03 with no option. v1 took him off; he played
  12 MLB games Jun 3 to Jun 20 and was optioned Jun 21. 18 days lost. Real 2018: 124. Counting error, fixed in v2.
- Chris Archer: not a miss. Round 44 recorded "after 2018". MLB Trade Rumors (Apr 3, 2014): 156 days entering 2014 and
  under club control through 2019. v1 has 157 days (2012 35: Jun 20-27 and Sep 7-Oct 3; 2013 122 from Jun 1) and 2019.
  Our error in the round 44 lookup. One day over, no effect on the year.
- Matt Moore: unresolved. 2011 17 (Spotrac's 0.017 at his Dec 2011 signing matches), 2012-14 172 each, 2015 154,
  2016-17 172 each: 1,031, one day short of "after 2017". Lost stint: optioned Aug 3 to Aug 31, 2015 (29 days, over the
  20-day line). MLB.com: he left the club Aug 2, the option was filed Aug 3. The "after 2017" truth dates from Dec 2011,
  before that option. No published service figure after 2015 found (Spotrac's service column climbs one whole year per
  row, so it is not usable). Not tuned for.
- Not involved in any of the three: 2020 and 2022 adjustments, September callups.
Corrected round 44 tally: 5 of 7, still under its bar. Round 44 stays a fail.

## 2. Retry (prereg f508434, written before the draw)
v2 = v1 plus one change (a bare minor-league "assigned" record no longer removes an active player). Training players:
8 of 9 right under v2 (Moore the one).
Sample (seed 20261145, sample20_v2.json). Looked up in order until the bar could not be met:
| Player | Group | v2 | Truth | Source | |
|---|---|---|---|---|---|
| Luis Severino | optioned | 2021 | 2022 | AP/CBS Feb 2019: two days short of free agency after 2021 | MISS |
| Marco Gonzales | optioned | 2023 | 2023 | MLB Trade Rumors Feb 2020 | ok |
| Odúbel Herrera | random | 2031 | 2020 | MLB.com Dec 2016 | MISS |
| J.P. Crawford | late | 2024 | 2024 | AP Apr 2022 | ok |
| Aaron Bummer | late | 2024 | not used | only a reader comment found | |
Two misses: at most 18 of 20 is possible, so the bar (19 of 20) fails. Lookups stopped there.
Why: Severino's 2016 counts 163 days, but he was sent down several times that year (v2 over-counts by at least 2 days
overall). Herrera's feed gives no days for 2015-2018 at all (a Rule 5 pick; the feed or the classifier misses his
roster status), so he never reaches 6.000.
Result: FAIL. The pre-registered fallback applies (published service figures where they exist; old rule labelled
"estimated" everywhere else). Not built this round. No retuning of the counter.

## 3. Methodology line (deployed: 0ece84c index.html, dc1149d t_build re-pin)
Correction to the brief: the r42/r43 band tests did not assume independent seasons. They cycled each player's own
residual vector, so a player's error is fully shared across his seasons. Independent seasons was a reported-only
column. The line says so: the test is the cautious one; three winters fall just short of 0.90 under it (Texas 2010-11
0.844, San Diego 2014-15 0.847, Detroit 1998-99 0.879); with independent seasons ten winters would get a band.
Gates: index gate CLEAR (8 data files), 19/19 suites before, live md5 ee7e1df8 = staged, 19/19 after on a fresh clone at dc1149d.

## 4. Challenges
A. Control end one year later for everyone (dry run C1, engine copy f with control_span end +1, same cache):
trade-side nets shown to 0.1 that change 3,201 of 7,643 (largest 6.4); club-winter totals 653 of 816 (largest 7.1);
all 44 winter share pages; front office channel nets 512 of 820 (largest 18.2); channel letters 133 of 662 (replication
of live letters 654 of 662); front office and club pages with a changed letter 95 of 148. TOR 2012-13 -50.8 to -52.3,
rank 1 to 2 from the bottom (band rule would need a rerun). 20-best and 20-worst lists keep 17 of 20 each. WSH 2014-15
33.9 to 36.6 and stays first. Counted, not estimated.
B. Graded players inside club control during a graded decision: debut before 2009 (no transactions, counter cannot
reach them) 1,381 (in a trade 1,244, in an extension 261); debut 2009 or later 2,154.
C. Assumption in t_winter's named-report exception: a TRADE_RUMORS row is current and about the player's current club.
Rows carry no date and dkRumor() keys on player id only. Planted test t_winter_plant.mjs (live): Daylen Lile's report is
about Washington; moved to a non-rebuilding club with the row kept, dkRumor still returns it and availOk accepts him.
staleReportRejected FAIL, as expected. Fix proposal: add a report date and club to each row; accept a report only if its
club is the player's current club and it is dated after his last move.
