# Round 46 (Nov 12): service-time fallback built, trade-report check fixed, challenges

## 1. Fallback (prereg f508434), deployed
Published figures file: published_service.json. Source: MLB Trade Rumors' annual arbitration projection posts,
which print official service time (X.YYY, as of the end of the prior season) beside each player. Posts with service
time found for 2015-2020 and 2023-2027 (2012, 2014 and 2021 posts have no service column; 2013 and 2022 not found).
2,667 rows, 2,622 matched to MLBAM ids (13 unmatched, 32 dropped as same-name ambiguous), 1,366 players. Control end
= the season service reaches 6.000, from the latest row, 172 days a season after it (build_pub.py).
On the site (index.html 6477985): the Deal Desk, simulator, club pages and trade block use official service time for
the 293 current players on the 2027 list (end of 2026); every other control end from our own count is marked
"estimated" / "est." (684 of 1,134 controlled players). Contract-covered control is not marked. Methodology: the club
control rule now states its measured error (item A).
What changed, live vs staged (diff_summary.json): 31 Desk players (27 control ends, 10 arbitration classes, 22
surplus values, 1 cornerstone flag: Paul Skenes, 3.000 after his Rookie of the Year credit, control through 2029, three
seasons left, so no longer a cornerstone under the four-season rule); 8 of 30 club Horizon pages (TB, BOS, SEA, ATH,
CHC, PIT, STL, CIN); 0 graded moves, 0 share pages (no engine run; share pages print no control end). All follow from
the pre-registered rule. Under the 50-page stop.
Two tests asserted the old count and were updated with the reason in the file: t_math serviceIsReal (Skenes now 3.000
and 2029) and t_qa cornerstonesStay (Crow-Armstrong replaces Skenes).

## 2. Trade reports: club and date (rumors.json b91f777, page 6477985, tests 3a49d18)
Each row now carries the club the report is about (rows[5]) and the date it was last confirmed (rows[6]); backfilled
from the Desk club and the file's checked date (no reported player changed clubs since Sep 1 per the MLB feed).
dkRumor drops a report if the player is now with another club, or if the live feed shows a change of club dated after
the report. Rows without the fields fall back to the file's checked date. Planted checks in t_winter:
before the fix (live page dc1149d): staleReportClubRejected false, staleReportDateRejected false: FAIL.
After (staged and live): both true, currentReportKept true: PASS.
The daily trade-reports job must write the two fields for new rows (skill edit proposed to Sean).

## 3. Challenges
A. Control end vs published, 1,366 players who reached arbitration (chalA.json):
- live grading rule (six seasons from debut) minus published: -10:1 -8:2 -7:5 -6:2 -5:12 -4:36 -3:61 -2:192 -1:523
  0:520 +1:11 +2:1. Off by a year or more for 846 (61.9%), almost all too early (834).
- transaction counter (service.json) minus published, 778 overlap: -1:20 0:632 +1:95 +2:24 +3:6 +4:1: off for 146 (18.8%).
Caveat: only players who reached arbitration are published, so the sample leans to players who were sent down.
Over 10%: proposal in the reply, not built.
B. Played seasons with 0 counted days (WAR cache rows vs counters, 2009-2026): live Desk counter 24 of 8,829
player-seasons (19 players, 11 of them 2024); v2 frame 8 of 1,935 (3 players: Herrera 2015-18, Walden 2010-12,
Calhoun 2023). Herrera and Walden are not missing data: the feed has them on file as a Rule 5 draft (code DR) and a
contract purchase (PUR), two codes the counter does not read. Calhoun 2023 unexplained.
C. The 1,381 graded players who debuted before 2009 get the same rule as everyone (six seasons from the MLB debut,
one more for a debut after mid-April; first WAR season plus five if no debut date). Stated on the methodology page;
as of this deploy the page also states its error. Past-move pages print no control end, so there is nothing to label
there. 43 of them have a published figure.
D. Assumption in the file: service time published at the end of a season, carried forward at 172 days a season,
gives the season he reaches 6.000 ("free agent after"). Checked against public free-agent years: Donaldson 2018,
Harper 2018, Machado 2018, Cole 2019, Betts 2020, Bryant 2021, Severino 2022: 7 of 7 match. It breaks when a player
loses days after the row: of 836 players with 2+ rows, the earliest row's control end differs from the latest's for
108 (12.9%). The file uses the latest row, so that error shrinks but is not zero.
