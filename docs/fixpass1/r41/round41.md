# Round 41 (Nov 12, 07:55 to ~08:15 ET)

## Item 1 + 2: winter rank wording fixed, methodology line added. DEPLOYED, all gates green
Rule (generator, engine/share_live.mjs): a winter page shows a rank only inside the 20 best or 20 worst, ranked on
the shown value (one decimal); exact ties share a rank (T-18); a page outside the 20s shows no rank. WSH/ATH keep
"too close to rank". Pages whose text changes: 7 (under the 50 stop line); every number unchanged.
- 1998-sd: "The #18 best" to "The T-18 best"
- 2006-sd: "The #19 best" to "The T-18 best"
- 2012-mia: "The #20 best" to "The T-18 best" (all three at +19.5)
- 2019-laa: "The #29 worst" to "A -16.8-win offseason"
- 2019-wsh: "The #26 worst" to "A -17.4-win offseason"
- 2020-nym: "The #21 worst" to "A -19.1-win offseason"
- 2021-tex: "The #675 worst" to "A +18.2-win offseason"
Preview kicker for no-rank pages: "One winter, every move graded".
Methodology (index.html, one sentence after the 20-80 scale line): "Letters are relative: the spread is measured
across every front office, so when other records change, a letter can move one step even if this front office's own
numbers did not." Same line added to the build source (/work prototype) so the next build keeps it.
Corrections page: two lines (the 7 pages, with #675; letters are relative, 6 moved that way, Minaya C to D+).
Staged diff, 18 files: 7 og/o images, 7 o pages, corrections page, index.html, tests/fixtures/page_code.json
(t_build re-pin, sha 9dfce0828ed1e47d, reason recorded), engine/share_live.mjs.
Commits: daddea2 og/o, c626510 o, 93c261e corrections, 4013754 index.html, 340181a t_build pin, c5f0368 generator.
(c16e633 after them is the scheduled trade-reports job, rumors.json only.)
Before (staged tree served locally, PAGE set): t_build, t_launch, t_wire, t_cards, t_nullgrades all exit 0 PASS.
After: live = staged for 18/18 at 13:10:32 UTC (Pages took ~3 min to start serving the batch; engine and fixture
checked on raw main). Fresh clone + cache-busted live files (index 80c040f7, data md5s unchanged):
TARGET=live PAGE=/tmp/r40/r41/post/index.html t_build exit=0 PASS
TARGET=live PAGE=/tmp/r40/r41/post/index.html t_launch exit=0 PASS
TARGET=live PAGE=/tmp/r40/r41/post/index.html t_wire exit=0 PASS
TARGET=live PAGE=/tmp/r40/r41/post/index.html t_cards exit=0 PASS
TARGET=live PAGE=/tmp/r40/r41/post/index.html t_nullgrades exit=0 PASS
Rollback set: /tmp/r40/r41/rollback (main versions of all 18). Not needed.

## Item 3: hash-name fix, t_build re-pinned and a deploy gate (staged, not deployed; see hash_gate_dryrun.log)
Re-pinned t_build masks hashed names the way it already masks ?v= stamps, so a data refresh does not fail it.
Consequence: t_build catches seed 1 (a reference reverted to a plain name: page code changed) but not seed 2 (data
bytes edited) or seed 3 (wrong name planted); t_hashnames catches all three. Not masking would make t_build catch
seed 3 too, but it would then fail on every data refresh. The two tests together are the guard.
gate_index.py refuses (exit 3) to clear index.html until every data file the staged page loads is served with 200 and
the md5 its name claims: refused before data, refused on one wrong-bytes file, cleared when all right, page fine after.

## Check A: WAR spot-check (pre-registered in prereg_warcheck.md before fetching)
Last refresh 46ddec3 to 0a9f2bd changed 0 existing values and added 163 rows, so "largest movers" = the 10 largest
added rows; plus 10 random 1998+ rows (seed 20261141). Reference: Baseball-Reference WAR, daily WAR files dated
Nov 6 2026 03:08 UTC (batting + pitching WAR per stint, matched on MLBAM id). Ledger WAR is our own build, so the
bar is: wrong club, gap over 1.0 win, or a sign flip with both sides 0.5+. The 1.0 is a judgment, not measured.
Result: 18 of 20 pass; club matches 20/20. Fails (both random rows, size):
- Phil Hughes 2015 MIN: Ledger -0.08 vs bWAR 1.77 (gap 1.85). Not explained yet; worth a look at the pitcher path.
- Adam Kennedy 2002 ANA: Ledger 2.82 vs bWAR 4.54 (gap 1.72). bWAR rates his defense highly; likely model, unconfirmed.
Gap overall: mean -0.22 (Ledger lower), SD 0.64, mean absolute 0.43, n = 20.

## Check B: where 0.5 came from
Not from a measured error. It was a judgment: display rounding (true gap 0.4 to 0.6) plus single model choices that
moved a total 0.3 to 0.5. A rough read of A says it is far too small: a winter total sums ~30 to 45 player-seasons
(WSH 2014-15 about 31, ATH 2011-12 about 45); with the measured SD of 0.64 per season and independent errors, the
difference between two such totals has an SD near 5.6 wins, and the -0.22 mean offset alone moves ATH against WSH by
about 3 wins. Rough (n = 20, independence assumed, bWAR is not truth). Proposed method in prereg_rank_threshold.md:
300-season disagreement sample, 2,000 resampled draws per winter, a rank shown only if it holds in 90% of draws.

## Check C: an untested assumption under the live build
Assumption: the page works the same in Safari's engine. Every suite runs Chromium; iPhone visitors get WebKit.
Test (engines.mjs): the live page in Chromium and WebKit 26.6 (Playwright), same iPhone 13 profile. Both: cards and
moves ready, no banner, 0 page errors, 152 clubs, 4,178 trades, 816 winters, CHC 55, Minaya 40, an identical
signature over every report-card grade, method/trees text identical. Wire and leaderboard text differ only in the
dropdown option labels (Chromium includes <option> text in innerText, WebKit does not), not in content. Passed.
Not covered: real iOS Safari memory limits and older iOS versions.
