# Round 44 (Nov 12, 09:45 to ~10:40 ET)

## Call 1: service-time control end. Pre-registered (a193bf0), built, FAILED the bar. Not shipped
Source: MLB Stats API transaction history per player (statsapi.mlb.com/api/v1/transactions), counted day by day against
the official regular-season dates; actual days capped at 172 (the old svc_fetch rescaling to 186 days removed);
2020 x 172/67; 2022 lockout days; option stints under 20 days counted. Control ends in the season service reaches
6.000. Feed coverage starts 2009, so pre-2009 debuts keep the old rule.
Named cases: Donaldson 2018 (public: after 2018) RIGHT; Olson 2023 (public: after 2023) RIGHT.
Sample (draw_sample.py, seed 20261144, fixed before any lookup): 5 optioned-after-debut-season + 15 random from 184
extended players with debuts 2010-2019. Lookups stopped once the bar could no longer be met:
| Player | New | Old | Public free-agent year | New right? |
| Nate Jones | 2017 | 2017 | after 2017 (AP, Dec 2015) | yes |
| Mitch Keller | 2025 | 2025 | after 2025 (AP / MLB Trade Rumors, Feb 2024) | yes |
| Elias Díaz | 2022 | 2021 | after 2022 (MLB.com: extension covers 1 arb year + 2 FA years, 2022-24) | yes |
| Kole Calhoun | 2019 | 2018 | first eligible for 2020 (ESPN, Jan 2017) | yes |
| Matt Moore | 2018 | 2017 | after 2017 (MLB Trade Rumors, Oct 2011: a month in the minors in 2012 would push it to 2018; he opened 2012 in the majors) | no |
| Chris Archer | 2019 | 2018 | after 2018 (deal through 2019 bought one FA year; options two more) | no |
| Ryan McMahon | 2024 | 2023 | after 2023 (ESPN / CBS, Mar 2022) | no |
Three misses in seven: at most 17 of 20 possible, under the 19 of 20 bar. Per the pre-registration nothing goes into
the regrade, and the innings fix stays held with it.
Why it misses: all three are short of 1,032 days by a little (Moore 1,031, Archer 1,017, McMahon 1,018 after the
season they should have reached it). The day count from transactions undercounts some stints (likely injured-list
and rehab paperwork, and same-day option/recall order). I did not tune it after seeing this: a fix needs a new
pre-registration and a fresh sample.
Still true on live: the control end is "six seasons from debut", wrong for late or optioned arrivals (Donaldson, Olson).

## Call 3: t_winter reported-player exception. Done
availList now allows a core player of a club that is not rebuilding only with a named report. New self-check
availReportedOnly: a planted unreported core player (first match on live data) fails the rule; the Lile row (named
report) passes. On live: availList true, availReportedOnly true.

## Call 4: one line on the 17 trades on no card. Deployed with call 3
Commits 232a52d index.html (8c233498), cf5f379 t_winter, 87313f2 t_build pin. Gate CLEAR before index.html.
All 19 suites pass before (staged tree) and after (fresh clone + live files); live = staged at 14:58 UTC.
Build source carries the line.
Methodology, Known limits: "Seventeen trades were made between one front office and the next (by an interim GM, or in
the days between one head of baseball operations leaving and the next arriving); they are graded and count in the
club's winter, but they are on no front office's card."

## Call 5: grade and Horizon/farm rank test pre-registered (a193bf0, prereg_grades_ranks.md). Not run
To run after the regrade, per Kirk. The regrade did not happen this round, so it waits.

## Challenge: a public number that flips at correlation 0.18
The 1998-99 Tigers winter page. As run (correlation 1), it is in the worst 20 in 87.9% of draws, under 90%, so the
page reads "A -30.5-win offseason". With independent seasons (correlation 0) it is in 99.8%. At 0.18 it would almost
certainly clear 90% and read "Among the 20 worst offseasons since 1998". Not run at 0.18 (Kirk: no new setting);
the two runs bracket it. Others in the same position: 2014-15 Padres (0.847 / 0.996), 2010-11 Rangers best
(0.844 / 0.994).

## One more assumption, tested: the scheduled share-pages job will not undo the winter wording
Ran engine/share_live.mjs exactly as the scheduled job does (--only-new against a fresh clone of main at a193bf0):
0 winter pages rewritten (5 club pages, which follow the Wire, as designed). The next scheduled run keeps the
no-rank wording.
