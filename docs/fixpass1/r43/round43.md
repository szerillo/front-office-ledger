# Round 43 (Nov 12, 09:05 to ~09:35 ET)

## Check A first: does "Among the 20" hold? Pre-registered (168f85a), then run as written
Same draws as the r42 run (seed, sample, 2,000 draws, residual design unchanged). Rule: keep the band only if the
winter is in the published 20 AND is in the simulated 20 in at least 90% of draws.
Result (membership_results.txt): one winter passes, the 2012-13 Blue Jays (in the worst 20 in 94.5% of draws).
Best side, published #1 to #20: P_top 0.74, 0.80, 0.84, 0.62, 0.52, 0.65, 0.62, 0.60, 0.60, 0.57, 0.51, 0.45, 0.27,
0.31, 0.41, 0.41, 0.45, 0.32, 0.24, 0.36. Edge #17 to #24: 0.45, 0.32, 0.24, 0.36, 0.31, 0.34, 0.18, 0.28.
Worst side #1 to #5: 0.945, 0.85, 0.88, 0.73, 0.76; the rest 0.13 to 0.64. Independent-seasons column reported only.

## Calls 1 and 2: no rank numbers anywhere tested; known-limits paragraph. DEPLOYED, gates green
- Winter pages: 39 lose the band and read "A +33.9-win offseason, under ..."; 2012-tor keeps "Among the 20 worst".
- Offseason explorer: no "#N" on any card; the tested band shows on TOR 2012-13 only.
- Front office leaderboard and the report-card ranking box: listed by score, no rank numbers; the box says why.
- Simulator: "would land better than about N% of real ones" (rounded to 10), no rank or neighbors.
- Methodology, "Known limits": FIP-based pitching, stint-row salary split, arbitration estimates, 1998-2014
  extension file, and the parked pre-season release rule. Corrections page: one paragraph.
- Commits: 222a16b og/o (39), 2d459ed o (39), 2403ca5 corrections, 3727fe4 index.html (a97f328c), b7a21a4 tests,
  52b75a8 t_build pin, d8caf40 generator. 86 files staged; 39 pages changed (under 50). Data files unchanged; gate
  CLEAR before index.html. Build source (/work prototype) carries the same 10 edits.
- Before (staged tree served locally): 18 of 19 suites pass, including t_build, t_launch, t_wire, t_cards,
  t_nullgrades, t_hashnames. After: live = staged 86/86 at 14:24 UTC; fresh clone + live files: same 18 of 19.
- The one red, t_winter availList, is the same on live before this deploy: the 07:07 trade-reports job added a named
  report on Daylen Lile (WSH), and the test forbids a non-rebuilding club's core player on the available list.
  The page follows the report; the test needs a reported-player exception. Not caused by this change.
- Found and fixed: t_nov11 dealsLazy had been red on live since r42 (it looked for "deals.js"; the file is now
  hashed). My r42 gate ran 6 suites, not all 19. The site loaded deals fine; only the test was wrong.

## Call 3: innings bug. Measured, HELD (grades would change)
Fix: read the feed's innings as outs (155.1 = 155 1/3) in the pitcher formula and the league constants.
Exact per-row effect from the live feed (22,628 pitcher stints): mean +0.005, max 0.017 wins.
Propagated through a full engine run (D2, same as live run Z_X6 but with the fix):
- trade-side numbers that change at one decimal: 712 of 7,643; largest raw change 0.3 wins
- winter totals that change: 315 of 816; largest 0.4 (TOR 2012-13 -50.8 to -51.0)
- front office channel nets that change at one decimal: 270 of 820; largest 0.5
- channel letters that change (page grading rule replicated): 9, among them TOR draft C to D+, BOS, DET, SD waivers
The per-row change is tiny; the larger moves come from the prospect and draft calibration curves refitting on the
new WAR (the same side effect as the pre-season rule in r39). Rule was "deploy only if no grade or band changes":
held. Not deployed; the engine run and change lists are kept (ip_changes.json).

## Check B: which way the full within-player correlation biases the 11.2
The run applied one residual to all of a player's seasons; the measured season-to-season correlation is 0.18. Full
correlation makes a player's errors add up instead of partly cancelling, so the spread of totals is overstated and
the 11.2-win gap is too large. Both tests are therefore strict: they deny ranks and bands that a correctly correlated
model might keep; they cannot grant one that would not hold. The independent-seasons column (the other extreme) still
gave no exact rank above 0.876, so "no exact rank" holds under either setting; the band result (1 of 40) is the part
most sensitive to this choice.

## Check C: service-time control end, 5 public cases. NOT fixed
Deployed engine (asset_rules.control_span): six seasons from debut, no service time ("options and Super Two are not
modeled"). My r42 "believed fixed" was wrong.
| Player | Engine last control season | Public | Match |
| Josh Donaldson | 2016 | free agent after 2018 (MLB Trade Rumors, Jan 2018) | no, 2 short |
| Matt Olson | 2022 | free agent after 2023 (AP / ESPN, Mar 2022) | no, 1 short |
| Kris Bryant | 2021 | free agent after 2021 (ESPN, Jan 2020) | yes |
| Mookie Betts | 2020 | free agent after 2020 (ESPN, 2019) | yes |
| Juan Soto | 2024 | free agent after 2024 (CBS Sports, Feb 2024) | yes |
Misses are the known class: late-arriving players with options or Super Two. It moves value between the trade that
acquired a player and his extension (Nov 11 sizing: fixing it moves Olson's extension -8.2 and his trade +6.8).
