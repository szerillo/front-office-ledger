# WEEKEND RESUME (written Nov 12, 2026, ~16:20 ET; thread paused)

## Live state
- Repo head when paused: see the commit that adds this file (docs only after the last site deploy).
- Last site deploy (green): index.html f37c918 (md5 c3e08d1c55faed0aac0c37bff63e024c), t_build fixture 3e2d184.
  Since then only docs and engine/ files (engine/ is not served by the site).
- Pause check (fresh clone at ad3019f): allsuites_v3 19/19 (counts in docs/fixpass1/r53/weekend_suites.txt);
  live index md5 = repo md5; gate_index CLEAR (8 data files live with the right bytes); value dumps unchanged:
  Desk c25bca11a598, grades 28cf6541870f, published-service map 8ef3fd0a1c31.
- What is public: grades on the debut-based control end, with the "depends on control end" chip on 133 letters and
  two methodology lines on control-end error; Desk control ends official for 293 MLBTR players plus Kurtz, Horton
  (rookie award credit) and Luis Garcia Jr. (hand-checked), every other control end marked estimated.
- Nothing is mid-run or half-deployed. No sandbox job is running.

## Launch blockers, in order (each with next action and pass bar)
1. Control end in past grades (F2). 108 of 152 card pages and 19 of 44 winter share pages show a value believed
   wrong. Kirk ruled a chip alone is not enough; launch waits.
   Next action, pick one (Sean or Kirk):
   - B (fix first): write a new prereg whose plant perturbs control spans, not wins (the round 52 wins plant moves
     fits the rule never touches, e.g. contract_book typical_fa). Order: record run, freeze check, control-span plant
     on the unfrozen run (must trip), then frozen (must pass), then F2 once.
     Pass bar for F2 (prereg_r51.md): 0 untraced letters, 0 untraced overall moves, every changed number attributed
     (nets, entries, trades, winters), no inventoried fit differs from live, letters changed at most 150, overall at
     most 40, TOR 2012-13 in top 2 with 90% of margin. If it passes: re-grade deploy with allsuites_v3 green before
     and after, staged diff = only the predicted 108/19 pages, post-deploy verify, rollback tested, corrections entry
     naming the count.
   - A (cheapest honest launch, about an hour, index.html only): page note on the 108 cards and 19 winter pages,
     and "under review" instead of a letter on the 58 channel letters and 26 overall grades round 50's F1 says would
     move. Pass bar: allsuites_v3 19/19 before and after, staged diff touches only those pages, value dumps otherwise
     unchanged.
2. Pre-season release rule: on the corrections page as a known open item (92 trade-side numbers, 59 winters, up to
   1.9). Parked; needs its own prereg (round 39 run failed its bar).
3. Innings decimals (155.1 read as 155.1, not 155 1/3): 712 trade numbers and 315 winters, at most 0.4 (measured
   unfrozen). After launch, its own run.
4. Precision after launch: Desk estimated control ends, the counter gaps below.

## Held items
- Grades on published control end: HELD (rounds 47, 50, 51, 52 stopped by their bars).
- Innings decimals: HELD, after launch.
- Kinley rule (re-signing filed as "assigned to <MLB club>" counts only if he is on that club's 40-man the next day):
  re-score with truth v2 PASSED 19 of 19 (round 52); NOT built. Next: a build GO, then a plant, dry run, no regrade.
- Same-day contract selection plus option order (Morgan 2026, 11 days): 1 of 184 frame player-seasons. Not built.
- Under-20-day option rule: 53 of 184 frame player-seasons (46 players) have 1 to 19 option days; crediting them
  changes 28 player-seasons, max 28 days, 206 in all. Not built.
- Desk estimated control ends: about 684 players on our transaction count, labeled estimated, with the measured
  error disclosed (146 of 778 off by a year or more, most run late). Waits for MLBTR's 2027 figures to finalize
  (signal: the "not finalized" sentence leaves the 2027 post; first re-pull Nov 12: 0 of 296 changed).

## Frozen preregs and amendments waiting for a GO (docs/fixpass1/)
- r51/prereg_r51.md (28d2959) + r52/amendment_r52.md (55394df): stopped at guard (c). Needs a new plant (control
  spans) before it can reach F2.
- r52/prereg_kinley_truth_v2.md (55394df): run and passed; the rule build needs a GO.
- r49/prereg_kinley.md (b2477dc): superseded by truth v2 for scoring.
- r38 pre-season release prereg (dd3d4a8): failed in r39; a retry needs a new prereg.

## Known wrong on live (current)
- 108 of 152 front-office card pages and 19 of 44 winter share pages (control end; round 50 F1, frozen run).
- Within those: 58 channel letters and 26 overall grades would move.
- Plus the known open items on the corrections page (pre-season release rule) and the small innings item.

## Decisions for Sean
- Launch path: A (labels now, launch sooner) or B (fix first, about two to three hours of runs if every stage passes).
- X drafts and the trade-reports skill card are his (untouched).
- Weekend restart: say which path, then the first action is the control-span prereg (B) or the label build (A).

## How to resume the sandbox (if it was reset)
- Everything that lived only in the sandbox is in docs/fixpass1/r53/sandbox_state_nov12.tar.gz (manifest beside it):
  the live-run engine (engine_f, which differs from repo engine/), engine variants as diffs (i, zf, zi, yf, yi),
  baseline run outputs (Z_X6 graded files, champs file), frozen calibration files (r50) and replay files (r51),
  evaluator inputs (new.json, ch.json, svc_rows.json), the step driver, guard and index gate.
- Not committed: the frozen network cache /tmp/v2/http (161 MB) and the Kinley roster cache (64 MB): too big for the
  web uploader. Rebuild needs network access (guard record mode) and may differ from the frozen vintage, so a
  rebuilt baseline must first reproduce live byte for byte (the freeze check) before any run is trusted.
- Runner: tests via docs/fixpass1/r51/allsuites_v3.sh (expects count_checks.py at /tmp/r49/count_checks.py; copy it
  there or edit the path).
