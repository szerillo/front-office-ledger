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

Scope: the 1,918 players with service data. 1,159 of them have a control end different from the debut-year
rule. Corrected (service-time) end versus current:
- extensions: 29 of the 164 covered move;
- trade seats: 833 move at all, 143 by 0.5 wins or more, 74 by a win or more (trades and extensions together).

Top 25 movers:

| # | Kind | Club | Date | Move | Now | Corrected | Change |
|---|---|---|---|---|---|---|---|
| 1 | ext | ATL | 2022-03 | Matt Olson 8y/$168M (control end 2022 to 2023) | +12.0 | +3.8 | -8.2 |
| 2 | ext | MIN | 2019-02 | Jorge Polanco 5y/$25.75M (2020 to 2022) | +8.7 | +1.3 | -7.4 |
| 3 | trade | ATL | 2022-03-14 | Olson from ATH | -4.2 | +2.6 | +6.8 |
| 4 | trade | ATH | 2022-03-14 | Olson to ATL | +4.2 | -2.6 | -6.8 |
| 5 | ext | NYM | 2019-03 | Jacob deGrom 5y/$137.5M (2020 to 2021) | -4.0 | -8.4 | -4.4 |
| 6 | ext | TB | 2023-01 | Yandy Díaz 3y/$24M (2022 to 2024) | +6.4 | +2.0 | -4.4 |
| 7 | trade | PHI | 2024-12-22 | Luzardo from MIA | +2.3 | +6.3 | +4.0 |
| 8 | trade | MIA | 2024-12-22 | Luzardo to PHI | -2.3 | -6.3 | -4.0 |
| 9 | ext | PHI | 2026-03 | Jesús Luzardo 5y/$135M (2025 to 2026) | +2.1 | -1.8 | -3.9 |
| 10 | trade | TB | 2018-12-13 | Yandy Díaz three-team deal | +8.4 | +11.5 | +3.1 |
| 11 | trade | CLE | 2018-12-13 | same deal | -7.4 | -10.5 | -3.1 |
| 12 | ext | LAD | 2020-02 | Chris Taylor 2y/$13.4M (2020 to 2021) | +2.4 | -0.7 | -3.1 |
| 13 | trade | TB | 2020-01-09 | Arozarena from STL | +8.6 | +11.7 | +3.1 |
| 14 | trade | STL | 2020-01-09 | Arozarena to TB | -8.6 | -11.7 | -3.1 |
| 15 | trade | WSH | 2014-12-19 | Trea Turner three-team deal | +18.5 | +21.5 | +3.0 |
| 16 | trade | SD | 2014-12-19 | same deal | -13.1 | -16.1 | -3.0 |
| 17 | trade | MIA | 2021-07-28 | Luzardo from ATH | +5.8 | +8.7 | +2.9 |
| 18 | trade | ATH | 2021-07-28 | Luzardo to MIA | -5.8 | -8.7 | -2.9 |
| 19 | ext | MIN | 2021-11 | Byron Buxton 7y/$100M (2021 to 2022) | +7.8 | +4.9 | -2.9 |
| 20 | ext | TB | 2022-08 | Tyler Glasnow 2y/$30.35M (2022 to 2023) | +1.2 | -1.5 | -2.7 |
| 21 | ext | LAD | 2020-02 | Max Muncy 3y/$26M (2021 to 2022) | +2.0 | -0.5 | -2.5 |
| 22 | trade | ATH | 2017-07-16 | Luzardo and Treinen from WSH | +4.9 | +7.4 | +2.5 |
| 23 | trade | WSH | 2017-07-16 | same deal | -4.9 | -7.4 | -2.5 |
| 24 | trade | LAD | 2016-06-19 | Chris Taylor from SEA | +9.3 | +11.7 | +2.4 |
| 25 | trade | SEA | 2016-06-19 | same deal | -9.3 | -11.7 | -2.4 |

The pattern: an extra controlled season moves value out of the extension, where it was being called a
bought-out free-agent year, and into the trade that brought the player in. Atlanta's Olson moves are
-8.2 on the extension and +6.8 on the trade, nearly a wash for the club but a large swing for each grade.
Grades that flip sign: Olson trade (both seats), Luzardo extension, Taylor, Glasnow and Muncy extensions.

Club ranks (all-time trades plus extensions, the 30-club table; 14 clubs move):
MIL 4 to 2, TB 2 to 3, ATH 3 to 4; COL 10 to 11, SF 11 to 10; CHC 17 to 13, SD 13 to 15, DET 18 to 16,
MIN 15 to 18, LAD 16 to 17; CWS 19 to 20, KC 20 to 19; SEA 24 to 25, TEX 25 to 24.
Biggest club totals: MIN -14.5, LAD -9.6, SD -8.8, NYM -7.2, STL -6.2. This is a lower bound, since only
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
