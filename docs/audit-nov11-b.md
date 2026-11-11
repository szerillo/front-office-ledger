# Accuracy audit, part 2 (Nov 11 2026)

Follows `audit-nov11.md`. Everything here can be re-run from the repo: `tests/tools/audit_sample.mjs`,
`tests/tools/audit_hi20.mjs`, `tests/tools/control_end_check.py`.

## 1. Was the sample random?

Not simply random. Method: every graded decision row in `cards.js` (1,306 rows; trades, signings and
extensions with a number: 729), de-duplicated by club, date and headline, then a seeded draw (linear
congruential generator, seed 20261111, `tests/tools/audit_sample.mjs`) stratified by type and era: 6 trades
from 2023-25 and 10 from other years, 4 and 10 signings, 2 and 8 extensions.

Two limits, both stated plainly:
- **Frame.** `cards.js` holds each card's best and worst lists, not every graded move (the trade book alone has
  4,172 deals). The frame over-weights extreme grades, which are also the ones readers see first.
- **Era mix.** In the frame, 2023-25 is 42.5% of graded rows (trades 40.7%, signings 47.8%, extensions 32.0%).
  The sample had 12 of 40 (30%), so recent moves were under-weighted. Part 2's 20 moves are all 2024-26 to
  correct for it.

The 40 moves:

| # | Type | Card | Date | Move | MLBAM ids |
|---|---|---|---|---|---|
| 0 | trade | cws | 2025-07-31 | Chicago White Sox traded RHP Adrian Houser to Tampa Bay Rays for 1B Curtis Me... | 701474,678554,687239,605288 |
| 1 | trade | tor | 2024-02-13 | Toronto Blue Jays traded SS Otto Lopez to San Francisco Giants for cash. | 672640 |
| 2 | trade | lad | 2023-01-11 | Miami Marlins traded SS Miguel Rojas to Los Angeles Dodgers for SS Jacob Amaya. | 500743,676070 |
| 3 | trade | nym | 2024-07-30 | Miami Marlins traded RHP Huascar Brazoban to New York Mets for SS Wilfredo Lara. | 623211,702906 |
| 4 | trade | min-derek-falvey | 2023-04-30 | The Minnesota Twins acquired Taylor Floyd for Trevor Megill. | 687905,656730 |
| 5 | trade | mia | 2024-07-30 | Miami Marlins traded LHP Tanner Scott and RHP Bryan Hoeing to San Diego Padre... | 800049,688363,702281,810891,663773,656945 |
| 6 | trade | mil-david-stearns | 2021-07-30 | Detroit Tigers traded LHP Daniel Norris to Milwaukee Brewers for RHP Reese Ol... | 596057,681857 |
| 7 | trade | mia-kim-ng | 2022-04-03 | Baltimore Orioles traded RHP Cole Sulser and LHP Tanner Scott to Miami Marlin... | 642121,656945,698931,669163 |
| 8 | trade | min-derek-falvey | 2021-07-22 | Tampa Bay Rays traded RHP Drew Strotman and RHP Joe Ryan to Minnesota Twins f... | 675977,657746,676534,443558 |
| 9 | trade | min-derek-falvey | 2022-03-13 | Cincinnati Reds traded RHP Sonny Gray and RHP Francis Peguero to Minnesota Tw... | 543243,677868,695534 |
| 10 | trade | laa | 2026-08-03 | Los Angeles Angels traded RHP José Soriano to Toronto Blue Jays for SS Arjun ... | 821022,804446,805796,667755 |
| 11 | trade | col-bill-schmidt | 2022-12-08 | Colorado Rockies traded RHP Kevin Kelly to Tampa Bay Rays for cash. | 687330 |
| 12 | trade | col | 2026-07-20 | Colorado Rockies traded RHP Seth Halvorsen to Los Angeles Dodgers for RHP Nic... | 693308,811716,678020 |
| 13 | trade | sea | 2017-07-20 | Miami Marlins traded RHP David Phelps to Seattle Mariners for RHP Brandon Mil... | 475479,641154,621165,669732,659910 |
| 14 | trade | nyy | 2014-12-05 | Three-team trade: the New York Yankees acquired Didi Gregorius for Shane Greene. | 544369,572888 |
| 15 | trade | atl | 2022-12-12 | The Atlanta Braves acquired Sean Murphy for William Contreras, Justin Yeager,... | 669221,661388,666205,687866,683690,676206,444489 |
| 16 | fa | sf | 2025-01-11 | Signed Justin Verlander · 1 yr / $15.0M (2024-25 winter) | 434378 |
| 17 | fa | det | 2024-12-10 | Signed Alex Cobb · 1 yr / $15.0M (2024-25 winter) | 502171 |
| 18 | fa | ari | 2024-02-17 | Signed Randal Grichuk · 1 yr / $2.0M (2023-24 winter) | 545341 |
| 19 | fa | pit | 2024-02-14 | Signed Yasmani Grandal · 1 yr / $2.5M (2023-24 winter) | 518735 |
| 20 | fa | wsh-mike-rizzo | 2022-11-29 | Signed Jeimer Candelario · 1 yr / $5.0M (2022-23 winter) | 600869 |
| 21 | fa | hou-dana-brown | 2026-01-02 | Signed Tatsuya Imai · 3 yr / $54.0M (2025-26 winter) | 837227 |
| 22 | fa | nym-billy-eppler | 2021-12-01 | Signed Max Scherzer · 3 yr / $130.0M (2021-22 winter) | 453286 |
| 23 | fa | mia-kim-ng | 2021-12-01 | Signed Avisaíl García · 4 yr / $53.0M (2021-22 winter) | 541645 |
| 24 | fa | bos-chaim-bloom | 2021-02-02 | Signed Enrique Hernández · 2 yr / $14.0M (2020-21 winter) | 571771 |
| 25 | fa | chc | 2022-12-19 | Signed Jameson Taillon · 4 yr / $68.0M (2022-23 winter) | 592791 |
| 26 | fa | atl | 2019-12-04 | Signed Cole Hamels · 1 yr / $18.0M (2019-20 winter) | 430935 |
| 27 | fa | cle | 2013-01-04 | Signed Brett Myers · 1 yr / $7.0M (2012-13 winter) | 408206 |
| 28 | fa | sd | 2016-12-20 | Signed Jhoulys Chacín · 1 yr / $1.8M (2016-17 winter) | 468504 |
| 29 | fa | phi | 2022-12-09 | Signed Matt Strahm · 2 yr / $15.0M (2022-23 winter) | 621381 |
| 30 | ext | hou-dana-brown | 2024-02-15 | Extended Jose Altuve · 5 yr / $125.0M (veteran) | 514888 |
| 31 | ext | ath-david-forst | 2025-01-15 | Extended Brent Rooker · 5 yr / $60.0M (arb) | 667670 |
| 32 | ext | tor | 2016-02-15 | Extended Josh Donaldson · 2 yr / $28.6M (veteran) | 518626 |
| 33 | ext | mia-kim-ng | 2022-03-15 | Extended Richard Bleier · 2 yr / $6.0M (veteran) | 542947 |
| 34 | ext | laa-perry-minasian | 2021-04-15 | Extended David Fletcher · 5 yr / $26.0M (arb) | 664058 |
| 35 | ext | sd | 2022-07-15 | Extended Joe Musgrove · 5 yr / $100.0M (veteran) | 605397 |
| 36 | ext | nyy | 2014-02-15 | Extended Brett Gardner · 4 yr / $52.0M (veteran) | 458731 |
| 37 | ext | ari | 2020-02-15 | Extended Nick Ahmed · 4 yr / $32.5M (veteran) | 605113 |
| 38 | ext | det-al-avila | 2021-08-15 | Extended Jonathan Schoop · 2 yr / $15.0M (veteran) | 570731 |
| 39 | ext | hou-james-click | 2022-04-15 | Extended Ryan Pressly · 2 yr / $30.0M (veteran) | 519151 |

## 2. Extrapolation and 20 more high-traffic moves

Part 1: 3 of 40 moves had at least one wrong field. As a rate per move: 7.5%, 90% interval 2.1% to 18.3%
(exact binomial). Over the 729 graded trade, signing and extension rows on the cards that is about 55 rows
(15 to 133). A card shows about 4.8 such rows, so at that rate about 31% of the 152 cards (10% to 62%, or
15 to 94 cards) carry at least one wrong field. Two of the three were OPEN/CLOSED errors fixed the same day;
on what was left (1 of 40, 2.5%, interval 0.1% to 11.3%) it is about 11% of cards (1% to 44%).

The interval is wide because the sample is small, and the errors were not independent coin flips: each
came from a rule that touches many moves at once. Counting the rules (below) is the better measure.

**20 more, chosen for traffic** (2024-26, the 12 biggest contracts and the 8 biggest trade swings on the cards):

| # | Type | Card | Date | Move | MLBAM ids |
|---|---|---|---|---|---|
| 0 | fa | nym | 2024-12-11 | Signed Juan Soto · 15 yr / $765.0M (2024-25 winter, QO signing, draft comp ch... | 665742 |
| 1 | ext | tor | 2025-04-15 | Extended Vladimir Guerrero Jr. · 14 yr / $500.0M (veteran) | 665489 |
| 2 | ext | kc | 2024-02-15 | Extended Bobby Witt Jr. · 11 yr / $288.7M (early) | 677951 |
| 3 | fa | lad | 2026-01-21 | Signed Kyle Tucker · 4 yr / $240.0M (2025-26 winter, QO signing, draft comp c... | 663656 |
| 4 | fa | ari | 2024-12-30 | Signed Corbin Burnes · 6 yr / $210.0M (2024-25 winter, QO signing, draft comp... | 669203 |
| 5 | fa | lad | 2024-11-30 | Signed Blake Snell · 5 yr / $182.0M (2024-25 winter) | 605483 |
| 6 | fa | sf | 2024-12-10 | Signed Willy Adames · 7 yr / $182.0M (2024-25 winter, QO signing, draft comp ... | 642715 |
| 7 | fa | chc | 2026-01-14 | Signed Alex Bregman · 5 yr / $175.0M (2025-26 winter) | 608324 |
| 8 | fa | bal | 2025-12-11 | Signed Pete Alonso · 5 yr / $155.0M (2025-26 winter) | 624413 |
| 9 | ext | sf-farhan-zaidi | 2024-09-15 | Extended Matt Chapman · 6 yr / $151.0M (veteran) | 656305 |
| 10 | ext | det | 2026-04-15 | Extended Kevin McGonigle · 8 yr / $150.0M (early) | 805808 |
| 11 | ext | chc | 2026-03-15 | Extended Nico Hoerner · 6 yr / $141.0M (veteran) · no seasons elapsed, OPEN |  |
| 12 | trade | bos | 2024-12-11 | Chicago White Sox traded LHP Garrett Crochet to Boston Red Sox for C Kyle Tee... | 676979,805367,682790,695731,691019 |
| 13 | trade | pit | 2025-12-19 | The Pittsburgh Pirates acquired Brandon Lowe, Mason Montgomery and Jake Mangu... | 664040,663968,682254,681347 |
| 14 | trade | tb | 2025-12-19 | The Tampa Bay Rays acquired Anderson Brito and Jacob Melton for Brandon Lowe,... | 820901,689200,682254,664040,663968 |
| 15 | trade | chc | 2024-01-11 | Los Angeles Dodgers traded 2B Michael Busch and RHP Yency Almonte to Chicago ... | 683737,622075,814307,701328 |
| 16 | trade | sea | 2024-07-26 | The Seattle Mariners acquired Randy Arozarena for Aidan Smith, Ty Cummings an... | 668227,811315,806223,807744 |
| 17 | trade | chc | 2024-12-13 | Houston Astros traded RF Kyle Tucker to Chicago Cubs for 3B Isaac Paredes, RH... | 663656,701358,669713,670623 |
| 18 | trade | bal | 2024-02-01 | Milwaukee Brewers traded RHP Corbin Burnes to Baltimore Orioles for SS Joey O... | 669203,669084,687401 |
| 19 | trade | cws | 2024-07-29 | Los Angeles Dodgers traded 3B Miguel Vargas, SS Alexander Albertus and SS Jer... | 800316,800419,678246,502054,656629,607200 |

| Field | Checked | Wrong | What |
|---|---|---|---|
| Players | 20 | 0 | |
| Date | 20 | 0 | all seven trades match the league feed to the day |
| Contract terms | 12 | 0 | Tucker 4/$240M, Bregman 5/$175M, Alonso 5/$155M, McGonigle 8/$150M, Hoerner 6/$141M and the rest match named-source reports |
| Value credited | 20 | 2 | Brandon Lowe (Pirates +9.4) and Kyle Tucker (Cubs, 2025): the season's salary was not charged (see section 7) |
| OPEN/CLOSED | 20 | 1 | Nico Hoerner's extension read CLOSED because none of its seasons had started; fixed live |
| **All** | **92** | **3** | 3.3%; 3 of 20 moves |

## 3. Super Two, counted

The engine sets the end of club control at six seasons from the debut season. It does not read service
time, so options, late call-ups and Super Two all move the true end. Using the service-time table already
in the repo (`data/service.json`, 1,918 recent players, with Super Two marked by four arbitration winters):

- 826 extension grades in total; 164 have service data; 36 of those involve a Super Two player.
- **30 of the 164 (18%) have the wrong control end on seasons the deal covers**, Super Two or not.
  At that rate roughly 150 of the 826 may be affected; the other 662 need historical service time to check.
- The engine's own grade is reproduced exactly by `control_end_check.py` (Olson 12.01, deGrom -3.96,
  Polanco 8.67 all match), so an override table is mechanical for the 30. It is not the whole fix: the
  same control end also sets which seasons a trade owns and what salary it is charged (section 7).

Biggest changes: Matt Olson 12.0 to 3.8, Jorge Polanco 8.7 to 1.3, Jacob deGrom -4.0 to -8.4, Yandy Diaz
6.4 to 2.0, Jesus Luzardo 2.1 to -1.8, Chris Taylor 2.4 to -0.7, Byron Buxton 7.8 to 4.9. Full list in the
script output.

**Olson, worked by hand** (8 yr / $168M, Mar 2022; engine control end 2022, true end 2023):

| Season | Engine (control ends 2022) | Corrected (control ends 2023) |
|---|---|---|
| 2022 | controlled: arbitration path $17.9M (final year) minus extension pay = -0.03 | controlled: arbitration path $8.7M (second year) minus extension pay = -0.95 |
| 2023 | free agent: 8.14 Ledger WAR minus 2.29 wins of pay x 0.87 = +6.14 | controlled: arbitration path $15.4M minus extension pay = -0.56 |
| 2024 | 3.86 - 2.22 x 0.66 = +2.40 | 3.86 - 2.22 x 0.87 = +1.92 |
| 2025 | 5.87 - 2.17 x 0.59 = +4.58 | 5.87 - 2.17 x 0.66 = +4.44 |
| 2026 | 4.19 - 2.13 x 0.58 = +2.95 | 4.19 - 2.13 x 0.59 = +2.93 |
| Sum, minus the veteran-class expectation 4.02 | 16.04 - 4.02 = **+12.0** | 7.78 - 4.02 = **+3.8** |

The 8 wins do not vanish: Olson's 2023 belongs to the trade that brought him from Oakland, so Atlanta's
trade grade should rise by about that much.

## 4. Prospect value in open trades

765 trades since 2019 carry projected value (the engine's open-expectation term) inside their number.
Of the 806 seats with a net of half a win or more, the median is 26% projected and 231 seats (29%) are
more than half projected; some are more than 100% (the played part is negative). Largest: Crochet (White
Sox +11.9, of which +7.2 projected), the Athletics-Padres deal of July 31 2025 (+2.5 total, +5.9 projected).

Mock of a played / projected split, not shipped: `docs/mock-split.html` (screenshot `docs/mock-split.png`).
On Crochet it reads +4.7 played, +7.2 projected. On Holmes and Taylor it reads Cubs +1.0 played, -2.7
projected. The letter would rank on the played part only, which removes the wording contradiction
without changing the method.

## 5. Phone load, profiled

Live site, iPhone viewport, slow 4G (1.6 Mbps, 150 ms) and 4x CPU slowdown: first paint 1.2 s, page
parsed 8.5 s, home content 9.1 s, network quiet 17.5 s. 19 requests, 3.0 MB over the wire.

| Asset | Over the wire | Time |
|---|---|---|
| `index.html` | 1,082 KB (gzip) | 6.4 s |
| `cards.js` | 915 KB | 8.6 s |
| `moves.js` | 524 KB | 6.8 s |

Inside `index.html`, one inline table, `DESK`, is 41% of the file (437 KB of the 1,051 KB gzip). Two of its
parts, `deals` (469 KB raw) and `peak` (385 KB raw), serve only the Deal Desk and the Simulator.
**Cheapest fix:** move `DESK.deals` and `DESK.peak` into a file fetched when those views open, the same
pattern as `book.js`. Estimated: about 250 KB less before the home page can draw, about 1.3 s on slow 4G.
`cards.js` and `moves.js` already load after the page and do not delay home content. A smaller one: the
display font loads as a 77 KB `.woff` where a `.woff2` exists.

## 6. The two pre-2012 bugs, and a grep for the pattern

- **Zero-sum check over all 4,172 deals.** After today's fixes, 2 deals still do not add to zero: Bedard
  (Jul 31 2011, Josh Fields leg and the Dodgers' players missing) and a one-sided 2009 Chris Burke record.
  Both are now held back on the player tree ("missing players on one side") instead of showing a number.
- **Same club twice in one record.** 29 records list one club in two legs: linked same-day deals stored
  together (Arizona, Nov 28 2003: Schilling to Boston, then De La Rosa on to Milwaukee with Sexson; also
  Minnesota and the Yankees in Mar 2022, Pittsburgh in Jul 2025). A player who passed through both legs
  was pulling one leg's card grade onto the other. Fixed: shared players no longer select a card grade,
  and Arizona's second leg now reads -15.6, matching Milwaukee's +15.6.
- **Same club, same day, separate deals.** 590 club-days have two or more separate trades. None share a
  player, so none can cross-wire; nothing to fix.

## 7. One more unverified assumption, tested

Assumption: a trade charges the acquiring club the salary it actually paid in every season of the window.
**False for one class of seasons.** Where a season falls after the engine's control end and the contract book
holds no contract for it (club options, arbitration years the engine thinks are free agency), the salary
charged is zero. Since 2015: 802 of 6,802 acquired player-seasons, touching 549 trade seats (corrected in
audit-nov11-c.md; this line first said 2,370 of 13,229 and 835 seats, a double count). Not all are
wrong (some are true minimum-salary seasons), but the largest are: Trea Turner 2022 (Dodgers, arbitration
$21M), Chris Sale 2018-19 (Red Sox, options $12.5M and $15M), Brandon Lowe 2026 (Pirates, option $11.5M),
Kyle Tucker 2025 (Cubs, arbitration $16.5M), Randy Arozarena 2026 (Mariners, arbitration). Same root cause
as section 3: control end from service time, plus option years in the contract book.

## 8. Go / no-go, updated

Green: players and dates (0 errors in 60 moves) and contract terms (1 label error in 36); OPEN/CLOSED; link preview tags; quarantined old
deals; all 13 suites pass live.

Red:
- Control end from debut year instead of service time: about 18% of covered extension grades and a share of
  trade salary charges are off (sections 3 and 7). This is the largest accuracy item left.
- Prospect value inside open trade numbers (Crochet), with a mock ready.
- Scheduled refreshes unproven (first new-schedule runs at 8:03 and 8:17 ET today).
- X card unconfirmed until a real post.

Amber: phone load (cheapest fix named above).
