# Round 35 (Nov 12, ~02:45 ET): null grades fixed at the source, t_build rule redone, flakes traced. Nothing deployed

Candidate: /tmp/deploy/good7 (index.html 279c1e66). Rebuilds from Z_X0 and from Z_X6 give byte-identical sites.

## 1. Missing grade printed as a letter
Letter helpers: g2letter, gradeClass, deskLetter (moveGrade and wireWinterLetter already return null / a dash).
Measured, not guessed: an instrumented copy of each build logs every helper call that gets a null or non-finite
grade, with the calling line, while sweep.mjs renders home, leaderboard, DNA, boards, heists, offseasons, every
report card (152) and a Desk trade for every club.
Paths, counted on live and good6 (same counts on both):
- dev grade missing: 3 regimes (HOU, LAA, ATH). HOU and ATH are new seats, whose card shows "nothing to grade yet";
  LAA (Mozeliak) is not, and its report card prints "Player development F". Live today: 1 print (this one).
- overall/success missing: 3 (HOU, ATH, and an archive SD interim group), all new seats; guarded, 0 prints.
- new seat with 3+ deals: 1 (SD interim, archive); 0 prints.
- channel under MIN_N with deals: live intl 14, ext 5, draft 6, ret 1, trade 0; good6 the same plus trade 2 (ATH,
  HOU). These render through gradeChip (null shows a dot) or the Desk line fixed in round 34; 0 prints.
- missing team: 0.
Fix at the source (build_site.py): g2letter and gradeClass return the "not graded" dot and grey class for null or
non-finite; deskLetter returns the dot for a non-finite ratio; letterClass maps the dot to grey; the development
tile's tooltip says "Not graded yet"; the "On the field" tile no longer substitutes 50 (C+) for a missing grade.
Seed (every front-office grade set to null, everything re-rendered): good6 954 null calls, all 954 print a letter or
a colour grade, across 7 call sites (overall tile, success tile, development tile, home rows, home leaderboard,
share button, hub list). good7: 954 null calls, 0 letters. Real data on good7: 2 null calls, 0 letters (LAA tile now
shows the dot). New suite test t_nullgrades.mjs (helper unit checks + null-everything render): good6 RED (277 letters
on screen), good7 PASS.

## 2. t_build rule, redone
Round 34's rule (literal or JSON.parse declarations = data, plus any line starting with a bracket, quote or digit)
moved 175 lines to code but also hid 314 lines, including hand-written tables (MIN_N, CHANNELS, DNA_MET), 1,531
closing-bracket lines and 14 code lines starting with "[" (the grade-policy loops). Removing the bracket clause made
the engine's pretty-printed EXT_MAP block false-red on a data change (8 lines between the W3 and E3 stage builds).
Rule now: data = the 24 declarations the engine and the build write, by name, whole statement (line or block);
everything else is code. good7: 4,933 data lines, 11,738 code lines (round 31 rule: 6,319 data, 10,352 code).
- Clean rebuilds: Z_X0 and Z_X6 rebuilds: PASS, PASS (0 false reds). Stage builds RV3/W3/E3/X0 (data-only steps): 0
  code lines differ. good2 vs good5: only the 2 intended stamp lines.
- Seeds: MIN_N.trade 3 to 2: RED. good6 and good5 (old helpers): RED. The 339-line build: RED. A value changed inside
  EXT_MAP and inside AUTO_REGIMES: PASS (data).
- Still misclassified: anything inside a named block counts as data by design, including the hand-written empty
  default `let TRADE_BOOK = {trades: [], names: {}};` that the page uses until book.js loads. A change there passes
  t_build; only the grade and letters censuses would see its effect. An unknown new engine block goes red (safe side).

## 3. t_ui2
10 serial runs: 10 PASS (i42 timing 47-60 ms against a 400 ms limit). 3 full parallel suite runs: 3 PASS (50, 66, 58 ms);
under extra load (6 more page loads, 2 CPUs): PASS, 71 ms. The round 34 failure ran while a 50-deal Desk run was also
loading the page, and the old check could not say which half failed (market built, or render time). Cause is the
test, not the page: the page's cached render is about 1/6 of the limit. The check is now two checks plus the timing.
Also found: t_wire readersGrade failed in parallel run 3 (fixed 500 ms wait for five counter replies). Now polls up to
5 s; passes. t_fun offsExplorer fails on every run, same as live.

## 4. Upload rehearsal on a throwaway repo
Possible only by creating a new repository in Sean's GitHub account and uploading the site files into it. That is a
new thing in his account and the same upload the permission check stopped as a deploy step, so I left it. It is on
the launch list as optional: Sean creates a private repo by hand, then I rehearse there.

## 5. Launch list
launch-list.md: one ordered list with owners, the four Sean decisions in one block at the top.

## 6. Assumption tested: the 102 / 18 still describe what readers see after the round 35 helper changes
letters.mjs on good7 is byte-identical to good3's (102 vs live); tier labels 18; Wire 0/121; t_grades 0 changed in
all 3 runs. The census records grade numbers, so it cannot see a null printed as "F": the sweep covers that, and the
only such print on live (LAA development "F") becomes "not graded" on good7. So reader-visible grade changes are the
102, the 18 tier labels, the ATH Desk line (round 34) and the LAA development tile.
