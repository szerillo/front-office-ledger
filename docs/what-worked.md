# What was tried and how it came out

One line per experiment or fix, newest first, so nothing gets tested twice. Details are in
`worklog.md` and the linked write-ups. Add a row whenever something is tested, including when the answer
is "no change".

## MLB
| Date | Tried | Result | Kept? | Where |
|---|---|---|---|---|
| Nov 10 | Quarter-win add for hitters 30 and under projected 2.5 to 4.25 wins | Gap was real: +0.36 (se 0.11) in year one, +0.30 in year two, every block of years. After the fix the tiers sit at -0.04, +0.05, +0.07 | Yes, 62 hitters | `engine/y1_split.py`, `y1_bump.py` |
| Nov 10 | Same question for hitters 31 and over, and for starters | Hitters 31+: -0.02. Starters: +0.11 (se 0.14), young ones over-projected, older under | No change | `engine/y1_split.py` |
| Nov 10 | Full rebuild of `desk_data.json` to apply a data change | Drifts from the live page in three side tables (status, prospect ranks, one missing table) | No. Change the page's data surgically | `engine/apply_y1.mjs` |
| Nov 10 | Move the trade book, player fates and quiz notes out of the first download | Page 15% smaller over the wire; three views needed a redraw when the book arrives; identical once loaded | Yes | `engine/split_book.py` |
| Nov 10 | Phone load re-timed after the split (live, throttled) | Home content 3.3 s on 4G (was 3.7) and 8.2 s on slow 4G (was 9.4); everything 6.0 s and 17.9 s | Measured | `tests/tools/perf_live.mjs` |
| Nov 10 | Moving more data out (player names, the Desk's player table) | Not tried: used at first paint everywhere, large risk for about 8% and 35% | Open | |
| Nov 10 | Scheduled refreshes: stop fast when Chrome is asleep, stamp a checked time, run more often | In place; first runs on the new schedule not yet observed | Yes | task prompts |
| Nov 10 | Qualifying-offer cost turning a market-rate signing into an F | Model is consistent (0.95 wins for most clubs, 1.5 over the tax line); the sheet now says what the grade is without the pick | Wording only | page |
| Nov 10 | Year-one projection too low for aces and stars? | No: aces 3.6 projected against 3.4 actual, star hitters 5.4 against 5.0 | No change | `engine/y1_bt.py` |
| Nov 10 | Aging too fast for stars? | Hitters fine for 2010-19 holdout; pitchers aged too fast | Pitcher attrition penalty halved (0.06 to 0.03) | `engine/aging_bt.py` |
| Nov 10 | Kirk's launch QA (3 blockers, 16 should-fix) | All fixed; re-walked live Nov 10 night, 32 of 32 scripted cases pass | Yes | `docs/qa-rewalk-nov10.md`, `tests/t_qa.mjs` |
| Nov 10 | Recover Sean's earlier formatting notes from stored transcripts | Not recoverable | Needs a re-list | |

## NHL
| Date | Tried | Result | Kept? | Where |
|---|---|---|---|---|
| Nov 10 | Value stat from season lines (v0) | Believable for forwards and scoring defensemen; repeats at 0.66 (F) and 0.61 (D) | Yes, as the base | `docs/nhl-value-v0.md` |
| Nov 10 | Handing each skater a share of his club's shot suppression | Does not follow a player to a new club (0.01 to 0.07) | Removed | `engine/nhl/movers.py` |
| Nov 10 | Heavy weight on plus-minus before 2009-10 | Lowers repeatability, no gain in club prediction | Weight 0.1 | `engine/nhl/test.py` |
| Nov 10 | Expected goals from shot location | Works: 0.773 discrimination, calibrated in every tenth | Yes | `engine/nhl/xg.py` |
| Nov 10 | Goalies on goals saved above expected | No better than save percentage (0.17 against 0.19 year to year); club effect remains | No. Goalies stay on saves at 70% | `engine/nhl/goalies.py` |
| Nov 10 | Shift-level skater model in place of season-line parts | Worse on repeat and on movers (0.27 against 0.54) | No | `engine/nhl/value1.py` |
| Nov 10 | v0 plus half of the shift-level effects (v1) | Club prediction 0.595 against 0.567; everything else level | Yes | `docs/nhl-value-v1.md` |
| Nov 10 | Any version to lift defensemen's share of wins | 14% in every version | Unsolved. Grade defensemen against defensemen | `docs/nhl-value-v1.md` |
| Nov 10 | Draft channel on v0, then v1 | Works; v1 changes nothing material (0.998); drafting repeats at 0.38 for general managers | Yes | `docs/nhl-draft-v0.md` |
| Nov 10 | General manager tenures from an official source | Found on the league's records site, 332 stints with dates | Yes | `engine/nhl/draft.py` |
| Nov 10 | Trades from Wikipedia's season transaction pages | All 21 seasons parsed: 2,435 trades, 84% of players matched to league ids, 2,881 picks. The JSON interface rate-limits after two pages; the plain-text page form (`index.php?action=raw`) does not | Working source, Sean decides later | `engine/nhl/trades_wiki.py` |
| Nov 10 | Valuing both sides of every trade and attributing to general managers | Works end to end; results repeat weakly (0.23 first half against second, 0.35 alternating); conditional picks and re-signings are the weak points | First cut | `docs/nhl-trades-v0.md` |
| Nov 10 | Tying a traded pick to "the sender's own pick" when the page names no owner | Wrong often enough to inflate results (a late first read as second overall). Now only when the draft record shows the pick passed through the acquiring club, or the page gives the overall number | Fixed | `engine/nhl/trades_value.py` |

## What a better NHL trade source would have to beat
Wikipedia's season pages are the working source (Nov 10, pending Sean's decision). They give: every trade
with its date, both clubs, every player, every pick with round, year and original owner, conditions in
footnotes, and a citation to the club or league announcement on each row; free to reuse with credit; 85% of
traded players match a league id by name and the rest mostly never played. A replacement is only worth it
if it adds at least one of: league player ids on every asset (no name matching), conditions and retained
salary as data instead of footnotes, the pick each traded selection finally became, or contract terms.
It would also need to be pullable without the rate limit that slows the Wikipedia pull to a few pages at a time.

## Standing facts worth not rediscovering
- Deploy: build with `engine/split_book.py`, upload `index.html` and `book.js` together when the book changes.
- Running all 12 suites at once makes `t_wire` flake on its readers-grade check; four at a time is clean.
- GitHub's upload page: the file input's ref changes from page to page (`ref_100`, `ref_101`, `ref_103` have
  all appeared, for existing folders too). Always read it from `find` before uploading.
- A large upload over the Chrome link can lose its reply while still landing: check with `git fetch` before
  repeating.
- The NHL stats service returns everything for a season and club in one call with `limit=-1`; game feeds
  take about 80 seconds a season at eight at a time.
