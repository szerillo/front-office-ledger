# Grade changes

Every regeneration of tests/fixtures/grades.json, with what moved and why. Written by
`UPDATE=1 REASON="..." node tests/t_grades.mjs`, which refuses to run without a reason. The audit doc links here.

## 2026-11-11 14:36 UTC · baseline

Reason: first snapshot, 13,209 grades (every trade side and every card row) from the page deployed Nov 11 with
the trade OPEN window fix. The page from before both OPEN fixes produced the same 13,209 grades.

## 2026-11-12 05:08 UTC · page built on candidate

Reason: Nov 12 deploy: re-sign rule (a same-club re-sign within 60 days keeps a trade open) and the 2020 charge prorated to 60 of 162 games, plus fix pass 1 (deterministic reads; seat-label order)

277 grades moved, 558 new, 544 removed (of 13223).

| Grade | Was | Now | Change |
|---|---|---|---|
| t / 2013-12-10 / ARI/ARI/CWS/LAA / 0ARI | -1.3 | -13.6 | -12.3 |
| t / 2013-12-10 / ARI/ARI/CWS/LAA / 1ARI | -13.6 | -1.3 | +12.3 |
| c / COL / 2019-01-15 / Extended Nolan Arenado · 8 yr / $260.0M (veteran) | -5.6 | -1.9 | +3.7 |
| t / 2010-11-12 / BOS/MIA / 0BOS | 0.0 | 3.2 | +3.2 |
| t / 2010-11-12 / BOS/MIA / 1MIA | 0.0 | -3.2 | -3.2 |
| c / LAA / 2019-03-15 / Extended Mike Trout · 12 yr / $426.5M (veteran) | -2.7 | 0.3 | +3.0 |
| c / WSH / 2019-12-09 / Signed Stephen Strasburg · 7 yr / $245.0M (2019-20 winter) | -18.9 | -16.0 | +2.9 |
| c / LAA / 2019-12-13 / Signed Anthony Rendon · 7 yr / $245.0M (2019-20 winter, QO) | -16.2 | -13.3 | +2.9 |
| t / 2014-12-19 / MIA/NYY / 0MIA | 7.3 | 4.9 | -2.4 |
| t / 2014-12-19 / MIA/NYY / 1NYY | -7.3 | -4.9 | +2.4 |
| c / NYY / 2014-12-19 / Miami Marlins traded RHP Nathan Eovaldi, RF Garrett Jones an | -7.3 | -4.9 | +2.4 |
| c / BOS / 2019-03-15 / Extended Chris Sale · 5 yr / $145.0M (veteran) | -9.1 | -6.7 | +2.4 |
| c / HOU / 2019-03-15 / Extended Justin Verlander · 2 yr / $66.0M (veteran) | -6.8 | -4.6 | +2.2 |
| c / STL / 2019-03-15 / Extended Paul Goldschmidt · 5 yr / $130.0M (veteran) | 5.5 | 7.7 | +2.2 |
| c / MIL / 2020-03-15 / Extended Christian Yelich · 9 yr / $215.0M (veteran) | -3.2 | -1.0 | +2.2 |
| c / DET / 2014-03-15 / Extended Miguel Cabrera · 8 yr / $248.0M (veteran) | -25.5 | -23.5 | +2.0 |
| c / BOS / 2019-04-15 / Extended Xander Bogaerts · 6 yr / $120.0M (veteran) | 4.7 | 6.6 | +1.9 |
| c / SD / 2019-02-21 / Signed Manny Machado · 10 yr / $300.0M (2018-19 winter) | 7.8 | 9.6 | +1.8 |
| c / PHI / 2019-03-02 / Signed Bryce Harper · 13 yr / $330.0M (2018-19 winter, QO) | 15.6 | 17.2 | +1.6 |
| c / NYM / 2016-11-30 / Signed Yoenis Cespedes · 4 yr / $110.0M (2016-17 winter) | -8.0 | -6.5 | +1.5 |
| c / PHI / 2019-12-09 / Signed Zack Wheeler · 5 yr / $118.0M (2019-20 winter, QO) | 12.5 | 14.0 | +1.5 |
| t / 2022-03-12 / MIN/MIN/NYY/TEX / 3TEX | -0.7 | -2.1 | -1.4 |
| t / 2022-03-12 / MIN/MIN/NYY/TEX / 0MIN | -1.2 | 0.2 | +1.4 |
| c / LAA / 2017-11-15 / Extended Justin Upton · 5 yr / $106.0M (veteran) | -7.3 | -6.0 | +1.3 |
| c / COL / 2018-04-15 / Extended Charlie Blackmon · 6 yr / $108.0M (veteran) | -5.6 | -4.3 | +1.3 |
| c / KC / 2011-06-06 / Drafted Bubba Starling (#5 overall, 2011) | -10.9 | -12.2 | -1.3 |
| t / 2023-01-03 / ATL/TEX / 0ATL | -0.1 | 1.1 | +1.2 |
| t / 2023-01-03 / ATL/TEX / 1TEX | 0.1 | -1.1 | -1.2 |
| c / PHI / 2018-03-12 / Signed Jake Arrieta · 3 yr / $75.0M (2017-18 winter, QO) | -4.9 | -3.7 | +1.2 |
| t / 2015-11-11 / NYY/SD / 0NYY | 0.3 | -0.9 | -1.2 |
| t / 2015-11-11 / NYY/SD / 1SD | -0.3 | 0.9 | +1.2 |
| t / 2018-04-02 / ARI/BAL / 0ARI | 0.0 | 1.2 | +1.2 |
| t / 2018-04-02 / ARI/BAL / 1BAL | 0.0 | -1.2 | -1.2 |
| c / CWS / 2019-11-21 / Signed Yasmani Grandal · 4 yr / $73.0M (2019-20 winter) | 0.5 | 1.7 | +1.2 |
| c / ATL / 2014-02-15 / Extended Freddie Freeman · 8 yr / $135.0M (arb) | 12.0 | 13.2 | +1.2 |
| c / CIN / 2012-04-15 / Extended Joey Votto · 10 yr / $225.0M (arb) | 9.7 | 10.8 | +1.1 |
| c / ARI / 2019-12-17 / Signed Madison Bumgarner · 5 yr / $85.0M (2019-20 winter, QO | -7.1 | -6.0 | +1.1 |
| c / WSH / 2015-01-21 / Signed Max Scherzer · 7 yr / $210.0M (2014-15 winter, QO) | 11.1 | 12.2 | +1.1 |
| c / WSH / 2018-12-07 / Signed Patrick Corbin · 6 yr / $140.0M (2018-19 winter, QO) | -5.3 | -4.2 | +1.1 |
| c / CWS / 2019-11-14 / Signed José Abreu · 3 yr / $50.0M (2019-20 winter) | 4.9 | 6.0 | +1.1 |

(237 smaller moves not listed)

New: t / 1998-06-09 / ATH/COL / 0ATH; t / 1998-06-09 / ATH/COL / 1COL; t / 2002-07-29 / COL/CWS / 0COL; t / 2002-07-29 / COL/CWS / 1CWS; t / 1999-07-31 / ATH/KC / 0ATH; t / 1999-07-31 / ATH/KC / 1KC; t / 1999-08-18 / ATH/MIL / 0ATH; t / 1999-08-18 / ATH/MIL / 1MIL; t / 2002-01-25 / SEA/SF / 0SEA; t / 2002-01-25 / SEA/SF / 1SF; t / 2001-11-02 / ATH/CHC / 0ATH; t / 2001-11-02 / ATH/CHC / 1CHC; t / 1999-12-13 / ATH/COL/MIL / 0ATH; t / 1999-12-13 / ATH/COL/MIL / 1COL; t / 1999-12-13 / ATH/COL/MIL / 2MIL and 543 more

Removed: t / 1998-06-09 / COL/ATH / 0COL; t / 1998-06-09 / COL/ATH / 1ATH; t / 2002-07-29 / CWS/COL / 0CWS; t / 2002-07-29 / CWS/COL / 1COL; t / 1999-07-31 / KC/ATH / 0KC; t / 1999-07-31 / KC/ATH / 1ATH; t / 1999-08-18 / MIL/ATH / 0MIL; t / 1999-08-18 / MIL/ATH / 1ATH; t / 2002-01-25 / SF/SEA / 0SF; t / 2002-01-25 / SF/SEA / 1SEA; t / 2001-11-02 / CHC/ATH / 0CHC; t / 2001-11-02 / CHC/ATH / 1ATH; t / 1999-12-13 / COL/MIL/ATH / 0COL; t / 1999-12-13 / COL/MIL/ATH / 1MIL; t / 1999-12-13 / COL/MIL/ATH / 2ATH and 529 more
