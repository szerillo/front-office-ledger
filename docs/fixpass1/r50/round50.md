# Round 50 (Nov 12, 2026)

## 1. Calibration-freeze run (prereg b2477dc): FAIL. Grades stay held.

Result against the written bar, reported first:

| Step | Bar | Result |
|---|---|---|
| 1. Freeze check (FZ0, live engine plus freeze) | 0 differences from live | PASS: 0 differences in nets, letters, overall grades, totals, trade seats, winters, ranks |
| 2. Spread plant (FP, +5.0 on one extension) | target ext net moves exactly 5.0; no other front office's letter, net or rank moves | PASS: stl-walt-jocketty 54.7 to 59.7; 0 other moves |
| 3. F1 (published control end, freeze on) | 0 untraced letters | FAIL: 2 (cle intl, sd intl) |
| | 0 untraced overall moves | FAIL: 3 (lad, nyy, sd-omar-minaya interim) |
| | every changed number attributed | FAIL: 8 nets, 74 trade seats, 71 winters, 80 entries unattributed |
| | letters changed at most 150 | PASS: 58 |
| | overall changed at most 40 | PASS: 26 |
| | TOR 2012-13 top 2, 90% of margin | PASS: 1 / 31.7 to 2 / 31.6 |
| | untraced pages at most 50 | FAIL: 80 |

No variants were run and nothing was re-sliced. Order followed the prereg (freeze check, then plant, then F1 and R1).
The plant target was fixed in run_note.md before any run: the one front office whose +5.0 cannot pass anyone in
the overall or extension ordering, so a moved rank could only be leakage.

What the failure shows (read after the verdict): the freeze held for every file the prereg named (md5-checked after
every step, unchanged), but at least one fit is not a file. ifa_score.py re-fits its league class baseline from all
outcomes inside the run: Cleveland's international entries move for players with no control change (Francisco Mejía
expected 1.71 to 1.69), and Anthony Santander's traced change carries the channel. The trade seats and winters that
move without a changed-control player point the same way (fits inside trade_book and the comps steps). A next prereg
would have to enumerate in-memory fits, not only fit files.

Plant sensitivity, disclosed: repeating the plant with the spread re-fit instead of frozen also moved no other letter
(step2_control.json). At +5.0 on one front office the plant cannot tell a frozen spread from a re-fit one.

Re-fit path (R1 minus F1, measured only): 258 nets, 31 letters, 16 overall grades, 616 trade seats, 101 winters.

Runs: FZ0, FP, F1, R1 under /tmp/sbx/runs; one FP launch failed at the shell before any step ran (the plant key held
a "|" the driver's shell read as a pipe) and was relaunched with ":" as the separator. Freeze mechanism:
ext_grade_freeze.diff, step_run_freeze.sh (trade_calib and draft_calib skipped; a per-step md5 check stops the run).

## 2. Kinley dry run: FAIL (17 of 19). Nothing built or deployed.

The frame is smaller than the planned sample: 19 player-seasons (elected free agency, then an assignment to an MLB
club before the next Opening Day, 2015 to 2026, service pool). Drawn as a census; read before scoring as 19 of 19
(at least 95%, matching 19 of 20). Truth: days on the club's active roster (league roster service, every season day)
plus MLB injured-list days, scaled like the counter.

| Bar | Result |
|---|---|
| at least 19 correct (within 10 days) | FAIL: 17 of 19 (old counter: 15) |
| Kinley 2026 counted 172 | PASS: 107 to 172 |
| all existing plants pass | PASS (Rule 5, purchase, elected free agency, DFA limbo) |
| 184-player frame: every change listed and explained | PASS: 1 change, Kinley 2026 107 to 172 |

The two misses are not cases the rule touches: Chase Anderson 2023 (counter 152, truth 136) and Eli Morgan 2026
(61 vs 50); the rule did not fire for either and both counts are unchanged from the old counter. The rule fixed Zac
Gallen 2026 (78 to 172) and Kinley. Per the bar, no build.

## 3. Team-heading match: deployed, 0 live value changes (proved by md5)

Commit 53ca8a9: engine/build_pub.py (team-heading tie break), engine/published_service.json and
engine/pub_svc_2027.json (the Desk map: 2027 list limited to Desk players). The rebuilt map equals the live PUB_SVC
exactly (293 players), so index.html was not touched (md5 d4baadb7 before and after). engine/ is not served by the
site (404), so the commit cannot reach a page.

| Value dump | Before | After |
|---|---|---|
| Desk values (1,982 players, club horizons) | c25bca11a598 | c25bca11a598 |
| Graded letters and numbers (152 cards, 942 channels) | 28cf6541870f | 28cf6541870f |
| PUB_SVC map in the live page | 8ef3fd0a1c31 | 8ef3fd0a1c31 |

Gates: 19/19 before, 19/19 staged, 19/19 after (fresh clone, new runner).

## 4. Innings fix: held.

## Challenges

A. It would be false if the new tie break placed a 2027 row on a Desk player. Plant (rows_planted: one extra 2027 row,
"Max Muncy" under the Athletics): the old builder leaves it ambiguous with the Dodgers' Max Muncy; the new one places
it on 691777. Desk dump md5 c25bca11a598 to ae98d506d962: 1 player (control end 2031 estimated to 2030), the ATH
horizon moves. A first plant (Luis García under the Twins) changed the map but no Desk value, because a contract
covers him: the Desk dump alone would have missed it. That is why the map md5 is in the value dump above.

B. Signal: the 2027 post's caveat sentence ("Service time data is not finalized and the Super Two cutoff is not yet
official") is gone; diff_mlbtr.py reports caveat_new false. The ESPN report of the official cutoff (Nov 5) is not
enough on its own, because MLBTR has not revised the post. First daily re-pull (Nov 12, 18:44 UTC): 296 rows, 0
changed, 0 added, 0 dropped, caveat still present. Lucchesi pair re-pulled: 5.112 (2025 list) and 5.047 (2026 list),
both unchanged. Our counter puts him at 4.090 after 2024 and 101 days in 2025: the 2025 figure is a typo for 4.112
(4.112 plus 107 days is exactly 5.047). The later list stands, which is what the build already uses.

C. No. Seven of 28 has a 95% range of 13% to 43%: a factor of three, so any single rate overstates what we know. The
count and the direction (all early) carry the message. Rewritten (deployed this round): "it ended control early for
7 of them and late for none. Twenty-eight is too few to state a rate, so we give the count." The estimated-control-end
line keeps its rate: 146 of 778, range 16% to 22%.

D. Untested assumption in the runner: that the run contains every suite. It globbed tests/t_*.mjs, so a clone missing
a suite would report a clean pass on 18. Plant: a tree with 18 suites. Old runner: exit 0, 18 PASS and DONE, no
warning. New runner (allsuites_v2.sh): exits 3 with INCOMPLETE and the found and expected lists; it also ends with
DONE n/19 and exits 1 unless n is 19. Used for every run after the plant.

## Deploy record
- Team-heading match: engine files 53ca8a9. 19/19 before (hpre), staged (hstaged), after (hpost, fresh clone).
- Count line (challenge C): index.html f37c918 (md5 c3e08d1c), t_build fixture 3e2d184. Before = the hpost run on the
  same live page; 19/19 staged (lstaged), gate_index CLEAR, live md5 matched staged within a minute, 19/19 after
  (lpost, fresh clone, allsuites_v2). Value dumps unchanged: Desk c25bca11a598, grades 28cf6541870f. No corrections
  entry: no letter or grade moved.
