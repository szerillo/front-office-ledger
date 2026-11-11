# Accuracy audit, Nov 11 2026

## 1. Forty random graded moves against primary sources

Sample: 16 trades, 14 free-agent signings, 10 extensions (seeded random draw from the card data; 12 dated
2023 to 2025). Sources: the league transaction feed (statsapi, every player in every deal), club and
league announcements and named reporters for contract terms (MLB.com, MLB Trade Rumors, ESPN, The
Athletic, AP), FanGraphs season WAR by club for production (pulled same-origin in Chrome).

| Field | Checked | Wrong | Rate | What was wrong |
|---|---|---|---|---|
| Players in the move | 40 | 0 | 0% | |
| Date | 40 | 0 | 0% | Trades and signings match the feed to the day. Extensions are stored by month and the site shows the month. |
| Contract terms (years, dollars, type) | 24 | 1 | 4% | Josh Donaldson 2016 (2 yr / $28.65M) is labelled a veteran deal; it bought two arbitration years only. |
| Value credited to each side | 40 | 2 | 5% | Donaldson: his 2017 arbitration season is booked as a bought-out free-agent season. Otto Lopez (TOR to SF for cash): the -7.5 is what he did for Miami after San Francisco lost him on waivers, but the page said "realized on San Francisco Giants". |
| OPEN / CLOSED | 40 | 2 | 5% | Houser to TB (2025) read CLOSED although all three pieces were flipped and still play; the trade's number follows them. Lopez read CLOSED although his window still runs. |
| **All fields** | **184** | **5** | **2.7%** | 3 of 40 moves had at least one error (7.5%). |

Production check: of the player windows I could line up against FanGraphs WAR for the same club and
seasons, all but four sit within a win (or 25%) of it. The four (Taillon, Altuve, Schoop, Ahmed) are
gaps between Ledger WAR and fWAR (pitcher runs vs FIP, defense source), not booking errors.

### Fixes and pattern searches
- **Trade OPEN/CLOSED follows the player, not the club.** A trade's number follows each piece wherever
  he plays until his window ends, so a trade is now OPEN while any piece is still in the league and not a
  free agent or retired. 15 trades reopened, nothing before 2021 touched.
- **"Value realized on" label.** Every trade card now says the giving side's number is his value after the
  trade wherever he played, naming the club he went to first. All trade cards, one rule.
- **Super Two control (not fixed).** Pattern search on the Donaldson error: extensions marked veteran with
  one controlled season. Matt Olson (2022) is the second confirmed case: two arbitration years, one counted.
  The fix is in the engine's control-end rule and needs a full rebuild (ledger.sqlite). See decisions.
- **Duplicate trade nodes on player trees.** Found while checking dates: the league feed files some trades
  a day off the book's date, and 31 player trees showed the same deal twice (Donaldson, Urshela, Sanchez
  2022). Fixed: one deal, one node.

## 2. Edge cases

| Case | How it grades today | Verdict |
|---|---|---|
| Player to be named later | Graded once the player is named (Megill to MIL, Taylor Floyd named in June 2023). | Right |
| Cash considerations | Cash counts as zero on both sides (Otto Lopez, Kevin Kelly). | Right by method; small cash sums ignored |
| Three-team trades | 79 deals; each club's number is what it got minus what it gave. 77 add to zero. | 2 wrong: Bedard 2011 (Josh Fields leg missing) and the two Arizona deals of Nov 28 2003 (the second seat showed the first deal's number) |
| Rule 5 pick passed to another club | The trade seat picked up the club's Rule 5 grade instead of the trade's number: Jordan Romano 2018 showed the White Sox +3.6 for giving him away. 8 deals. | Wrong, fixed |
| Two-club deals with a missing piece on one side | Greinke to LAA 2012 (Segura, Pena, Hellweg), Gerut for Gwynn Jr. 2009: the giving side did not list what the other side got. | Wrong, fixed by completing the giving side from the receiving side |
| Opt-outs | Graded on the seasons played and paid (Alonso and Diaz, both out after 2025). Imai stayed in for 2027 and stays OPEN. | Right |
| Released players still being paid | The salary keeps counting as cost after the release (Avisail Garcia, Miami). | Right |
| Traded twice in one season | The first trade keeps the player's value through the flip; the flip charges it back (Uribe 2015, Arroyo 2015). | Right by method |
| Receiving club loses the player on waivers | The original sender keeps being charged for everything he does later (Lopez: -7.5 for Toronto for a player it had designated for assignment). | Method question for Sean |

## 3. How a grade is computed (for readers)

Every move is graded on what it actually produced for the club, against what a typical club gets from
the same kind of move. For a trade, each player a club receives counts his Ledger WAR (our wins measure,
with park, defense and a reliever leverage adjustment) from the trade to the end of his control window,
wherever he plays it, minus the salary the club took on, with each later season discounted 10%; the
club's number is what it got minus what it gave, so the two sides of a deal add to zero. A prospect who
has not finished his window also carries the value still expected from his ranking. For a free-agent
signing, it is his Ledger WAR for the club in the seasons played minus what a typical signing at that
price returns, plus a pick charge when he turned down a qualifying offer; salary paid after a release or
trade still counts. For an extension, the arbitration seasons are graded against what arbitration would
have cost and the bought-out free-agent seasons against the typical free-agent return. Letters rank a
move against moves of its own type. A move is OPEN while anyone in it can still change the number.

### The five grades a knowledgeable fan would call wrong

| Grade | Why it looks wrong | At fault |
|---|---|---|
| Crochet trade: White Sox +11.9, Red Sox -11.9 | Boston got an ace. Its number is one season, because his extension owns 2026 on; Chicago's +15.6 in is mostly the value still expected from Teel, Meidroth and Montgomery. | Method: prospect value counts before it is played (same call as open decision 2) |
| Mookie Betts trade: Dodgers -5.5 | The deal that brought Betts to LA reads as a loss. The trade is graded on 2020 only; his extension (+18.8) is its own decision. | Method: control years only. The career card and tree now say so on the trade line |
| Otto Lopez for cash: Blue Jays -7.5 | Toronto had designated him; the Giants lost him on waivers and Miami got the value. | Method (waiver loss) plus a label error, fixed |
| Jordan Romano Rule 5 pass: White Sox +3.6 | A club cannot win by handing away a Rule 5 pick. | Code: wrong decision used for the trade seat, fixed |
| Josh Donaldson 2016 extension graded as buying free-agent years | It bought two arbitration years. | Data: Super Two control ends a year early in the engine; Olson 2022 too |

## 4. Scheduled refreshes
At 10:20 UTC Nov 11 the new 8:03 and 8:17 AM ET runs had not fired yet (first fire 13:03 UTC). The two
runs on the old schedule (02:37 and 03:23 UTC) stamped nothing, and the hub's own note at 03:53 UTC says
Chrome could not be reached. The jobs can only commit through Sean's Chrome, so any run while the laptop
sleeps does nothing. A check is scheduled for 13:40 UTC.

## 5. Go / no-go for the first link

Green
- Players, dates and contract terms: 0 to 4% error in the sample, and the errors found are fixed or listed.
- OPEN/CLOSED from facts; trades follow flipped pieces.
- Link previews: tags and images on home and move pages return 200.
- No em dashes; 13 test suites pass on the live site.
- Both data files stamped Nov 11 by a real run.

Red
- Prospect value in open trades (Crochet, Holmes and Taylor): the most visible risk; waits on decision 2.
- Scheduled refreshes unproven; they fail silently whenever the laptop sleeps.
- Two Super Two extension grades (Donaldson 2016, Olson 2022) are wrong until an engine rebuild.
- The X card itself is unconfirmed until a real post.

Amber
- Phone load 8.2 s on slow 4G.
- NHL numbers stay off X until the pick ties are fixed.
