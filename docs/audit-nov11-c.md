# Nov 11 audit, part 3 (block 4)

Scripts are in `tests/tools/`; each section names the one it used. Engine runs need `/work` (asset_rules.py
and its data). ledger.sqlite is not in the repo, so the engine's free-agent, release and signing events are
rebuilt from the page's own moves feed (`moves.js`). With that stand-in, the engine reproduces the published
trade book on 1,285 of 1,342 checked player rows (96%) within 0.06 wins. All comparisons below are new minus
old from the same stand-in, so the remaining 4% offsets cancel.

## 1. Regression tests, one per bug

| Bug | Check (suite) | Pre-fix commit | Result there | Now |
|---|---|---|---|---|
| Rule 5 conduit seat took the Rule 5 grade as its trade net (Romano) | `rule5ConduitSign` (t_nov11) | 221d6f5 | fails | passes |
| Same deal shown twice on a tree | `oneNodePerDeal` | 221d6f5 | fails | passes |
| Hoerner's unstarted extension read CLOSED | `unstartedExtensionOpen` | 0d586b2 | fails | passes |
| Arizona Nov 28 2003 linked legs cross-wired | `linkedLegsAddToZero` | 0d586b2 | fails | passes |
| Deals missing one side showed a number | `incompleteDealHeldBack` | 0d586b2 | fails | passes |
| Pre-2021 extension still running read CLOSED (Betts, found today, section 5) | `preCutoffStillRunningOpen` | 944772d | fails | passes |
| Lowe/Tucker season salary not charged | `tests/t_known_salary.py` (Lowe 2026, Tucker 2025, Turner 2022, Sale 2018-19) | not fixed | reports KNOWN ISSUE | reports KNOWN ISSUE |

The salary check is an engine check, not a page check. It exits 0 and prints the known issue, so it does not
hide the problem or block the other suites. `STRICT=1` makes it fail; flip that on once the fix lands.
All 13 page suites pass locally and live.

## 2. Control-end bug sized by impact (control_end_impact.py, control_end_movers.py)

Scope: the 1,917 players with service data, less 7 whose service record skips a season they played (deGrom
2017; see section 7). 1,151 have a control end different from the debut-year rule. Corrected (service-time) end versus current:
- extensions: 28 of the 163 covered move;
- trade seats: 825 move at all; 71 grades move by a win or more (53 trade seats, 18 extensions).

Top 25 movers:

| # | Kind | Club | Date | Move | Now | Corrected | Change |
|---|---|---|---|---|---|---|---|
| 1 | ext | ATL | 2022-03 | Matt Olson 8y/$168.0M, control end 2022 to 2023 | +12.0 | +3.8 | -8.2 |
| 2 | ext | MIN | 2019-02 | Jorge Polanco 5y/$25.75M, control end 2020 to 2022 | +8.7 | +1.3 | -7.4 |
| 3 | trade | ATL | 2022-03-14 | trade with ATH (Matt Olson +7.0, Shea Langeliers -0.2) | -4.2 | +2.6 | +6.8 |
| 4 | trade | ATH | 2022-03-14 | trade with ATL (Matt Olson -7.0, Shea Langeliers +0.2) | +4.2 | -2.6 | -6.8 |
| 5 | ext | TB | 2023-01 | Yandy Díaz 3y/$24.0M, control end 2022 to 2024 | +6.4 | +2.0 | -4.4 |
| 6 | trade | PHI | 2024-12-22 | trade with MIA (Jesús Luzardo +4.0) | +2.3 | +6.3 | +4.0 |
| 7 | trade | MIA | 2024-12-22 | trade with PHI (Jesús Luzardo -4.0) | -2.3 | -6.3 | -4.0 |
| 8 | ext | PHI | 2026-03 | Jesus Luzardo 5y/$135.0M, control end 2025 to 2026 | +2.1 | -1.8 | -3.9 |
| 9 | trade | TB | 2018-12-13 | trade with CLE/SEA (Yandy Díaz +3.1) | +8.4 | +11.5 | +3.1 |
| 10 | trade | CLE | 2018-12-13 | trade with SEA/TB (Yandy Díaz -3.1) | -7.4 | -10.5 | -3.1 |
| 11 | ext | LAD | 2020-02 | Chris Taylor 2y/$13.4M, control end 2020 to 2021 | +2.4 | -0.7 | -3.1 |
| 12 | trade | TB | 2020-01-09 | trade with STL (Randy Arozarena +3.1) | +8.6 | +11.7 | +3.1 |
| 13 | trade | STL | 2020-01-09 | trade with TB (Randy Arozarena -3.1) | -8.6 | -11.7 | -3.1 |
| 14 | trade | WSH | 2014-12-19 | trade with BOS/SD/SD/TB (Joe Ross +0.1, Trea Turner +2.9) | +18.5 | +21.5 | +3.0 |
| 15 | trade | SD | 2014-12-19 | trade with BOS/TB/WSH (Joe Ross -0.1, Trea Turner -2.9) | -13.1 | -16.1 | -3.0 |
| 16 | trade | MIA | 2021-07-28 | trade with ATH (Jesús Luzardo +2.9) | +5.8 | +8.7 | +2.9 |
| 17 | trade | ATH | 2021-07-28 | trade with MIA (Jesús Luzardo -2.9) | -5.8 | -8.7 | -2.9 |
| 18 | ext | MIN | 2021-11 | Byron Buxton 7y/$100.0M, control end 2021 to 2022 | +7.8 | +4.9 | -2.9 |
| 19 | ext | TB | 2022-08 | Tyler Glasnow 2y/$30.35M, control end 2022 to 2023 | +1.2 | -1.5 | -2.7 |
| 20 | ext | LAD | 2020-02 | Max Muncy 3y/$26.0M, control end 2021 to 2022 | +2.0 | -0.5 | -2.5 |
| 21 | trade | ATH | 2017-07-16 | trade with WSH (Jesús Luzardo +1.9, Blake Treinen +0.5) | +4.9 | +7.4 | +2.5 |
| 22 | trade | WSH | 2017-07-16 | trade with ATH (Jesús Luzardo -1.9, Blake Treinen -0.5) | -4.9 | -7.4 | -2.5 |
| 23 | trade | LAD | 2016-06-19 | trade with SEA (Chris Taylor +2.4) | +9.3 | +11.7 | +2.4 |
| 24 | trade | SEA | 2016-06-19 | trade with LAD (Chris Taylor -2.4) | -9.3 | -11.7 | -2.4 |
| 25 | ext | COL | 2022-03 | Ryan McMahon 6y/$70.0M, control end 2023 to 2024 | +2.1 | -0.3 | -2.4 |

The pattern: an extra controlled season moves value out of the extension, where it was being called a
bought-out free-agent year, and into the trade that brought the player in. Atlanta's Olson moves are
-8.2 on the extension and +6.8 on the trade, nearly a wash for the club but a large swing for each grade.
Grades that flip sign include the Olson trade (both seats) and the Luzardo, Taylor and Glasnow extensions.

Club ranks (all-time trades plus extensions, the 30-club table; 14 clubs move):
MIL 4 to 2, TB 2 to 3, ATH 3 to 4; COL 10 to 11, SF 11 to 10; CHC 17 to 13, SD 13 to 16, DET 18 to 15,
MIN 15 to 18, LAD 16 to 17; CWS 19 to 20, KC 20 to 19; SEA 24 to 25, TEX 25 to 24.
Biggest club totals: MIN -14.5, LAD -9.6, SD -8.9, STL -6.1, SEA -5.4. This is a lower bound, since only
players with service data were re-run. Regime (GM) ranks were not recomputed here.

## 3. $0 post-control seasons, sampled (zero_salary_sample.py)

**Correction first.** The 2,370 count in part 2 does not reproduce. Rebuilt with the engine's own windows
(which end at a free-agent filing or release), the population is **802 player-seasons in 549 trade seats**
since 2015, out of 6,802 acquired player-seasons. The earlier figure most likely counted each season from both
seats of the trade (13,229 is close to 2 x 6,802) and missed the window cutoffs. Use 802.

Seed stated before drawing: **20261112**, same LCG as audit_sample.mjs, 30 without replacement. Salaries are
from Baseball-Reference salary tables, pulled same-origin in Chrome.

| Class | n | Share (90% interval) | Of 802 | Cases |
|---|---|---|---|---|
| Arbitration year the engine treats as free (control-end bug) | 13 | 43% (30-58%) | about 350 (237-466) | Piña 2019, Kratz 2019, Castro 2022, Díaz 2022, Stassi 2021, Richards 2024, Soler 2021, McGuire 2026, Montas 2022, Sewald 2024, Kittredge 2024, Torrens 2026, Slater 2024 |
| Contract on file, missing from the contract book (data gap: options, extensions signed with an earlier club) | 9 | 30% (18-45%) | about 240 (148-360) | Escobar 2017 option, Cueto 2015 option, García 2017 option, Barnhart 2022 option, Gordon 2018 extension, McCullers 2026 extension, Martin 2022, Trevino 2026, Enns 2026 |
| Genuine minimum or minor-league season ($0 is right) | 6 | 20% (11-34%) | about 160 (86-275) | Coghlan 2017, Freeman 2020, Abad 2021, León 2026, Nolin 2023, McKinney 2024 |
| Season should not be in the window (free agent, buyout) | 2 | 7% (2-18%) | about 50 (18-147) | Plouffe 2018, Kittredge 2026 |

So 22 of 30 (73%, interval 59-84%) are real salary seasons charged $0: about 590 of the 802 (469 to 676).
Model bug and data gap are close to even. The service-time fix closes the first class. Adding options and
earlier-club contracts to the contract book closes the second. A small third bug is that a window can run
past free agency when the feed has no filing.

## 4. Lazy-load of the Deal Desk comps

Only the comps (`DESK.deals`, about 103 KB zipped) moved. They serve only the Deal Desk and Simulator. The
other big block (`DESK.peak`, prospect peaks) stays inline. Rendering every view with it empty changed text
on home, the Wire, report cards, Horizon and the boards, so deferring it would make home numbers shift after
load. The comps now load from `deals.js` three seconds after the page loads, or right away when the Deal Desk
or Simulator opens; the view re-renders when they arrive. The working page keeps them inline;
split_book.py and unsplit_book.py do the move and round-trip byte for byte.

Same profile (slow 4G 1.6 Mbps, 150 ms, 4x CPU, iPhone viewport), live site, median of 3:

| | Before | After |
|---|---|---|
| index.html (zipped, on the wire) | 1,082 KB in 6.4 s | 976 KB in 5.7 s |
| DOMContentLoaded | 7.96 s | 7.67 s |
| Home content on screen | 9.07 s | 7.79 s |
| Network idle | 16.86 s | 16.75 s |

Home content arrives 1.3 s sooner. One side effect found and fixed the same hour: when the comps arrived the Desk re-rendered and wiped an Assistant GM note already on screen (t_qa caught it live for LAA); the note is now kept, with its own check (`agmNoteSurvivesComps`). Idle barely moves: cards.js (915 KB) and moves.js (524 KB) still
dominate it. Moving those behind first paint is the next step.

## 5. Date-keyed rules added today, checked

| Rule | Keys on | In-season or pre-start extension check | Result |
|---|---|---|---|
| Decisions before 2021 keep the engine's flag | sign year < 2021 | Betts (Jul 2020, through 2032, still a Dodger) read CLOSED. So did 29 pre-2021 draft and international signings still in their control years (Henderson, Westburg, Kirby, Kwan, Pages and others) | **2 bugs, fixed.** An extension with seasons still to come and the player with the club is OPEN. A draft or international decision is OPEN while the player is with the club with under six years of service (the page's service figure, not the debut rule). Judge (2013 draft) stays CLOSED. |
| Free agency: winter + years <= 2026 is closed | label "(YYYY-YY winter)" | Only matches winter signings; in-season signings fall through to the roster check | Holds |
| Extension: seasons elapsed and none to come is closed | engine sides | In-season extensions starting next season read "no seasons elapsed" and stay OPEN (Bradish, Burns, Wetherholt). Pre-start ones that began 2026 keep a "Still to come" side. 0 extensions with seasons left read CLOSED | Holds; one stale case: Reynolds' 2022 two-year deal still reads OPEN because the engine marks a season "not yet played" after his 2023 extension took it over. Data, not the rule; left as known. |
| "Next N seasons" windows (waivers, players let walk) | claim date, Oct+ starts next year | Same convention as the engine | Holds |
| Out of the league: last season < 2026 | season | Not extension-specific | Holds |

I also tried "a later extension closes the earlier one" for Reynolds and dropped it: Cristopher Sánchez's
2026 extension adds years on top of his 2024 deal, which is still running.

## 6. Error rate restated as root causes per move

The 92 high-traffic checks were not independent: Lowe and Tucker are one salary mechanism, and every OPEN
error traced to one rule. Counted by root cause:

| Sample | Moves | Errors (field level) | Distinct root causes | New ones |
|---|---|---|---|---|
| Random 40 (seed 20261111) | 40 | 5 | 3: control end from debut year (Donaldson, 2 fields); OPEN keyed on the acquirer (Houser, Lopez); "realized on" label (Lopez) | 3 |
| High-traffic 20 | 20 | 3 | 3: control end (Tucker); options missing from the contract book (Lowe); my unstarted-extension rule (Hoerner) | 2 |
| Rules check (this pass) | 98 extensions plus the pre-2021 sweep | 31 decisions | 2: the 2021 cutoff (Betts, 29 draft and international); stale engine side (Reynolds) | 2 |

That is **5 root causes in 60 moves checked, about one per 12 moves**. In the high-traffic 20: two new causes
and one repeat. Three of the seven causes found today came from rules written today (the OPEN rule, the
unstarted-extension rule, the 2021 cutoff). New rules are the riskiest code on the site, so each now has a
named regression check.

## 7. Pushback round (Nov 11, 8:30 ET)

**Where the old 2,370 appeared.** docs/audit-nov11-b.md section 7 (fixed, with the correction noted),
docs/worklog.md block 3 entry (fixed), project memory (fixed). Not in index.html, site copy, HANDOFF or the
project docs. Earlier chat summaries to Kirk carried it and cannot be edited; this note supersedes them.

**Arbitration years treated as free.** 13 of 30, so 43% with a 90% interval of 30% to 58%: about 350 of the 802,
**237 to 466** (Wilson interval). Shadow fix, report only: price each such season with the engine's own award
model (`arb_salary`: 0.6 plus the better of last season's WAR and the two-season average, times the class step
1.0 / 1.5 / 3.1, times $/win drift) under the service-time control end. Checked against what the 13 were
actually paid (Baseball-Reference):
- 10 of 13 can be priced; Piña, Kratz and Stassi have no service record, so the shadow leaves them at $0.
- On the 10: $47.9M modeled against $39.8M paid, median miss $1.7M, about 20% too high overall. Worst:
  Torrens 2026 ($6.2M modeled, $2.3M paid), Richards 2024 ($4.4M against $2.2M).
- Better rule for the fix: the real salary when it is known (contract book, or the MLB Trade Rumors
  arbitration files for 2026 and 2027 already in /work), the award model only when it is not.
- Grades moving by a win or more with the service-time end and the award model applied: 71 (53 trade seats,
  18 extensions). Window length and salary change together in that run; they were not separated.
Nothing shipped.

**What would prove the service-time ends wrong, and the hand check.** A season's starting service of 6.000 or
more means the player was already free; the control end is the last season that starts under 6.000.
Baseball-Reference salary tables list service at the start of each season:

| Player | Engine (debut rule) | Service time rule | Baseball-Reference | Verdict |
|---|---|---|---|---|
| Matt Olson | 2022 | 2023 | 2023 starts 5.103, 2024 starts 6.103 | service rule right |
| Jorge Polanco | 2020 | 2022 | 2022 starts 5.024, 2023 starts 6.024 | service rule right |
| Yandy Díaz | 2022 | 2024 | 2024 starts 5.122, 2025 starts 6.122 | service rule right |
| Chris Taylor | 2020 | 2021 | 2021 starts 5.037, 2022 starts 6.037 | service rule right |
| Tyler Glasnow | 2022 | 2023 | 2023 starts 5.158, 2024 starts 6.158 | service rule right |
| Jacob deGrom | 2020 | 2021 | 2020 starts 5.139, 2021 starts 6.139 | **service rule wrong** |

deGrom's service record has no 2017 row although he pitched all of 2017, so the sum ran a season long. Seven
players have such a hole; the tools now give no service-time answer for them (the debut rule stands). deGrom
dropped out of the top 25 and the club table above; NYM no longer moves. Sources:
baseball-reference.com/players/o/olsonma02.shtml, /p/polanjo01, /d/diazya01, /t/tayloch03, /g/glasnty01,
/d/degroja01 (salary tables, service column).

**Tests for each of today's rules.** Five rules had no check that would catch their own failure: the waiver
window, a claimant who filed for free agency, an ended free-agent contract, a post-2021 draft pick no longer in
the league, and the two-club repair. Added to t_nov11 (Kyle Nelson 2021 claim, Jesús Sánchez 2026 claim, Ozuna
2021-24, Benny Montgomery 2021 draft, Greinke 2012). All five fail on a0340e0 (before the OPEN rules) and pass
now; the Greinke check also fails on 221d6f5 (before the repair). Every rule written Nov 11 now has one.

**Largest remaining item on the slow-4G load.** index.html itself. Blocking cards.js, moves.js and book.js
together leaves home content at about 7.3 to 8.0 s (against 7.5 to 8.4 s with nothing blocked), so the
first document gates home, not the scripts after it. Inside index.html (919 KB zipped): DESK 322 KB (35%;
the prospect peaks are about 104 KB of it), code and styles about 354 KB, player names 102 KB, AUTO_REGIMES
86 KB.

## 8. Fresh sample of 40 (Nov 11, 9 AM round)

**Draw.** Seed 20261113, same LCG. Uniform over every graded move, not the report cards (the cards list each
club's best and worst moves, so a card-row sample leans to extremes): the 4,172 trades in the trade book (one
side picked at random) and the 3,545 free-agent signings and extensions in the contract book since 1998.
The 60 moves already audited are skipped. Drawn: 23 trades, 14 signings, 3 extensions; 13 from 1998-2009,
16 from 2010-19, 11 from 2020-26. Script: `tests/tools/audit_sample2.py`.

**Checks.** Players and date against the league feed (18 trades) or Baseball-Reference (the feed has gaps
before about 2008); signing terms against Baseball-Reference salary tables; OPEN/CLOSED against each player's
status and window; trade sides add to zero.

| Field | Checked | Wrong | Unverified |
|---|---|---|---|
| Players and date | 38 | 0 | 2 (Romero/Casilla 2005, Shackelford/Austin 2003: neither source answered) |
| Terms | 13 | 1: Kurt Suzuki's 2010 extension starts in 2010 in the contract book; it covered 2011-14 | 4 |
| OPEN / CLOSED | 40 | 1: Utley to the Dodgers (2015) read OPEN | 0 |
| Trade sides add to zero | 23 | 0 | 0 |
| **All** | **152** | **2 (1.3%)** | |

**Error rate.** 2 of 40 moves have a wrong field: **5.0%, 90% interval 0.9% to 14.9%**. The Utley error came
from my own trade OPEN rule (below) and is fixed, which leaves 1 of 40 (2.5%, 0.1% to 11.3%). The earlier
random 40 had 3 of 40 (7.5%, 2.1% to 18.3%). The intervals overlap almost entirely, so the "7.5% down to 2.7%"
story is not shown by the data: samples of 40 cannot tell those rates apart. What they do show is that
errors per move sit somewhere from about 1% to 15%.

**Gaps, separate from errors.** 8 of 40 moves show something missing rather than wrong: 5 signings from the
2003-05 winters (Clayton, Lofton, Halter, Wells, Wright) show the feed line with no terms and no grade, and 3
signings are not on the player's tree at all (Flaherty 2004, Suzuki's 2010 extension, Howell 2017). Errors
plus gaps: 9 of 40 moves, 22.5% (12.3% to 36.0%). Completeness of older signings is the larger problem.

**Root cause found: trade OPEN rule (written Nov 11).** A piece of unknown status counted as active, and an old
trade had no window check, so 694 of 4,156 pre-2021 trades read OPEN (Utley's on John Richy, a minor leaguer
with no current record). Fixed: a piece keeps a trade open while he is active and his window from the trade has
not run out (six seasons, or his club-control years if longer); an unknown-status piece counts only inside the six
seasons. Pre-2021 trades OPEN: 694 to 88, each with a piece still active and under club control (Trammell keeps
the 2019 Bauer three-team deal open, correctly). All trades OPEN: 1,512 to 849; 2022-26 unchanged. Tests
written first and failing before the fix: `oldTradeUnknownPieceClosed`, `controlYearsKeepTradeOpen`.

That makes 8 root causes found Nov 11, 4 of them in rules written that day.

## 9. Phone load, conditions and spread

Playwright Chromium, iPhone viewport 390 x 844 with a mobile user agent, network 1.6 Mbps down / 750 kbps up /
150 ms (Lighthouse "slow 4G"), CPU slowed 4x, fresh browser context per run (cold cache), live site.
Metrics: LCP from the browser's own observer, and "home content visible" (the home view present with more than
2,000 characters of text). LCP fires at about 1 s on the masthead, so it does not measure when the page
becomes useful; home content visible is the number to quote.

Five clean runs after the Nov 11 9 AM deploy, nothing else running on the machine:

| Run | LCP | DOMContentLoaded | Home content visible | Network idle |
|---|---|---|---|---|
| 1 | 1.11 s | 7.23 s | 7.35 s | 16.18 s |
| 2 | 1.06 s | 7.41 s | 8.13 s | 16.34 s |
| 3 | 0.72 s | 7.34 s | 7.45 s | 16.31 s |
| 4 | 1.28 s | 7.71 s | 8.45 s | 16.58 s |
| 5 | 0.66 s | 7.41 s | 7.51 s | 16.42 s |
| **Median (range)** | **1.06 s** | **7.41 s** | **7.51 s (7.35 to 8.45)** | **16.34 s** |

An earlier set of five read 8.74 s median; it ran while other test scripts used the CPU, so it is set aside.

**Home-first file, estimate only (not built).** The full index.html is 919 KB zipped: about 4.6 s to download at
1.6 Mbps plus about 1.5 to 2 s to parse and run at 4x CPU slowdown, which is most of the 7.5 s. A home-first
document carrying only the home view's code and the numbers it shows would be about 150 to 250 KB zipped, so
home content could appear at roughly 2.5 to 3.5 s, a saving of about 4 to 5 s, with the full page loading behind
it. Drift risk: the home numbers would be a snapshot. Built by a separate job, the snapshot could disagree with
the full data, and home would visibly change when the full page loads, the same problem that kept the prospect
peaks and player names inline. Built in the same split step from the same data, the risk is small, provided a
check renders home both ways in every build and fails the build on any difference. Live feeds (the Wire,
trade reports) would still load live either way.

## 10. Round 7 (Nov 11, 9:30 AM)

**Ten of the 88 still-open pre-2021 trades, hand-checked (seed 20261114).** Truly open, a piece still active
and inside his window: Corniell (TEX 2020), Baker (TOR 2018: only waiver claims and a trade since), Wilcox
(TB 2020), Conine (MIA 2020), Trammell (SEA 2020: claims and a trade, no release). Not open: Vieira (CWS 2017,
released 2019), Yean (PIT 2020, minor-league deal 2025), Enns (MIN 2017, minor-league deal 2018), Rivas (CIN
2020, free agent Nov 2022, signed with Seattle Jan 2023 per Baseball-Reference) and Lukes (TB 2016, free agent
Nov 2021, signed with Toronto). 5 of 10 were rule misses. The engine ends a piece's window at a release or a
free-agent signing anywhere; my rule did not. Fixed with tests first (`releasedPieceClosesTrade` failing before,
`claimedPieceKeepsTradeOpen`): pre-2021 OPEN trades 88 to 50, all trades 849 to 707. Rivas and Lukes stay
OPEN: the league feed carries no minor-league free agency for them, so the page and the engine both miss it.

**Grades and ranks before and after both OPEN fixes.** 0 of 13,209 grades changed (the new grade snapshot
passes against the page from before the fixes) and no view's text changed except the Wire clock, so no club
rank moved. OPEN/CLOSED labels changed on player trees and card rows only.

**Suzuki's extension start.** Our own research file, `data/research/ext_1998_2014.csv`, has first_season 2010
for the July 2010 deal; the build copied it. Baseball-Reference: $420,000 in 2010, $3.4375M in 2011, so it
started in 2011. Sweep: 3 extensions signed June or later start in the signing season (Suzuki 2010, Tabata
2011, Luis Lara 2026); 16 more start in the last season of a prior deal with the same club, which is normal for
a deal that tears up the old one. Hand-checked 5 against Baseball-Reference salaries: Suzuki wrong; Tabata 2011
(the reported six years include 2011), Pedroia 2014, Carrasco 2019, Chipper Jones 2006 right.

**Signings without terms or grades, full count (3,545 signings and extensions since 1998, matched to the
player trees):**

| Kind, years | Moves | Graded | Terms, no grade | No terms | Not on the tree |
|---|---|---|---|---|---|
| Free agent 1998-2005 | 689 | 318 | 5 | 249 | 117 |
| Free agent 2006-14 | 839 | 298 | 524 | 15 | 2 |
| Free agent 2015-26 | 1,210 | 433 | 753 | 20 | 4 |
| Extension 1998-2005 | 141 | 1 | 0 | 4 | 136 |
| Extension 2006-14 | 388 | 2 | 8 | 1 | 377 |
| Extension 2015-26 | 278 | 2 | 263 | 5 | 8 |

"Graded" means a net number on the tree node; "terms, no grade" shows the contract and the WAR produced but no
net. Extensions from 1998-2014 are almost all missing from the trees (513 of 529, from the ext98 source).
Trades are all graded (4,172, with 2 held back as incomplete). The report cards and rankings are clean: all
1,567 signing rows on the cards have terms and a number, so no card or ranking includes an ungraded move.
The gap is on player trees only. (Counts come from matching each contract to a tree node by club and year;
the sample findings in section 8 match.)

**The 7 service-record gaps.** No public page changes: the service-time control end is not on the site, and
the exclusion lives only in the report tools. Filling the gap from Baseball-Reference is better where it
exists: its salary table gives starting service for deGrom, White, Allen, Sears and Oviedo; it has none for
Turnbull and one season for Estes. Recommended when the fix ships: Baseball-Reference first, debut rule only
where neither source has the season.

**Arbitration model, held-out test (`tests/tools/arb_calib_holdout.py`).** Actual salaries from
Baseball-Reference for 40 arbitration-eligible players (seed 20261115; 9 had no salary table): 83 arbitration
seasons from 28 players, 2018-26, excluding 2020 and seasons owned by multi-year deals.
- Current model: $364.7M against $446.2M paid, **18% low**; median miss $1.42M a season.
- Refit (base and the four class steps), each season held out in turn: 9% low; median miss $1.70M.
- The earlier 10-case check said 20% high. The direction flips with the sample, and no fit gets a season
  closer than about $1.5M. Not calibrated; do not use it for the fix. Use actual salaries (contract book,
  Baseball-Reference) and leave unknown arbitration seasons flagged rather than estimated.

**Phone, top three on the 7.5 s load** (CPU profile on the same slow-4G profile; the profiler slows the run):
1. Bytes: index.html, 976 KB zipped, 5.7 to 6.4 s on the wire. The CPU sits idle for about 3.5 s of it.
2. Parse and compile: about 2.6 to 2.8 s of browser work ("program") for the 3.3 MB page at 4x slowdown.
3. Home render: `renderHome` spends about 0.8 s in Desk and Simulator projections (the hub's free-agent and
   trade widgets: dkSuggest, gmProj27, gmPV) and the Wire panel about 0.5 s grading signings before it draws.

Cut under 1 s with no new build file: draw the home hub first and fill those two panels on the next frame.
Same data and same numbers, so no drift; the panels appear a moment later. Estimated 0.8 to 1.2 s off home
content visible. Not built.

**Do the suites catch a wrong grade?** No, before today. A planted +2.0 on a 2018 CWS/NYY trade (both sides
moved so they still add to zero) shows on the page and on the player tree, and 12 of 13 suites passed (the
13th failed only on a check newer than the planted page). A first plant on one side only never reached the
page (the two-club repair recomputes that side). New suite `t_grades`: a snapshot of all 13,209 shown grades
(every trade side and every card row) in `tests/fixtures/grades.json`. It fails on the plant (2 grades changed)
and passes on the real page. Regenerate it on purpose with `UPDATE=1` after an intended change.

Root causes found Nov 11: 9, 5 of them in rules written that day.

## 11. Round 8 (Nov 11, 10 AM)

**Do grades read OPEN/CLOSED? No, by design.** `folTradeOpen` and `folDecOpen` return a flag that only goes to a
decision's `open` field and a tree node's `status` (index.html lines 2282, 2316, 2592, 2624, 10992). Every
reader of a decision's `.open` draws a label: tree status, the UNSETTLED/SETTLED chip, the prospect-value tag
(lines 2568-2667, 10950-11042, 13175-13619). No `.open` read sits inside a filter, sum, sort or rank, and the
grade functions (`seatNet`, card `war`, the engine's `trade_window`) never take it. The engine's only "open" is
the prospect value still expected, which keys on the trade date and the prospect's status, not on the page flag.
So the 0 of 13,209 is by construction; `t_grades` now guards it.

**Ten more of the 50 still-open pre-2021 trades (seed 20261116), against Baseball-Reference transactions.**
Truly open: Wilcox, Koss, Trammell, O'Brien, Baz, Speier, Edwards, Cantillo/Arias/Waldron. Not open: Lukes
(minor-league free agency 2021, again) and Ponce (released by Pittsburgh Nov 2021; the league feed shows no move
for him at all). 2 of 10 missed, both invisible to the feed: 20%, 90% interval 7% to 46%, so roughly 5 to 20 of
the 50. Material, so OPEN is now labelled as following the league's transaction feed: the tree legend, the
trades legend and every UNSETTLED chip say the feed misses some minor-league releases and free agency, so an
older deal marked open may in fact be settled.

**`data/research/ext_1998_2014.csv` (532 rows), seeded sample of 30 (seed 20261117) against Baseball-Reference
salaries.** 20 checkable (Baseball-Reference served pages without salary tables for the other 10 after the
first 20; not retried today).
- Wrong: David Ross 2007 is credited to Atlanta; both seasons (2007 $1.6M, 2008 $2.525M) were with
  Cincinnati, so the grade sits on the wrong club. Chad Tracy 2006 starts in 2006; his 2006 salary was the
  minimum and the deal ran 2007-09 (the Suzuki pattern, a May signing).
- Doubtful: Scott Feldman 2010, 2 years / $11.5M; he was paid $6.8M for 2010-11 and $13.3M with the 2012
  option, so the total matches neither reading.
- Right: Derrek Lee, Zimmermann, Ziegler, Brett Anderson, Haren, Tulowitzki, Brantley, Buehrle, Motte,
  Desmond, Figgins, Holliday, Piazza, Kotsay, Burrell (sums match the totals; first seasons match the salary
  jump); Zito 2002 is consistent if the total includes his 2002 bonus.
- 2 clear errors in 20 (10%, 90% interval 3.5% to 27%), 3 counting Feldman, plus Suzuki outside the sample.
  Fields wrong: club, first season, total. That is more than 1 or 2, so the file is a root cause on its own:
  roughly 20 to 140 of its 532 rows may carry a wrong club, start or total. It feeds the contract book (src
  `ext98`), so its extension grades and the trade windows those contracts cut are affected.

**Arbitration model: what the 83 are, and whether it feeds public numbers.**
- The 83: seasons 2018-26 (2025-26 under-weighted: 23% of the sample against 39% of all arbitration seasons
  in the service data, because multi-year deals own more recent seasons), classes 11% / 29% / 31% / 29%
  (population 11% / 27% / 36% / 24%), 59% pitchers (population 56%). Close to representative apart from the
  most recent two seasons.
- Why the sign flipped: the model squeezes salaries toward the middle. Lowest third of the 83 (paid up to
  $2.5M): model 12% high. Middle third: 19% low. Top third: 23% low. The first 10 cases were mostly cheap
  bench and bullpen arms, so they read 20% high.
- **It does feed public numbers today.** `asset_rules.contract_cost` charges `arb_salary` for any season
  inside the engine's arbitration years with no contract on file, `ext_grade.py` (line 147) uses it for the
  arbitration path in extension grades, and the page's `gmArbSal` (16 calls) prices arbitration salaries in
  the Simulator and Deal Desk. Count: 3,919 of 16,071 acquired player-seasons in trade windows (24%) are
  priced by it, on 2,007 trade sides; on 315 sides its charge is a win or more. Its compression means trade
  grades charge too little for good players' arbitration years (acquirers look a little better) and too much
  for fringe players'. This is a live accuracy item, not a shadow one.

**Phone: compression.** GitHub Pages serves index.html gzipped: 976 KB on the wire from 3.29 MB raw (30%).
Brotli is not offered (asking for br alone returns the raw file). Brotli at its strongest setting would be
700 KB, 276 KB less, about 1.4 s on slow 4G, but it needs a host or CDN in front of Pages that serves Brotli,
not a code change. Cache lifetime is 10 minutes (max-age=600).

**Grade snapshot regeneration now leaves a record.** `UPDATE=1` refuses without `REASON="..."` (15+
characters). It writes every grade that moved, by how much, and the commit to `docs/grade-changes.md`
(created today with the baseline entry). Demonstrated on the planted page and reverted.

**Process.** `docs/rule-checklist.md`: the eight steps every new rule passes before it ships (state the rule
and its engine counterpart, failing tests first, count what moves across the full population, 10 seeded hand
checks of changed items, 10 of unchanged items, a planted case a suite must catch, all suites with the grade
snapshot, then a live re-run).

Root causes found Nov 11: 10 (the research file added), 5 in rules written that day.

## 12. Round 9 (Nov 11, 10:30 AM)

**Arbitration salaries in trade grades, shadow only (pre-registered in `docs/prereg-arb-shadow.md`, written
locally at 15:18 UTC before the run; it reached the repo only after the run, so the commit time does not prove the
order; script `tests/tools/arb_shadow.py`).** Population: every acquired player-season in a
trade window the award model prices: 5,245 seasons on 2,544 trade sides (the earlier 3,919 / 2,007 counted only
seasons charged above the minimum).
- Run 1, real salaries where we have them: 75 of 5,245 seasons (1.4%). 2 sides move a win or more, 2 flip, no
  top-25 or club-rank change. Too little coverage to settle anything.
- Run 2, sensitivity: each season's salary times a ratio drawn from the 83 held-out seasons, binned by the
  model's predicted salary, 500 draws (seed 20261118). Median (5th to 95th percentile): **341 sides move a win
  or more (305 to 374); 63 sign flips (46 to 77); 5 changes to the league top or bottom 25 (3 to 6); 10 clubs
  move 2+ places in the all-time trade table (6 to 15), the largest by 5 (3 to 7).**
- **Material on all four pre-registered tests.** Caveat: draws are independent by season, so they ignore that a
  player's seasons miss together; that widens the true spread but does not move the median direction, since the
  model is low in every bin.

**Calibration terciles, both ways (player-level bootstrap, 2,000 draws, seed 20261119).**

| Split on | Low third | Middle third | Top third |
|---|---|---|---|
| Actual salary | +12% (-10% to +39%) | -19% (-39% to +8%) | -23% (-31% to -13%) |
| Model's predicted salary | **-51% (-60% to -35%)** | **-25% (-37% to -10%)** | -7% (-18% to +10%) |

Splitting on actual salary manufactured the "squeeze": sorting on the outcome puts players who were paid less
than expected in the bottom third. Split on the prediction, the model is low everywhere, worst where it predicts
the least (near its $0.75M floor). Last round's "12% high on the cheapest third" is withdrawn.

**`ext_1998_2014.csv`, all 30 sampled rows.** Baseball-Reference served the other 11 pages without salary
tables again, so the second source was contemporary reports and Spotrac: 6 confirmed (Capps 2008-09 $3.05M,
Villarreal 2008-09 $2.85M, Freddy Sánchez 2010-11 $12M, Alexei Ramírez 2012-15 $32.5M, Dessens two years, and
Webb). 5 (Vázquez, Lincecum, Willis, Delgado, Morneau) match widely reported terms but were not fetched.
- Wrong, 3 clear in 25 sourced rows (12%, 90% interval 5% to 28%): Ross 2007 (club), Tracy 2006 (first season a
  year early), **Webb 2006 (first season a year early: the deal ran 2007-10; Spotrac, signed Jan 13 2006, and 2006
  was paid under his earlier contract)**. Plus Feldman 2010 (total doubtful) and Ramírez 2011 (signing month
  January in the file, February 3 per Spotrac and MLB Trade Rumors; minor).
- Fields that fail: first season (2), club (1), total (1 doubtful), signing month (1).
- One rule per field, run on all 532 rows (`tests/tools/ext98_rules.py`):
  - Club: the row's club must be a team he played for in the signing season, the season before, or the first
    season (the signing club, so later trades are not errors). Flags exactly 1 row, Ross. Clean and complete for
    what we found.
  - First season, signed June or later starting the same season: flags Suzuki (right) and Tabata (wrong flag),
    misses Tracy (May) and Webb (January).
  - First season inside a prior contract with the same club: catches Webb among 16 candidates, most of them
    correct tear-up deals; misses Tracy, whose prior deal is not in the book.
  - So club errors are caught by one rule; first-season and total errors are not, without each row's salary
    history. The dependable rule is "first season = the first season paid at the new rate", which needs salary
    tables for all 532 rows (Baseball-Reference, paced over several sessions, or Spotrac).

**Public counts of open trades.** None. OPEN appears only as per-row labels (tree status, UNSETTLED chips); the
"still open" strings in the page belong to scenarios and unfinished winters, not trades. Nothing needs an
interval.

**Retroactive checklist on the five rules behind today's rule-made root causes.**

| Rule | 1 engine rule | 2 tests first | 3 full count | 4 hand-check changed | 5 hand-check unchanged | 6 planted case | 7 all suites | 8 live re-run | Bug it let through |
|---|---|---|---|---|---|---|---|---|---|
| Trade OPEN follows the acquirer, then any piece in the league (morning) | no | no | partial (15 reopened) | no | no | no | yes | yes | Houser; later Utley, Vieira |
| Extension OPEN from elapsed seasons (morning) | no | no | no | no | no | no | yes | yes | Hoerner |
| Pre-2021 decisions keep the engine flag (morning) | no | no | no | no | no | no | yes | yes | Betts, 29 drafts |
| Trade window, unknown-status pieces (9 AM) | partial | yes | yes (694 to 88) | no | no (done next round: 5 of 10 wrong) | no | yes | yes | Vieira, Yean, Enns |
| Release or free agency ends the window (9:30) | yes | yes | yes (88 to 50) | **no** | yes (next round: 2 of 10 wrong, both feed gaps) | partial (grades guarded, OPEN labels not) | yes | yes | none found yet |

Every rule skipped step 4, the hand-check of items it changed. The last rule still has that gap: the 142 trades it
closed have not been checked against an outside source (Baseball-Reference was throttling); that is the first job
next session. No rule had a planted OPEN case; `t_nov11` now holds real cases for each, which serves the same purpose
going forward.

**Phone transfer size, checked as a phone.** iPhone Safari (gzip, br) and Android Chrome (gzip, br, zstd) both get
gzip: index.html 976,214 bytes on an edge-cache miss and on a hit; cards.js 914,312, moves.js 523,701, book.js
197,996, deals.js 107,389. 2.72 MB on the wire in all; the cold mobile Playwright profile measured the same
976 KB for index.html.

Root causes found Nov 11: 10, 5 in rules written that day (no new kind this round; Webb is the research file).
