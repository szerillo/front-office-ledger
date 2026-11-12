# Round 51 (Nov 12, 2026)

## 1. Grades on published control end: HELD. The prereg stopped at the sensitivity check; F2 was not run.

Prereg 28d2959 (prereg_r51.md) was committed before the first run. Results against the written order:

| Step | Bar | Result |
|---|---|---|
| 1. B0 record run (live engine, round 50 freeze, RECORD on) | identical to live | PASS: 0 differences; cards.js, moves.js, offseasons.json, trade_book.json byte-identical to Z_X6 |
| 2. FZ2 freeze check (live engine, full freeze, replayed fits) | identical to live | PASS: 0 differences; the same four files byte-identical |
| 3. Sensitivity check (plant +1.0 on 8,783 season values of the 846 changed-control players) | PU must complete and trip; PF must complete and pass | COULD NOT COMPLETE: both PU and PF stopped at champions_build (step 15 of 31) |
| 4. F2 | | NOT RUN |

Why step 3 stopped: the plant changes which players the championship-ledger step looks up, and one lookup
(statsapi people/465041 rosterEntries) is not in the frozen network cache. The sandbox guard ends the run on any
network call it cannot replay (exit 97), as designed. The real rule change in round 50 (F1) never needed that call.
No partial results were scored. Per the prereg, no variant was run and F2 did not start.

Fit inventory (from evidence, inventory_F1.json, committed with the prereg): instrumented runs logged every file read
with its md5, every module global at exit and every statistics/numpy estimator call. Beyond the round 50 freeze, five
in-run fits move when control ends change: the international class baseline (ifa_score class_tot/class_n), move-letter
bands (regen_v3 MOVE_BANDS), style statistics (regen_v3:51-52), reliability weights (reliability.py) and the
validation regression (validation.py). Steps 1 and 2 show the record/replay freeze of all of them reproduces live
byte for byte.

Proposed amendment (needs Kirk's GO, not run): the read logs show champs_computed.json is read only by regen_v3, for
the championship pages; no graded file reads it. Plant runs would skip champions_build and copy the baseline
champs_computed.json, with championship pages excluded from the plant bars only. The real F2 run keeps the step.

## 2. Kinley misses: two different causes

Anderson 2023 (counter 152, truth 136): the counter is right; the truth method is wrong. The 16 days are 3 days in
DFA limbo (May 10 to 12) and 13 days of a retroactive injured-list placement (July 15 to 27, filed July 28). A
designated player keeps accruing service, and so does a player on the injured list; the truth (active-roster
snapshots plus IL from the filing date) counts neither.
Morgan 2026 (61 vs 50): the counter is wrong. On Mar 25 the feed files his contract selection after his option on
the same date, so the counter ends the day on the roster; he was optioned. 11 days overcounted.
Shared across the 184-player frame (count184.json): the same-day option order applies to 1 player-season (one date,
32 days). The truth-method blind spots are common: 133 of 184 players have a retroactive IL placement and 65 an
in-season DFA, so any re-scoring needs a truth that credits both. Also found: under 20 days on optional assignment
in a season still earn service (the counter treats every option day as off). Not sized.
No prereg written yet; the next one needs the truth fixed first.

## 3. Gallen 2026 (78 to 172): supported, not verified against a published 2026 figure

Published: 5.100 entering 2025 (MLBTR 2025 list) and 6.100 entering 2026 (Spotrac). No published figure covers
2026 itself, because a six-plus-year veteran is on no arbitration list. Supporting evidence: the Feb 14, 2026
return was a one-year major league contract (MLB.com, MLBTR), he pitched from Opening Day (Mar 26) to Sep 25, and
the league roster service shows him active or on the injured list for a full service year of season days. Label: supported by roster
records, not verified against a published figure.

## Challenges

A. Launch scope. "A published number is wrong" versus "estimated and labeled":
- Wrong and not labeled per number: the debut-based control end in past grades (disclosed in the methodology;
  133 letters carry the "depends on control end" chip). The round 50 run F1 shows the correction would change a number
  on 108 of 152 front-office cards (58 channel letters, 26 overall grades) and the value of 19 of 44 winter share
  pages. These are the live pages I believe show a wrong value today: 108 card pages and 19 winter pages.
- Wrong but listed as known open items on the corrections page: the pre-season release rule (92 trade-side numbers,
  59 winters, up to 1.9).
- Wrong and small, not labeled: innings read as decimals (155.1 not 155 1/3); measured in round 43 at 712 trade
  numbers and 315 winters, at most 0.4.
- Estimated and labeled: Desk control ends marked estimated (counter; the error is disclosed), MLBTR figures until
  final, the counter gaps (Kinley re-signs, same-day options), which reach only labeled estimates.
Call for Kirk: the control-end item is the only one that changes letters people will quote; the others are precision.

B. Third source for Lucchesi: Spotrac's contract table lists his 2024 arbitration deal at 4.112 years of service at
signing and 4.113 for 2025; FanGraphs and Spotrac both show 5.047 now. That supports 5.112 being a typo. Caveat: an
earlier Spotrac snapshot also showed 5.113, so the sources were not independent at the time.

C. allsuites_v2 does not catch an empty suite. Plant: 19 suites, t_cards prints PASS with 0 checks. v2: exit 0,
"t_cards exit=0 PASS", DONE 19/19. Fix, allsuites_v3.sh: each suite must report at least as many checks as on the last
clean run (manifest from round 50's post-deploy run; count_checks.py reads the report). v3 on the plant: exit 1,
"t_cards exit=0 THIN(0<6) checks=0", DONE 18/19.

v3 on the live tree (f37c918 page, fresh pull): DONE 19/19, every suite at or above its manifest count (v3_live_exits.txt).
