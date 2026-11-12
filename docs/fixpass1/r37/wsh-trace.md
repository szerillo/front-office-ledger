# WSH 2014-15 (+33.9), by hand from the raw rows

## What moved: one signing, only at the 2020-fix stage
Stage builds: live 32.8, data 32.8, fix pass 32.8, 2020 fix 33.9, re-sign 33.9, good7 33.9.
The winter: trades +21.9 (unchanged), free agents +10.9 to +12.0. The one row that moves is "Signed Max Scherzer,
7 yr / $210M": +11.1 to +12.2.

## The Scherzer row (fa_grade.py:126-160; contract_book.json)
Contract book: WSH, signed 2014-12, start 2015, 7 yr, $210M, AAV $30.0M, source espn, band 3.
Ledger WAR held by WSH: 2015 5.42, 2016 4.40, 2017 5.15, 2018 6.49, 2019 5.21, 2020 1.45, 2021 0.99 at share 0.5
(traded July 30). Realized = 29.11.
Cost per season = (AAV 30.0 - league minimum 0.75) / $ per win (2015 7.0, 2016 7.7, 2017 8.0, 2018 8.2, 2019 8.0,
2020 8.0, 2021 8.5) x share x season fraction. Expected = cost x typical return for that contract year
(1: 1.024, 2: 0.774, 3: 0.696, 4: 0.683, 5+: 0.474) x band 3 multiplier 1.034. QO signing: 1.0 win charged.
- 2020 charged in full: cost 3.656 wins, expected 1.792. Total expected 17.042. Value 29.11 - 17.04 - 1.0 = 11.07.
- 2020 charged 60/162 (fa_grade.py:18 SEASON_FRAC): cost 1.354, expected 0.664 (1.128 less). Total expected
  15.914. Value 29.11 - 15.91 - 1.0 = 12.20.
Matches the site to the decimal: +11.1 to +12.2, winter +32.8 to +33.9. The 2020 charge comes from the AAV, not
from the Baseball-Reference salary rows, so nothing is prorated twice.

## What would make +33.9 wrong (or move it)
1. Deferred money: the AAV is nominal ($30M); about $105M of the deal was deferred without interest, so the
   present-value cost is lower. Correcting it raises WSH; it cannot drop it below Oakland.
2. 2021 share 0.5: he was with Washington until July 30, about two thirds of the season. A day-based share adds about
   0.27 wins of expected cost: WSH about 33.6.
3. The flat 1.0-win QO charge and the typical-return curve are model choices; each moves this row directly.

## The No. 1 claim does not hold up, so it is out of the note and the posts
WSH passes Oakland 2011-12 only because Oakland also fell, 34.3 to 33.4, at the re-sign stage. The cause is one
piece: Ryan Sweeney, sent to Boston in the Reddick trade (2011-12-28). He elected free agency on 2012-11-30,
re-signed with Boston on a minor-league deal on 2013-01-25 (the re-sign rule keeps his window open), and Boston
released him on 2013-03-30, before Opening Day. asset_rules.py:362 ends a window in the year of a release
(`end = yy`) whatever the month, so his 2013 season with the Cubs (0.94 WAR) is credited to Boston. Boston's piece
goes 0.6 to 1.4 and Oakland's trade 9.4 to 8.5.
- The same pre-season-release credit exists on live for 50 trade pieces (19 with 0.5+ WAR); good7 adds 2, both
  Sweeney (also on Oakland's 2008 trade for him). spring.py lists them.
- With a release before April ending the prior season (as a free-agent signing already does,
  asset_rules.py:363), Oakland returns to about 34.2 and stays No. 1 by about 0.3.
So the flip is real on the site after the deploy, but it rests on a credit I think is wrong. Recommendation: say
nothing about No. 1 today, and pre-register the release-month rule as the first change after launch.
