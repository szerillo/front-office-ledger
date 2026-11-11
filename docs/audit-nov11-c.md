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

**Arbitration salaries in trade grades, shadow only. Pre-registered, not provable (`docs/prereg-arb-shadow.md`, written
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
- **Correction (section 13):** these runs charged a deadline deal's own season in full; the engine charges the
  acquirer's share of it. Corrected: run 1 moves 0 sides by a win (1 club rank by 1); run 2 median 286 sides
  (254 to 316), 50 flips (35 to 62), 5 top/bottom-25 changes (3 to 6), 10 clubs 2+ places (6 to 14), largest 4.
- **Material on all four pre-registered tests** (still true after the correction). Caveat: draws are independent by season, so they ignore that a
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

## 13. Round 10 (Nov 11, 11 AM): the $0 seasons with real salaries

**Correction to section 12.** The arbitration shadow charged the trade season in full. The engine
(`asset_rules.trade_window`) charges a July deal's own season by the acquirer's share of the player's stints
that year. Fixed in `tests/tools/arb_shadow.py` (`share`). Corrected run 1: 0 sides move a win or more, 0 flips.
Corrected run 2 (median, 5th to 95th): 286 sides move a win or more (254 to 316); 50 flips (35 to 62); 5 top or
bottom 25 changes (3 to 6); 10 clubs move 2+ places (6 to 14), largest 4. Still material on all four tests.

**Shadow: $0 post-control seasons at what players were paid** (pre-registered in
`docs/prereg-zero-salary-shadow.md`, committed as ddc7026 before any salary was matched to a grade; script
`tests/tools/zero_salary_shadow.py`). 802 seasons on trade sides since 2015 sit after the engine's control end
with no contract in the book and a $0 charge (`zero_salary_classes.py` sorts them: 252 inside the service-time
control end, 42 under a contract the book lacks, 24 after a free-agent filing, 484 with no service record).
- Baseball-Reference salary tables for the 413 players, pulled at one player every 9 seconds. Three parallel
  workers tripped the site's rate limit after 24 players (my error: about 24 requests a minute against its 20);
  11 more redirect to minor-league pages. Coverage so far: **40 of 802 seasons (5%), 39 paid above the $0.75M
  floor.** Fixture: `tests/fixtures/zero_br_2026-11-11.txt`. The pull resumes with one worker once the block lifts.
- On those 40 alone: **14 sides move a win or more, 2 flip, 1 club moves 2 places** in the all-time trade table.
  The club-rank test is already met, so this is material on the pre-registered bar at 5% coverage. Largest
  movers: Hamels 2019 ($20M club option, charged on both the 2015 TEX and 2018 CHC deals, -1.8 and -1.3),
  Marte 2020-21 (ARI, MIA, -1.6 each), Teoscar Hernández 2023 (SEA, -1.2).
- Combined with arbitration run 1 (real salaries only): 14 sides, 2 flips, 0 top-25 changes.
- Not yet done: the pre-registered hand check of 10 covered seasons against a second source (after the pull).

Root causes found Nov 11: 11 (the share error in my own shadow script added), 5 in rules written that day.

## 14. Round 11 (Nov 11, 11:30 AM): sampling bias, closed trades, proration

**Order of record.** Pre-registration `docs/prereg-round11.md`, commit be53af2 at 16:30:49 UTC. First output after
it: the proration population run at 16:31:13 UTC; the random-40 draw (seed 20261122, named in be53af2) between
16:31:13 and 16:33:33 UTC, so after the commit; its salary pull 17:05 to 17:18 UTC. Before the
commit (stated in the file): the 15-trade draw and three hand-worked proration cases. The $0 shadow's
pre-registration, ddc7026, is 16:01:26 UTC; its first output came after it. Section 12's arbitration shadow is
labelled "pre-registered, not provable".

**$0 seasons: pull order is biased.** The first 40 players were pulled in MLBAM id order, which runs oldest
first (median id 430,884 against 562,238 in a random draw), so veterans on bigger salaries. Random 40 from the
802 (seed 20261122, `tests/fixtures/zero_br_rand40_2026-11-11.txt`): 31 have a salary row, **25 paid above the
$0.75M floor: 62.5%, 95% interval 47% to 76%, so about 500 of the 802 (377 to 608)**. Pull order: 39 of 40
(97.5%, 87% to 99.6%). The intervals do not overlap: the pull-order figure was biased high and is withdrawn as
an estimate. With all 147 seasons now covered (pull order plus random): 22 sides move a win or more, 6 flip, 2
clubs move 2+ places. Still material on the club-rank test.
- Second source for the random 40 (seed 20261120 drew 10): Montero 2021 $2.25M, Stratton 2023 $2.8M, Heaney 2021
  $6.75M, McGuire 2026 $1.2M match (MLB Trade Rumors, Spotrac, AP); Hamels 2019 $20M option matches wide reports;
  Hutchison 2022 $0.7M against Spotrac's $0.8M; **Kittredge 2026 $1.0M is the buyout, not the salary: Baltimore
  exercised his $9M option**. Mitchell, Font, Stewart (all under the floor) not checked. 1 material miss in 7.
  McGuire 2026 is a new free-agent deal with the White Sox, so it likely should not sit in the 2022 trade window.
- "About 240 of 802" (contracts missing from the book) rests on 9 of 30: 30%, 95% interval 17% to 48%, so 134 to
  384. A guess until the pull finishes.

**15 of the trades the release / free-agency rule closed (147 on today's page; seed 20261121;
`tests/tools/closed_by_release.mjs`).** Events checked against MLB Trade Rumors, MLB.com, Spotrac, Wikipedia.
- Wrong label: **Eli White (2023 TEX/ATL)**. Atlanta released him on Jul 22 2023 and re-signed him three days
  later; he played for Atlanta into 2026 and was traded to Boston in August, so the deal should read OPEN.
  1 of 15: 6.7%, 95% interval 1.2% to 29.8%, so 2 to 44 of the 147.
- Right label, wrong reason: Germán (2014 MIA/NYY; non-tendered Dec 3 2015, re-signed by the Yankees Dec 11; the
  deal closes anyway with his 2023 free agency) and Kilian (2021 CHC/SF; released and re-signed by the Cubs
  within four days in April 2025). The other 12 events and closures are right (Bryant, Bader, Bleday, Cousins,
  Canning: free agency or non-tenders; the rest signed elsewhere).
- **New root cause, engine and page alike:** a release or non-tender followed by re-signing with the same club
  ends the window. In the engine it also cuts the grade: Germán carries 0.0 in the 2014 Yankees side.
  `tests/tools/resign_same_club.py`: 63 traded pieces were re-signed by the holding club within 60 days of a
  release or filing while inside club control (debut-rule control, so a few are true free agents); 13 produced a
  win or more for that club afterwards inside six seasons, 34.7 wins in all. Not fixed.

**Proration of the trade season.** The engine charges the trade season by the acquirer's share of the player's
stint rows (1 of 2 rows = half), not the days left. Three 2017 deals worked by hand (`proration_check.py`):
- Upton (DET to LAA, Aug 31): days left 31 of 183, so $3,747,951 of $22.125M, **matching the AP figure to the
  dollar** (Detroit paid $747,951 of it). Engine: half of the season, $10.69M above the minimum against $3.62M.
- Martinez (DET to ARI, Jul 18): 75 of 183 days, $4.82M owed, matching MLB Trade Rumors. Engine $5.94M against
  $4.51M above the minimum.
- Darvish (TEX to LAD, Jul 31): three stint rows give the Dodgers two thirds; days left give a third. Engine
  $6.17M against $3.47M.
- The assumption fails. Population (1,186 trade-season charges re-prorated by days, flips ignored): 2 sides move
  a win or more, 2 flip, 1 top or bottom 25 change, 1 club moves 2+ places. Material on two pre-registered tests.
  Cash sent with a player is not modeled either.

**Arbitration thirds, with n (`tests/tools/arb_terciles.py`).** Calibration is on the 83 held-out seasons (28
players), not the 75 real salaries in the shadow. By the model's prediction: 27, 28, 28 seasons (18, 20, 20
players); -51% (95%: -62% to -33%), -25% (-39% to -7%), -7% (-19% to +14%). **The top third cannot be told from
zero**, so "low in every third" is corrected to "low in the bottom two thirds". By actual salary: +12% (-12% to
+47%), -19% (-42% to +14%), -23% (-32% to -10%). Twenty players per third is too few to pin the top third.

**Baseball-Reference.** One fetcher, one request every 15 seconds, honoring Retry-After (the 429 at 16:29 UTC
asked for 2,101 seconds; the pull resumed at 17:05). Cross-checks come from MLB Trade Rumors, Spotrac, AP.

Root causes found Nov 11: 13 (proration by stint rows, same-club re-sign added), 5 in rules written that day.

## 15. Round 12 (Nov 11, 12:30 PM): while the full salary pull runs

**Order of record.** Pre-registration `docs/prereg-round12.md`, commit d4be855 at 17:30:34 UTC, written before any
row of the 344-player pull (started 17:22:46 UTC) was read. It fixes what counts as a valid salary row (season,
dollars, a club he played for that season, not below that season's minimum, larger of two rows) and how the 11
players whose MLBAM link lands on a minor-league page are checked (salary-row clubs must match his own stints in
every priced season; 5 of them, seed 20261124, against Spotrac or Cot's). Both apply when the pull is read.
The random-40 seed (20261122) was named in be53af2 before the draw (section 14 corrected).

**Closures by the release / free-agency rule: a census, then a second sample.**
- Census (`tests/tools/resign_census.mjs`): of the 147 trades this rule closes, **11 close only because a player
  was released or non-tendered and re-signed by the club holding him within 60 days**; with those pairs removed
  they read OPEN: 2017 NYY/TEX, 2018 ATH/TB/TEX, 2019 CIN/NYY/SEA, 2022 MIN/NYY/TEX, 2023 ATL/TEX (Eli White),
  2023 STL/TOR (Robberse), 2023 CWS/NYY (Carela), 2023 MIA/PIT (Muñoz), 2025 LAD/STL, 2026 SF/TOR, 2026 LAD/TOR.
  The "club holding him" is the club at the time of the release, so flips count (Muñoz was re-signed by
  Cincinnati after two claims).
- Second seeded 15 (seed 20261123, round 11's 15 excluded): 3 wrong (Henriquez, Sanmartin, Muñoz), all of this
  kind. With round 11: **4 of 30, 13% (95% interval 5% to 30%)**, and every error found is in the census. So the
  11 are the bulk of it; the census is the number to fix against.

**Arbitration bias: dollars or percent, and flips at the bound** (`tests/tools/arb_bound.py`). Per third of the
model's prediction (27, 28, 28 seasons): model $1.29M vs paid $2.61M (-$1.32M a season, -51%); $2.72M vs $3.64M
(-$0.92M, -25%); $9.07M vs $9.78M (-$0.71M, -7%). The shortfall is close to a flat $0.7M to $1.3M a season, so
the bias is better read as dollars than percent. Rerun with a fixed ratio per third:
- at the point estimates: 74 sides move a win or more, 5 flips, 4 top or bottom 25 changes, 4 clubs move 2+;
- at the end of each 95% interval nearest zero (-33%, -7%, 0%): **0 sides move a win, 0 flips**, 2 top or bottom
  25 changes, no club moves 2+.
So no public trade grade flips at the least bias the data allow; flips depend on the point estimate. The earlier
sensitivity median (286 sides, 50 flips) came from per-season random ratios, which add spread; the fixed-ratio
run is the fairer test of the bias alone.

**One assumption in the $0 rerun: a salary row is money paid for playing that season.** Pre-registered test:
covered seasons whose row is under 40% of the season before. Only 3 rows qualify (2 player-seasons), not the 5
planned. Canha 2025 $1.4M is his real salary (MLB Trade Rumors, Spotrac): holds. Kittredge 2026 $1.0M is the
buyout; Baltimore paid $9M: fails. 1 of 2 fails, so buyout rows can understate a season. In this population it
is rare (3 of 147 covered seasons by this test, one player) and it errs toward too small a charge.

**Resume point for the pull (item 6).** Checkpointed per player in memory only: the worker stores each player in
the tab as it lands and skips players already stored, so a stall or a 429 resumes at the next player. **If the
tab closes, what has not been exported is lost**; the durable checkpoint is the fixture file (the first 61 players
plus the random 40). The 19:30 UTC check exports whatever has landed, done or not, so the fixture becomes the
resume point.

## 16. Round 13 (Nov 11, 12:50 PM)

Headings in this file carry the time each round was requested (ET), not commit times. Every commit cited below is
quoted with its GitHub time. Pre-registration for this round: `docs/prereg-round13.md`, bbdcebe at 17:54:29 UTC.
What ran before it is listed in that file (the re-sign rule's steps 1 to 4, and the suites started).

**142 or 147.** 142 was round 7's difference of two totals (849 OPEN before the release rule, 707 after) from an
earlier counting harness. Counted directly (each trade read OPEN with the feed hidden from the rule, CLOSED with
it), the rule closes 147 on today's working page, on the live page, and on the page as deployed at 203a5e3 (the
commit that added the rule). 147 stands; 142 is withdrawn.

**The 11 on the site.** All 11 trades show a grade (trade grades never read OPEN, section 11) and a CLOSED status
on the player tree and in the trade rows. With the fix, status turns OPEN and the UNSETTLED chip appears; no grade
on the page changes. The engine ends the same windows at the release, so two grades also miss value after the
re-sign (rough, player WAR after the re-sign inside six seasons, before salary): Henriquez on the 2022 MIN side
(-1.2 shown, about +2.0 missing) and Eli White on the 2023 ATL side (-0.1 shown, about +1.8 missing). Both would
flip sign if the engine is fixed too. The other nine pieces have 0.0 to 0.2 after the re-sign.

**The fix and the checklist (not deployed; `docs/patches/resign-keeps-open.diff`).**
1. Rule: a release or free-agent filing followed within 60 days by a *minor-league* re-sign with the club that
   held him does not end his window; a major-league re-sign is a new signing and still ends it. Engine
   counterpart: none; `asset_rules.trade_window` ends the window at the release. The page and the engine disagree
   until the engine gets the same rule.
2. Tests first: `sameClubResignKeepsOpen` (Eli White 2023 OPEN) failed on the current page and passes with the
   rule; `otherClosuresStayClosed` (Germán 2014, Kilian 2021) passes on both.
3. Full count: OPEN trades 710 to 721; exactly the 11 of the census reopen; none close.
4. Changed items checked outside our data: the 11 rest on 8 players' release-and-re-sign events, all 8 confirmed
   (MLB.com, MiLB.com, MLB Trade Rumors, Wikipedia, RotoWire): White, Henriquez, Sanmartin, Robberse, Carela,
   Muñoz, Loutos, Fitzgerald. 8 of 8 right.
5. Unchanged items: the 26 closures in the two samples that are not in the census were all checked in rounds 11
   and 12; all 26 labels right.
6. Planted case: `sameClubResignKeepsOpen` fails on the page without the rule.
7. All 14 suites pass on the working page with the rule, including `t_grades` (0 grades moved).
8. Not run: no deploy.

**Arbitration: dollars or percent, out of sample** (`tests/tools/arb_oos.py`). Only 7 of the 83 seasons fall in
2018-2020 (2, 2 and 3 per third), so the pre-registered test is underpowered and no claim is made. For the
record, on the 76 test seasons: current model median miss $1.44M (total -17%), percent factor $1.82M (+26%),
dollar offset $1.70M (+19%); both corrections fit on 7 seasons do worse than no correction. The "flat dollars"
reading in section 15 is withdrawn as a claim; it describes the 83 in sample only. **83 vs 75:** the 83 are the
calibration sample (seasons drawn from 40 random arbitration players); the 75 are the seasons of the trade
shadow's 5,245 that have a real salary on file. Different sets for different jobs.

**Salary rows that may not be pay for playing** (`tests/tools/salary_row_sweep.py`, 518 rows, 90 players):
two rows in one season 12; under 40% of the prior season 14; a season with no major-league stint 21; a common
buyout amount ending a run 13. 48 rows (9%) hit at least one rule, 9 hit two. In the $0 population: 12 rows, 4
above the minimum: Kittredge 2026 $1.0M (buyout; wrong), Canha 2025 $1.4M (real), Chris Martin 2022 $2.5M (a
one-year deal; real), Sandy León 2020 $2.0M (real, but see 2020 below). So far 1 of 4 is a buyout.

**New finding, not pre-registered: 2020.** The engine charges 2020 salaries at the full-season rate (dpw 2020 =
2019 = 8.0) while 2020 value is a 60-game season and 2020 pay was prorated (Montero 2020: a prorated $290,741 of
$785,000, AP). Trout's 2020 charge is 3.13 wins against 2.3 WAR. Re-charging every acquired 2020 trade season at
60/162 (`tests/tools/season2020_check.py`): 198 seasons, 33.5 wins of charge removed; 6 sides move a win or more, 0
flips, 1 club moves 2 places. Signing and extension grades that cover 2020 are not sized yet and are likely
larger.

**Pages that belong to another player.** Check over all 90 players with salary rows (salary seasons against
played seasons): 0 suspects. The 11 redirect players are checked when the pull lands.

**Timestamps against git.** Every commit time quoted in this file matches GitHub: ddc7026 16:01:26, be53af2
16:30:49, d4be855 17:30:34 (all UTC). Not checkable against git: "written locally at 15:18 UTC" (section 12, a
local file time; already labelled not provable) and run-log times (16:31:13, 16:29, 17:22:46, 17:05), which come
from command output, not commits. Section 14's earlier "draw at 17:05" was the one wrong time; corrected there.

Root causes found Nov 11: 15 (the same-club re-sign in the page rule, 2020 charged at full season), 5 in rules
written that day.

## 17. Ship block (Nov 11, 1:05 PM)

1. **Same-club re-sign keeps a trade OPEN: built and tested, not on the live site.** The working page carries the
   rule; `tests/t_nov11.mjs` now requires Eli White (2023), Robberse (2023), Carela (2023) and Muñoz (2023) to read
   OPEN (fails on the live page, passes on the build). Rebuilt with `engine/split_book.py`: only index.html changes
   (book.js 5efd14cbe3 and deals.js ef3f86b4e0 unchanged). OPEN trades 710 to 721; all 14 suites pass on the built
   page, t_grades with 0 grades moved. Committing index.html to main publishes it (GitHub Pages), which needs
   Sean's OK, so the change is in `docs/patches/resign-keeps-open.diff` (applies cleanly with `patch -p1`, tested).
2. **Arbitration correction: not shipped.** The pre-registered out-of-sample test (bbdcebe, section 16) is
   underpowered (7 training seasons) and both corrections did worse than the current model on 2021 and later.
   The old estimate stays, with a caveat added to the methodology list in the same build: the estimate runs low
   against salaries actually paid, and the correction is not applied.
3. **Scheduled refreshes.** The four "Ledger:" tasks have no computer attached, so their cloud runs cannot reach
   Chrome. Attaching one ("Require this computer") is a setting only Sean can turn on, in the Claude desktop app
   on his MacBook Air: open each task's settings and turn it on. Applied here: the contract-terms task's prompt now
   tells it to read the skill's reference files with the Read tool only (the Nov 11 run stalled on a permission
   prompt from `sed` on a symlinked file). A GitHub Action is not a fit for three of the four jobs (they need web
   research by Claude), and the share-page job would publish to the live site on a schedule, which needs Sean's
   OK; web upload also skips `.github`.
4. **Buyout and 2020 rows.** `tests/fixtures/salary_overrides.csv` replaces Kittredge 2026 ($1.0M buyout) with the
   $9.0M Baltimore paid; the $0 shadow now scales every 2020 salary row to 60/162 (2020 pay was prorated). Effect on
   the shadow (147 covered seasons): paid above the floor 110 to 108; sides moving a win or more 22 (unchanged);
   flips 6 to 8; clubs moving 2+ places 2 (unchanged). Report only, as before.

## 18. Round 15 (Nov 11, afternoon)

1. **2020 source.** BRef 2020 rows are full-season rates, not prorated pay: Heaney 4,300, Montero 785, Marte
   11,500, Leon 2,000 ($K). AP and Spotrac report the prorated amount, which equals full rate x 60/162 (Heaney
   $1,592,593 of $4.3M; Montero $290,741 of $785,000; Stassi $296,296 of $800,000; Bundy $1,851,852 of $5M).
   Counts: BRef 4 of 4 full rate; AP 4 of 4 prorated; Spotrac 1 of 1 prorated. So scaling BRef 2020 rows by 60/162
   (b894f07) shrinks once, not twice. Cot's was not fetched.
2. **Why OPEN 710 to 721 moved no grades.** Grades are precomputed in TRADE_BOOK (book.js). `folTradeOpen` only sets
   the OPEN label; no grade reads it. Eli White 2023 ATL/TEX: label closed to OPEN, seats ATL -0.1 / TEX +0.1
   unchanged. The grade moves only when the engine applies the same rule (item 5).
3. **Arbitration out-of-sample test: inconclusive.** Gain +0.29 $M a season, 95% -0.35 to +1.31, SE 0.41; smallest
   detectable gain at 80% power about $1.16M a season (`tests/tools/arb_oos_power.py`). A better-powered design is
   pre-registered in `docs/prereg-round14.md` (dff5ab9, 18:35:21 UTC; leave one player out, 200+ seasons, adopt only if the interval
   excludes 0 and gain is at least $0.25M). Not run.
4. **Flips 6 to 8.** The two new flips are both sides of the 2025-07-31 CHC/BAL deal (CHC +0.5 to -0.14, BAL -0.5 to
   +0.14), caused by the Kittredge 2026 $9.0M override charged to the club holding him under flip-follows-piece.
   Shadow only; that deal shows on club and tree pages, it has no share page.
5. **Builds (local, not deployed).**
   - Engine re-sign rule: `docs/patches/engine-resign-rule.diff`. A release or FA filing followed within 60 days
     by a minor-league re-sign with the club that held him no longer ends the asset. Check
     (`tests/tools/engine_resign_check.py`): 36 pieces, 72 sides. Henriquez 2022 MIN -1.2 to +0.3; Eli White 2023
     ATL -0.1 to +1.1. Largest club moves: NYY 2014-12-19 -7.3 to -4.9 (Germán), BOS 2010-11-12 +3.22, MIA
     2007-12-04 +1.03.
   - Home first, slow panels after: built, measured, no gain, reverted. Kept as
     `docs/patches/home-first-not-shipped.diff`.
6. **Assumption test (rows flagged by the buyout/option sweep).** 20 rows, seed 20261127, each checked against a
   second source (`tests/tools/salary_spotcheck_r15.json`). Wrong 7 of 20 = 35% (Wilson 95% 18% to 57%). Wrong by
   $250K or more: 4 of 20 = 20% (8% to 42%): Bautista ATL 2018, LeBlanc 2020, Shreve 2019, Diaz 2023. Three more are
   $100K rows for seasons spent only in the minors (Swarzak 2020, Sanchez 2023, Heineman 2021). Conclusion: flagged
   rows cannot be trusted as filed; the 19:30 UTC pull plus the valid-row rules is the fix path.

## 19. Round 16 (Nov 11, 2:19 PM): sizing the salary-row problem

1. **What the flag catches.** The flagged population is 48 of 518 Baseball-Reference salary rows (90 players) in the
   two Nov 11 fixtures, flagged by `tests/tools/salary_row_sweep.py`: two rows in one season (12), under 40% of the
   prior season (14), no major-league stint that season (21), a common buyout amount ending a run (13); 9 rows hit
   two rules. Errors in the 20-row sample by rule: two rows in a season 3 of 4, no stint 4 of 9, buyout amount 1 of
   5, under 40% 0 of 6. So the flag mostly catches split seasons and placeholder rows, not buyouts.
   - 35% (18% to 57%) of 48 is about 17 wrong rows (9 to 27). Superseded by the weighted estimate in section 20.
   - **Grade exposure: none live.** Baseball-Reference rows feed only the two shadow runs; live grades use the
     contract book and the arbitration model, so no live grade and no share page reads them. In the $0 shadow, 12
     of the 48 rows sit in priced seasons. Bounds (`tests/tools/flag_bounds.py`): every one at $0 charge, 0 sides
     move 0.5 or more; every one at the player's prior-season salary (an extreme case: Bautista $18M, Canha
     $11.5M, both rows verified as right), 4 sides move 0.5 or more on 2 trades (2025-03-22 KC/MIL, 2018-08-28
     NYM/PHI), 3 flips.
2. **The four large errors, fixed in `tests/fixtures/salary_overrides.csv`.** Bautista 2018 $1.0M (Atlanta rate;
   AP and MLB.com), LeBlanc 2020 $0.8M (MLB Trade Rumors, MLB.com; the shadow scales 2020), Shreve 2019 $0.9M (MLB
   Trade Rumors). Rerun on all 147 covered seasons: paid above the floor 108 to 109; sides moving a win or more 22,
   flips 8, clubs moving 2+ places 2, all unchanged. The 8 flips (unchanged from section 17): 2015-11-12 SEA/SD,
   2016-12-01 ATL/STL, 2022-11-18 LAA/MIN, 2025-07-31 CHC/BAL. None has a share page (winter pages are keyed to
   the winter's start year: 2016-stl, 2015-sea, 2022-min and the others are not in share.json), and the shadow is
   not live.
   - **Diaz 2023 $21.25M: traced, not fixed.** It is Baseball-Reference's own figure, copied verbatim into
     `tests/fixtures/arb_br_2026-11-11.txt` with 2024 also $21.25M and 2025 $21.5M. No outside source matches
     (Spotrac 2023 cash $23.75M with the signing bonus, AAV $20.4M, tax figure about $18.6M after deferrals). It most
     likely mixes deferred money and a share of the bonus. Corrected in section 20: MLB Trade Rumors lists $21.25MM
     for Diaz among the Mets' 2024 commitments, so the figure does have an outside source. No effect: 2023 sits inside his contract, so neither
     shadow prices it. Left as is and labelled.
3. **Rule for rows below the season minimum.** A row below that season's major-league minimum is never a
   major-league salary: drop it. If the season has another valid row, use it; if the player had major-league
   time, charge the minimum; if not, charge nothing. This is rule A4 of d4be855. It touches 31 of 518 rows (6%): 24
   with a major-league stint, 7 without. Effect on grades: none (both shadows already charge nothing below the
   $0.75M floor). Known gap: Walker 2020's only row is $100K, so the rule charges the minimum where he was owed $2M.
4. **19:30 UTC pull.** Not landed when this section was written; reported separately when it does.
5. **Baseball-Reference stores the full 2020 rate: 9 of 10 (60% to 98%), post hoc.** Seed 20261129, named at the draw, not
   committed before it, so this result is exploratory; the pre-registered check is in section 20 (`tests/tools/season2020_spotcheck_r16.json`). Holds for a mid-2020 trade (Marte) and an
   extension (Merrifield). Fails for Walker (a $100K placeholder). **New finding:** Price's row is the right rate,
   but he opted out and was paid $0, so the 60/162 step charges about $11.85M never paid. Opt-outs are not in
   the shadow population, and the live engine already charges Price's 2020 season $0 (`asset_rules.contract_cost`).
6. **Ship mode, checklist item 5 sized** (`tests/tools/season2020_signings.py`): free-agent grades covering 2020
   are charged too much for that season (a full-season charge against 60 games of value), so today's grades for
   those signings are too low. Fixing it raises 179 signings, 93 by half a win or more, 21 by a win or
   more (102.5 wins in all); 87 extensions, 46 by half a win, 14 by a win (60.3 wins, approximate: extensions use
   another formula). Largest: Cole NYY +2.9, Rendon LAA +2.9, Strasburg WSH +2.9. Public winter pages it would
   change: 2019-wsh +5.4, 2019-laa +3.7, 2019-phi +2.5, 2015-det +1.8, 2017-stl +1.3, 2014-wsh +1.1, 2017-mil +0.7,
   2013-tex +0.6 (corrected in section 21: this list mixed in extensions). Not built into the live page: Sean's call.

## 20. Round 17 (Nov 11, 2:39 PM)

1. **Item 5 direction, checked.** The engine charges every season of a signing at the full-season rate, 2020
   included, while 2020 value is 60 games, so today's grades for contracts covering 2020 are too low and the fix
   raises them. Section 19 had the direction right; its wording is clarified. Cole (NYY, 9 years, $324M; page now:
   18.3 wins realized, 20.2 expected, -1.9): 2020 charged on $35.25M above the minimum (full rate), 4.67 wins in
   the free-agent formula; prorated, $13.06M and 1.73 wins. Change +2.9 wins, so about -1.9 to +1.0 on the page's
   numbers. (Reproducing his grade from contract_book.json gives -0.9 against the page's -1.9; the 2020 change is
   the same either way.) The share-page list in section 19 stands: those winter grades rise.
2. **Flagged rows, weighted by category.** The four flag rules overlap (60 rule hits on 48 rows), so the naive sum
   12 x 3/4 + 21 x 4/9 + 13 x 1/5 + 14 x 0/6 = 20.9 counts 12 rows twice. Each row assigned to one category
   (order: two rows in a season, no stint, buyout amount, under 40%; the sample error rates set the order):
   populations 12, 21, 7, 8; sampled 4, 9, 3, 4; wrong 3, 4, 0, 0. Point estimate **18.3 wrong of 48**; with a
   Jeffreys prior per category and the unsampled rows drawn from it, **median 19, 95% 12 to 25 (25% to 52%)**.
3. **2020 full rate, pre-registered** (`docs/prereg-round16.md`, 0af4595 at 19:41:31 UTC; draw 19:41:43 UTC).
   Only 9 rows in the fixtures fit "traded in 2020 or $600K or less", so all 9: **2 of 9 pass (6% to 55%)**. All 7
   fails are placeholder rows below the season minimum ($100K, $450K): LeBlanc twice, Kratz, Swarzak, Justin Miller,
   Culberson, Shreve. Both real rows pass, including two players traded on Aug 31 (Maybin $1.5M, Hedges $3M). So:
   real 2020 rows are full rate (11 of 11 across both checks); placeholder rows are not salaries, and rule A4 drops
   them.
4. **19:30 pull: did not land.** Its scheduled check fired at 19:30:47 UTC; reading the Baseball-Reference tab was
   refused by the permission system (consistent with the standing instruction to leave that tab alone), so
   nothing was exported: the fixture is unchanged (62 lines, first 61 players plus the random 40). The rows,
   rejects by rule and the five cross-checks cannot be reported until the tab is read or the pull is rerun.
   **Cloud refresh: not fixed.** rumors.json and wire.json still read checked 07:51 UTC; the four Ledger tasks fired
   at 13:05, 13:22, 13:41 and 13:57 UTC with no bound computer and wrote nothing. Needs "Require this computer".
5. **Walker 2020 fixed** in `tests/fixtures/salary_overrides.csv`: $2.0M, the minor league deal's major-league
   salary (NBC Sports Philadelphia: $740,000 on the 60-game proration). Shadow rerun: unchanged (147 covered, 109 above
   the floor, 22 sides, 8 flips); Walker 2020 is not a priced season in the shadow population (only his 2016 is).
6. **Large rows, pre-registered** (same file; seed 20261131, 20 of 70 rows of $15M or more). **3 of 20 mismatch by
   more than $500K (5% to 36%)**: Diaz 2023 and 2024 ($21.25M against Spotrac's $11.75M base, $14.15M payroll and
   $19.65M total), and Donaldson 2022 ($21.75M against a $21M salary). Diaz is not the only one. Two matches
   carry notes: Suarez 2027 is an unexercised $16M mutual option, and Bichette 2026 matches cash ($2M salary plus
   the $40M bonus paid that March) but not a bonus spread over the deal. `tests/tools/prereg16_results.json`.
7. **Ship mode.** Launch items blocked only by my work: item 5 (build the fix), item 9 (the pull: blocked by the tab
   permission), item 6 (engine re-sign: built, waits on item 1). Did item 5: `docs/patches/season2020-charge.diff`
   scales 2020 by 60/162 in `fa_grade.py` (cost, expected, per-season increments) and `ext_grade.py` (`wins_of`).
   Checked on Cole (above). Full regrade not run here: ledger.sqlite in this workspace lacks the `sweep_tx` table
   that fa_grade.py reads. Applying it is Sean's call.

## 21. Round 18 (Nov 11, 2:58 PM)

1. **Item 5, exact.** Rebuilt the engine's `sweep_tx` table from the public MLB transactions feed
   (`tests/tools/sweep_tx_build.py`, 235,830 rows, 1997-2026) and ran `fa_grade.py` before and after
   `docs/patches/season2020-charge.diff`. The rerun reproduces 646 of 646 overlapping published signing grades
   to the tenth (it covers 646 of the 2,616 card rows). **Cole, before: $36M salary, $35.25M above the minimum
   charged for 2020 in full, 1.22 WAR in 2020, 18.3 realized against 20.2 expected, -1.9. After: 2020 charged on
   $13.06M, expected 17.3, +1.0.** Sign: today's grades are too low; the fix raises them. In the 646: 42 grades
   change, all up; 30 by half a win or more, 6 by a win or more; 6 flip from minus to plus (Cole, Ryu, Treinen,
   Calhoun, Kelly, Guerra). `tests/tools/fa2020_exact_r17.json`.
2. **Public pages, corrected.** Section 19's list counted extensions by their start year as winter moves.
   Signings only, on winter pages in share.json: 2019-wsh +4.8 (Strasburg, Harris, Thames, Kendrick, Castro),
   2019-laa +3.5 (Rendon, Teheran), 2019-phi +1.6 (Wheeler), 2014-wsh +1.1 (Scherzer), 2015-det +0.7
   (Zimmermann), 2017-mil +0.7 (Cain), 2013-tex +0.6 (Choo). 2017-stl drops out: none of its signings ran
   through 2020. These seven come from the free-agent formula (the rerun does not cover those clubs' rows); none
   is applied to the site.
3. **Donaldson 2022 rescored.** The AP terms give a $3M signing bonus, an $18M salary in 2020 and $21M in
   2021-23, so the $21.75M row is $21M plus a quarter of the bonus: a match under the pre-registered rule. Large
   rows: **2 of 20 mismatch (3% to 30%), both Diaz.**
4. **Primary sources for the 20 large rows** (AP, a club announcement or MLB.com with the season figure; Cot's
   pages answer with a bot block, so none came from Cot's): 15 of 20 have one (Hamels 2016 and 2020, Price 2021,
   Donaldson 2017, 2019 and 2022, Suarez 2025 and 2027, Bryant 2021 and 2025, Bassitt 2024, Happ 2025 and 2026,
   Bichette 2026, Skubal 2026). Happ's AP story dates the salaries a year late ($20M 2025-26, $18M 2027) against
   MLB Trade Rumors ($20M 2024-25, $18M 2026); the rows follow MLB Trade Rumors. **No primary source found: Marte
   2023 and 2024, Rodon 2025 (reports and Spotrac only), Diaz 2023 and 2024 (Spotrac and MLB Trade Rumors, which
   lists $21.25MM for 2024).** So Diaz is not the only row without one.
5. **Top launch item without the pull: done.** Item 5's fix is built and, for the free-agent rows the rerun
   covers, regraded exactly (above). Still open for it: extension grades (`ext_grade.py` needs more of the
   ledger than `sweep_tx`) and Sean's OK to apply it.

## 22. Round 18 follow-up (Nov 11, 3:07 PM)

1. **How many signings have a 2020 season.** The 646 in section 21 were current regimes only. All graded
   free-agent rows (current plus archive): 1,717, of which 1,716 on-page rows the rerun reproduces exactly. **174
   have a 2020 season: 162 change, 12 do not.** Why the 12 do not: 11 have an AAV of $1.0M or less, so the 2020
   cost moves at most about $0.16M above the minimum and the grade change rounds away under 0.05 (Hechavarria,
   Maile, Riddle, Osich, M. Hernandez, Plawecki, Souza, Jeffress, Y. Garcia, Hunter, Hahn). The 12th is Price,
   whose 2020 share is 0 (he opted out). `tests/tools/r18_results.json`.
2. **Winter pages, exact.** Rebuilt the winter table (`offseasons_build.py`) from the before and after reruns.
   It reproduces the published FA column for 548 of 816 winters (the rest hold rows the rerun does not cover).
   **Exact deltas on the seven public pages: 2019-wsh +5.3 (FA -22.7 to -17.4), 2019-laa +3.8 (FA -18.4 to -14.6,
   total -20.6 to -16.8), 2019-phi +2.4, 2014-wsh +1.1, 2017-mil +0.8, 2015-det +0.6, 2013-tex +0.5.** Section
   21's estimates were low on the first three. 71 winters change in all. Local only, nothing applied.
3. **2020 filler rows.** The 7 failures in the 2020 sample are the whole population: exactly 7 player-seasons
   carry a $100K or $450K 2020 row. They should hold: LeBlanc $800K, Kratz $1M, Culberson $1M, Shreve $575K,
   Walker $2M; Swarzak and J. Miller had no MLB salary that year. Exposure: the $0 population includes LeBlanc
   2020 and Kratz 2020 (both now overridden, Kratz added this round); the arbitration shadow includes none; no
   graded deal reads these rows. **Rule (FILLER): a row under that season's minimum is raised to the minimum if
   the player had an MLB stint that season, else dropped.** Applied in the local shadow only: unchanged, 22
   sides, 8 flips, same list. Engine change is Sean's call.
4. **Field-level check, pre-registered** (`docs/prereg-round18.md`, d8f8910, committed before the draw; draw
   e3695ab, seed 20261132, 25 of 1,717 rows, drawn 20:11:20 UTC). Sign date against the MLB feed: **25 of 25**
   (0 mismatches, Wilson 95% 0% to 13%). Team: **25 of 25** (0% to 13%). Years and total against AP, club or
   MLB.com, Spotrac as fallback: **24 of 25 (1 mismatch, 4%, 0.7% to 19.5%): Heim ATL 2026, card $1.5M, AP and
   MLB.com $1.25M.** Later reports give $1.5M, probably base plus a bonus; under the pre-registered order AP wins.
   Six rows had no AP or club figure (Lewis, Hart, Arguelles, Almonte, Winker, Brogdon) and matched on the
   fallback. `tests/tools/prereg18_results.json`.
5. **Large rows.** Primary sources found: **Marte 2023 and 2024** (AP: $14.5M in 2022, $19.5M in each of 2023 to
   2025, $5M signing bonus; the row adds $5M over 4 years) and **Rodon 2025** (AP: $5M bonus, $22M in 2023, $27M
   after; the row adds $5M over 6 years). **Diaz 2023 and 2024: flagged unsourced** in
   `tests/tools/prereg16_results.json` and `tests/tools/salary_spotcheck_r15.json`, the only files that show them
   (no public page shows season salary rows). AP gives a $17.25M salary in both years plus a $12M bonus; $21.25M is
   $17.25M plus $12M over 3 years, a split no source states. Over 5 years, as for Marte and Rodon, it is $19.65M.
6. **Dependency check, re-run** after the Walker and Kratz overrides and the traded-row category: **0** engine,
   page or tool files outside `tests/` read the fixtures, so **0** live grades touch the 48 flagged rows. 12 of the
   42 flagged player-seasons are priced live by the contract book's own figure, not the fixture.

Open with Sean: deploy, the 2020 fix, the FILLER rule in the engine, the BRef pull.

## 23. Round 19 (Nov 11, 3:58 PM)

1. **The 268 winters.** The live site is a faithful build: the shipped engine outputs rebuild `offseasons.json`
   byte for byte (816 of 816). The gap was my rerun's input, not the site. The `sweep_tx` table I rebuilt
   (section 21) skipped `ingest/retro_backfill.py`, which production runs after the feed; the MLB feed is nearly
   empty before 2009 (14 transactions for the whole 2003-04 winter). Causes: **data version 268, code version 0,
   rounding 0, other 0.** 68 winters (all 1998-2008) were missing and 200 (all 1998-2008) had lost every signing.
   Largest gaps: 2001-tex (Hart) -21.1, 1998-bal (Wren) -16.5, 2000-col (O'Dowd) -14.2, 2004-nyy (Cashman)
   -13.8, 1998-lad (Malone) -13.5. **With the backfill applied, the before-fix rebuild matches the free-agent
   column on 816 of 816 winters** (813 whole rows; the other 3 differ only in which equal-grade move is listed, or
   a Retrosheet date: Dreifort Dec 11 against Dec 19). The 2020 deltas in section 22 are unchanged, now measured
   against a baseline that rebuilds exactly. What would show the live site wrong instead: an input that differs
   from its documented source. The rebuild reads the same files, so it cannot test those; the field checks do.
   `tests/tools/sweep_tx_build.py` now says to run the backfill.
2. **Heim: disputed.** AP and MLB.com: $1.25M. The card's $1.5M comes from `engine/contracts_recent.py`, which
   credits MLB Trade Rumors; Field Level Media and The Big Lead repeat $1.5M in May. No amendment or bonus
   breakdown found, so the final figure is not established. Labelled disputed in
   `tests/tools/prereg18_results.json`. Grade effect under 0.05 either way.
3. **Signing bonuses.** The contract book has no bonus field: all 3,608 contracts store a total. Free-agent grades
   charge total over years every season (3,608 of 3,608); extensions spread the total along the service path
   (`asset_rules.ext_salary`). So live grades use one method per contract kind. The spreading choices seen are in
   Baseball-Reference season rows only: Marte, Rodon, Donaldson over all years; Diaz over 3 (his opt-out followed
   year 3); Bichette in the year paid. All five sit inside contract-book deals, which neither shadow prices: **grade
   change 0 under any single method.** Counting every bonus-bearing contract needs a per-contract bonus source
   (Spotrac; Cot's blocks bots). Method left for Sean.
4. **Exposure on the full population** (2,616 graded signings, the published count; the 1,717 was the incomplete
   rerun). Still 162 grade changes (174 with a 2020 season); no 1998-2008 signing reaches 2020. Public pages: the
   same 7 winter pages; the 19 move pages are November 2026 moves and the 30 club pages show the current winter,
   so **0 more. The 7-page table is complete.**
5. **Field-check frame: the assumption fails another way.** The frame was all 1,717 rows (1,717 unique; the seed
   reproduces the draw), and rows without an outside source were not excluded. But the 1,717 came from the rerun
   without the backfill, so **899 graded rows from 1998-2008 (34% of 2,616) could not be drawn**, including every
   contract whose terms come from the `fa97` source (714). Retrosheet dates are a small risk (4 of 7,021 signings
   have no day). A supplementary pre-registered draw from those rows is the fix.
6. **Done: the 2020 fix for extensions, exact.** Section 21 said `ext_grade.py` needed more of the ledger than
   `sweep_tx`; wrong, it needs only the name map, which the backfilled table supplies. In a sandbox (repo
   `asset_rules.py`, so without the unreleased re-sign rule; `/work` outputs untouched, checked by checksum), the
   before-fix pass reproduces **806 of 806 extension rows and 152 of 152 regime totals**. With the fix:
   - extensions covering 2020: 75 change, 61 up, 42 by half a win, 20 by a win or more, 3 flips, +47.1 in all
     (Arenado -5.6 to -2.0, Trout -2.7 to -0.3, Altuve +1.1 to +3.3, Goldschmidt +5.5 to +7.4);
   - 304 others move (max 1.0; 8 by half a win, 2 by a win, 3 flips, -43.5 in all) because each class's typical
     rate is recomputed on the population (veteran 0.370 to 0.392, arbitration 0.167 to 0.180), so lifting 2020
     deals lowers the rest of the class. That side effect is a design choice for Sean.
   No share page shows extension grades. `tests/tools/r19_results.json`. The free-agent and extension halves of
   checklist item 5 are now both regraded exactly; applying them is Sean's call.

## 24. Round 20 (Nov 11, 4:18 PM)

Correction to section 23, item 6: my 2020 span rule misread two deals (Molina 2017, Braun 2011). Corrected
counts: **77 extensions covering 2020 change (+48.8 in all), 302 others move (-45.2)**, not 75 and 304.

1. **The 3 rows of 816 that differ, and determinism.** With the backfill, against live:
   - 2000-01 Dodgers (Malone): Dreifort's signing date. The MLB feed says Dec 19, Retrosheet says Dec 11
     (`20001211`, transaction 14110, `dreid001`, `LAN`). Live shows Dec 11; my rebuild took the feed row.
   - 2010-11 Mets (Alderson): tie at 0.0. Live lists Capuano, the rebuild lists Buchholz.
   - 2016-17 Marlins (Hill): tie at -0.4. Live lists Ellis, the rebuild lists McGowan.
   None is a public winter. **Shuffle test** (input table shuffled twice, rebuilt twice): with the shipped code the
   two builds differ from each other and from live (free-agent column matches live on 766 and 779 winters, one
   winter drops out, 31 to 37 dates and 7 grades change), because `fa_grade.priced()` reads rows with no ORDER BY
   and back-to-back re-signings can swap contracts. With an ORDER BY the two shuffles give identical files.
   A second source of order dependence turned up: winter totals are float sums, so add order can move a rounded
   cell. STL 2004-05 dollars are exactly $15.5M; live rounds to 15, an ORDER BY build to 16. Exact sums fix
   that. Patch: `docs/patches/deterministic-order.diff` (ORDER BY date, person, transaction id; `math.fsum` for
   the winter sums; tied moves keep their add order, which is now fixed). Result: both shuffles byte-identical
   (md5 `1a4a4a5e`), 803 of 816 rows equal live; 12 differ only in moves tied on size (8 same moves in another order,
   4 a different tied move, one of them +0.1 against -0.1), 1 in that rounding cell; **0 public winters change**. I also tried an explicit tie-break key (date, kind, player):
   also deterministic, but it changes 75 move lists, 19 of them public, so I do not recommend it. Applying the
   patch is Sean's call.
2. **The group-rate recompute is shipped code**, not my sandbox: `engine/ext_grade.py` lines 160-163 build
   `CLASS_RATE` from every evaluated extension, and lines 172-175 apply it; the repo and `/work` copies are
   identical. The 2020 fix two ways (list only; the choice is Sean's):

   | | Deals covering 2020 | Other extensions |
   |---|---|---|
   | (a) As built (rates recomputed) | 77 change, 63 up, 44 by half a win, 21 by a win, 4 flips, +48.8 | 302 change, 6 by half a win, 1 by a win, 2 flips, -45.2 |
   | (b) Rates held at pre-fix values | 74 change, 69 up, 44 by half a win, 25 by a win, 5 flips, +58.2 | 0 change |

3. **Supplementary field check, 1998-2008.** Pre-registered at `a94dd4b` (rules) with frame and draw script at
   `6db694c`, committed before the draw. Seed 20261134; 899 rows (fa97 674, espn 225; Dreifort excluded as already
   examined); n = 20 fa97 + 5 espn, weighted toward fa97 because that source had never been drawn. Results in
   `tests/tools/prereg20_results.json`. Club 25 of 25 and Retrosheet date 25 of 25 exact.

   | fa97 (n=20) | match | mismatch | unverified | pass bar (at most 1 and 2) |
   |---|---|---|---|---|
   | Club | 20 | 0 | 0 | pass |
   | Date (outside report) | 18 | 1 (O. Hernandez: AP agreement Dec 22, row Jan 3) | 1 (Dessens) | pass |
   | Years | 17 | 0 | 3 | **fail** |
   | Total | 15 | 1 (Fassero: Spotrac $1.35M, card $1.5M) | 4 | **fail** |

   **fa97 fails the pre-registered bar on years and total**, on sourcing coverage: Conine, Hermanson, Dessens and
   Alfonseca have no listed source for terms (only unlisted salary sites or blogs; AP says Alfonseca's terms were
   not disclosed). Among verified totals the mismatch rate is 1 of 16 (95% interval 1% to 28%). espn (n=5): one
   total mismatch, Furcal, card $30M against AP's $33M guaranteed including the $3M buyout (interval 4% to 62%).
   Notes on judgment calls, kept visible in the results file: R. Alomar scored a match on SI's 4/$32M (AP said
   $30M to $32M; a later MLB.com piece says 3/$21.9M); Vizcaino and Floyd rest on ESPN text quoted secondhand.
   Furcal and Fassero are candidates for `salary_overrides.csv`; the bar failure is a finding, not something to fix
   by widening sources after the fact.
4. **Assumption about `retro_backfill.py`: it does not double-count a signing that is also in the MLB feed.**
   Count: 7 same player and club signings within 60 days appear in both sources (3 same day, 4 on different
   dates, 2 to 32 days apart). Graded twice: **0** (Dreifort and Holmes are graded once; the 2 pairs that do appear
   twice, in SD 2008-09 and DET 2008-09, have no terms and carry no grade). Also 0 Retrosheet signings lack an MLB
   id. The date dispute in item 1 comes from this seam: where both sources exist, the feed date can win.
5. **What would prove rebuild-matches-live wrong, other than bad inputs:**
   - **Shared code.** The rebuild runs the same engine on the same intermediate outputs, so a byte match shows the
     site is reproducible, not that the grades are right. A bug reproduces itself. Only an independent
     recomputation of grades from raw WAR and terms tests this; not yet run.
   - **Order luck.** The match held for the row order production happened to have; the shuffle test shows another
     order gives different contracts and dates. Shown above; the patch closes it.
   - **Float order.** Rounded sums can flip with add order (STL 2004-05). Shown above; same patch.
   - **The served file is not this file.** Checked: the live `offseasons.json` from frontofficeledger.com, the raw
     GitHub copy and the repo copy share one md5 (`6842d1d0`), and the page reads the values without recomputing
     them. Not the cause.
   - **A different Retrosheet archive in production.** The 813 whole-row match makes a different archive
     unlikely, but production's archive version is not recorded anywhere. Worth stamping in the build.

Nothing went to the public site. Still with Sean: deploy, the 2020 fix and the rate choice in item 2, the filler
rule, the Baseball-Reference pull, the bonus method, and now the determinism patch.

## 25. Round 20 repost (Nov 11, 4:59 PM)

1. **Five-way shuffle.** `sweep_tx` rows shuffled 5 times (seeds 20261141 to 20261145), each rebuilt three ways.
   Shipped code: 5 different files; whole rows equal to live 699 to 733 of 816, FA columns 745 to 775, move
   lists 69 to 91 differ, 1 winter missing in 3 of 5 runs, 55 to 88 FA listing rows differ. ORDER BY only: 5
   identical files, 803 of 816 rows equal live, 0 graded rows differ (the 10 listing rows that differ carry no
   grade: two Retrosheet/feed duplicates, Dreifort and Holmes, and 8 feed rows newer or older than production's
   snapshot). ORDER BY plus exact sums (the patch): 5 identical files, md5 `1a4a4a5e`, same counts. Note: feed
   rows have no `tx_id` (NULL), so ties after date and person are broken only for Retrosheet rows; that is
   harmless because `priced()` already keeps the first row per date and person. `tests/tools/r20_repost_results.json`.
2. Unchanged from section 24.
3. Unchanged from section 24: pre-registered at `a94dd4b` (21:22:08 UTC), drawn 21:22:20 UTC; fa97 fails on
   years and total (unverified counts), passes on club and date.
4. **Id-map join.** All 562 player ids on the 900 graded signings dated before 2009 (899 plus Dreifort) come
   through the Retrosheet-to-MLBAM join (4,787 ids in all backfilled rows: 4,782 from the Chadwick register only,
   5 also in `crosswalk.csv`, 0 disagreements; 0 MLBAM ids mapped from two Retrosheet ids). Checked against MLB's
   own people records: **562 of 562 names match**. 12 signings fall after the player's last MLB game; all are real
   signings by players who did not play again (Flaherty 2006, Prior 2007, Clement 2008, R. Alomar 2005, Reese 2005
   and 2006, Mirabelli 2008, Kim 2008, Harnisch 2002, Sanders 2000, Bautista 2005; H. Ramirez 2008 flags only because MLB lists no last-game date). By hand:
   the 25 drawn rows of section 24, plus these 12 by name and date. A second assumption in the backfill: a
   Retrosheet date with day 00 becomes the 15th (4 of 7,021 signings).
5. **Check run: independent recompute of every graded free-agent row** (`tests/tools/fa_independent_check.py`,
   my own code from `lvm_cache.json` by club name and the documented price formula, not the engine's functions).
   Of 2,616 graded rows: realized agrees on 2,614, expected on 2,615 (QO charge included), 1 contract not matched.
   The 1 realized difference is Mirabelli BOS 2004-05 (0.6 live against 0.0): he was traded to San Diego in 2006
   and reacquired, and the engine stops crediting a deal once the player leaves, as documented. So the
   arithmetic holds outside the shared code. It still shares inputs (WAR cache, contract terms, season shares),
   which only the field checks test.

Nothing went to the public site.

## 26. Round 21 (Nov 11, 5:19 PM): launch list, determinism, fa97 re-check, WAR vintage

1. **Launch list:** `docs/launch-blockers-nov11.md`, ordered. Top item without Sean: the determinism patch.
2. **Determinism patch (`4ff51c5`).** 10 shuffled rebuilds under the patch: **1 distinct md5** (`1a4a4a5e`).
   Tests that could show it is still order-dependent: `PRAGMA reverse_unordered_selects=ON` changes the shipped
   build (`f375887b` to `a8a1e777`) but not the patched one; PYTHONHASHSEED 1, 2 and 3 and SQLite 3.51.1 against
   3.53.1 give the same patched md5. The 13 rows it changes against live are listed in full in
   `tests/tools/r21_determinism.json`: 12 move lists (8 same moves reordered, 4 a different tied move) and one
   dollar cell; none has a share page and none is a 2022+ winter. They do show in the all-winters view.
   **Rounding rule as built:** Python `round()` on the sum, which is round-half-to-even. 132 winter dollar totals
   sit exactly on .5 and live already rounds 131 of them to even (87.5 to 88, 102.5 to 102). The 132nd, Cardinals
   2004-05 at exactly $15.5M, shows 15 live only because the float sum came out at 15.4999...; with exact sums it
   is 16, which is the half-even answer. Half-up instead would change 64 cells, 10 in 2022+ winters and 2 on share
   pages (2005-bos, 2013-det). Recommendation: keep half-even and write it down.
3. **fa97 re-check, pre-registered** (`docs/prereg-round21.md`, `9753a0b`, committed 22:23:27 UTC before the first
   new search). Re-sourced inside the budget: Hermanson $800K (AP list), Alfonseca $1.35M (AP list), Dessens
   $1.55M (AP list), Conine total $1.7M (Baseball Almanac salary table; years still unverified). fa97 now: years
   19 match, 0 mismatch, 1 unverified; total 19 match, 1 mismatch (Fassero), 0 unverified. **Both pass**, so per the
   pre-registered rule pre-2009 terms stay as they are. Caveat: only the 4 failing rows were searched again.
   The card uses Fassero $1.5M (source $1.35M) and Furcal $30M (AP $33M with the buyout). Corrected, their grades
   move -1.5 to -1.4 and +4.1 to +3.7. Neither has a share page; both show on club pages and player trees.
   `tests/tools/prereg21_results.json`.
4. **WAR vintage.** The rebuild and the live grader read the same file: `/work/lvm_cache.json`, md5
   `4fc652f0`, identical to `data/lvm_cache.json` in the repo and on GitHub main, last changed in commit
   `0a9f2bd` (Nov 3, 14:24 ET), with version flags `__lvm_v15__` to `__lvm_v17__`. Every live build file is later
   (`cards.js` Nov 8, `book.js` Nov 10, `offseasons.json` Nov 10). Direct evidence that live used this vintage: the
   free-agent column rebuilt from it matches live on 815 of 816 winters (the 816th is the rounding cell), and the
   independent recompute matches 2,614 of 2,615 graded rows. The `/work` file times all read 06:08:27, so they
   come from a restore and say nothing about vintage. Not covered: trade nets were taken from the shipped outputs,
   not recomputed from this file.

Nothing went to the public site.

## 27. Round 22 (Nov 11, 5:36 PM): determinism patch deployed

Approved by Sean (via Kirk) for patch `4ff51c5` only.
- **Engine:** `279379f` (`engine/fa_grade.py` md5 `357f0041`, `engine/offseasons_build.py` `70c54fe4`).
- **Site:** `13a4570` (`offseasons.json` md5 `1a4a4a5e`). GitHub main and frontofficeledger.com (including the
  `?v=1` URL the page requests) serve `1a4a4a5e`; Pages updated it at 22:40:14 UTC.
- **Deployed code, 5 new shuffles** (seeds 20261151 to 20261155), run from the files fetched at `279379f` with only
  I/O paths redirected: 5 of 5 give `1a4a4a5e`. `PRAGMA reverse_unordered_selects=ON`: no change. `/work` untouched.
- **Live before/after:** 13 of 816 rows changed, none with a share page and none 2022+. 8 are the same five moves
  in another order. 4 swap one tied move: ATL 2001-02 Castilla for Smoltz (-0.5); ATL 2003-04 Alfonseca for E.
  Pérez (+0.8); SD 2007-08 Clark +0.1 for Wolf -0.1; MIA 2016-17 Ellis for McGowan (-0.4). The 13th is Cardinals
  2004-05 dollars, 15 to **16**.
- **Rollback (one step):** upload the previous `offseasons.json` (md5 `6842d1d0`, at
  `raw.githubusercontent.com/szerillo/front-office-ledger/279379f/offseasons.json`) to the repo root through
  the upload page. The engine files can go back the same way from `7c19cf0` (`01c80d6b`, `d6692708`).
- **Assumption checked: no other build step reorders ties.** It fails: 44 SELECTs without ORDER BY remain in
  scripts that read `sweep_tx` or the grader outputs (`tests/tools/r22_unordered_selects.txt`, file:line each),
  including the trade grader (`sweep_score.py` 4, `hist_score.py` 4, `trade_book.py` 1). `asset_rules.py:313` is
  order-free today because `asset_end` takes a minimum. The two set loops (`r5_conduit.py:12`, `desk_data.py:773`)
  only fill lookup maps. Untested whether the others change any published file; that test is step 0 of
  `docs/plan-items-5-6.md`.
