# Round 32 (Nov 12, ~00:40 ET): Option A built (cards.js split in the build), nothing deployed

## 1. Split candidate (/tmp/deploy/good4)
split_cards.py runs inside build_site.py after the data files are copied. CARD_DETAIL (152 clubs) is cut by size
into cards.js (63 clubs, 2,007,672 bytes) and cards2.js (89 clubs, 1,963,450 bytes). cards.js starts cards2.js
itself, so the page's loader and page code are unchanged: index.html differs from good3 only in the cards.js ?v=
stamp (7e6428d93e to 0090cf05b3). Whichever part runs second calls cardsMerge(), and cardsMerge is called from
nowhere else, so the merge always sees all 152 clubs. Cost: cards2.js starts after cards.js arrives (serial, not
parallel). The 20 s "did not finish loading" banner still covers a failed second part.

Exactness: the build asserts the two halves rebuild the original JSON text byte for byte. Reassembled data md5
889c86e5 = original cards.js data md5 889c86e5. In a JS context, either load order gives 152 clubs, one merge call,
and the same object as the unsplit file.

Same numbers as pre-split:
- Suites: 14/15 PASS; t_fun 111/112 (offsExplorer, same pre-existing failure). t_build PASS with no fixture change
  (?v= is masked). t_grades PASS, 0 changed against the good3 fixture, so the 277 moved vs live stands.
- letters.mjs: L_g4.json byte-identical to L_g3.json, so still 102 grades vs live.
- Tier labels: 18. Wire census: 0 of 121.
- One md5: X0 to X6 built with the new build_site.py give 7 identical sites (every file). Z_X0 and Z_X6 (pinned
  names) give sites byte-identical to good4.

## 2. Split rollback set (/tmp/deploy/rb_split, eb310ee files)
cards.js 1,999,641 + cards2.js 1,962,591 bytes. index.html differs from live only in the cards.js stamp
(d7787e137c to 6969ce5e8d). Reassembled data md5 8e83ca4f = live cards.js data md5 8e83ca4f. letters.mjs census
on rb_split is byte-identical to the live census. Wire 0/121, tier labels 0. Deal Desk: all 50 verdicts
byte-identical to live.

## 3. Size check (size_check.py, also at the end of build_site.py)
Red (exit 3) when a file the deploy uploads is over 3.4 MB. With a base dir, files byte-identical to the base are
not uploaded and are only listed. Seeded: unsplit good3 RED (cards.js 3,970,686); unsplit rollback with the
candidate on main RED (cards.js 3,961,796); good4 and rb_split green; limit lowered to 3.0 MB on good4 RED
(index.html 3,317,020 and moves.js 3,076,537). Info: data/lvm_cache.json 5.2 MB, data/hist_results.json 7.7 MB,
data/pros_peak.json 3.6 MB are already in the repo over the limit and are not part of this deploy.

## 4. Upload routes (reported, not used)
The 3.6 MB limit belongs to the Chrome extension's file_upload call, not GitHub. GitHub's web uploader takes files
up to 25 MiB each when Sean drags them in himself; git push takes up to 100 MiB. Both are routes Sean can use by
hand. Neither is open to me under the standing rules (no push, no credentials), and in-browser assembly was the
route the permission check stopped.

## 5. Deal Desk check (prereg desk-prereg.md, md5 6731a653, written 05:31:46 UTC before the deal set existed)
Deal set: deals_gen.py seed 20261112, 05:34:25 UTC; FA totals frozen from live fair value at 05:34:47 UTC
(deals50_final.json md5 eacdb9ae). 30 trades, 12 FA signings, 8 draft packages; only players whose Desk row,
status and QO flag are identical on both builds. Graded on L (live), C (good4), R (rb_split), C' (good4 with live
MOVE_BANDS and DESK.deals), S (seed: dpw 2027 +10%).

Amendment 1 (after the first run, disclosed): the "tile numbers" capture was empty for 42 of 50 because trade and FA
verdicts render as a deal sheet. Numbers are now the deal-sheet rows, net line and tiles; "core text" is the verdict
minus comp boxes and GM lines. Both read from the saved verdict HTML, no rerun.

Results: E1 R vs L: 0 differences, full HTML. E2 FA, C vs L: 0 letters, 0 numbers, 0 core text. E3 trades and
draft, C vs L: 0 letters (none moved, though allowed), 0 numbers, 0 core text. Full HTML differs on 26 trades only in
comp boxes and GM lines (DESK.deals comps, GM style tags and trade-grade lines). E4 C' vs L: 0 letters, 0 numbers.
Seed S: 1 letter (F08), 8 deals' numbers, 14 core texts differ: RED, as expected. 3 trades show "Desk grade n/a" on
every build (T03, T05, T09). Not covered: extensions (the verdict reads form fields).
Harness note: dkFaVerdict with an argument is the Wire path, so FA text reads "Signed undefined"; this is the test
calling it without a date, not a page bug users see.

## 6. Name pin: is the live form what MLB.com shows?
No. Spot check of 5 of the 35 form differences on MLB.com and MiLB.com player pages: MLB uses the API form, the live
form matches Baseball-Reference's style.
- 115135: live "Ken Griffey", mlb.com/player/115135 heads "Ken Griffey Jr."
- 110184: live "Sandy Alomar", mlb.com/player/110184 heads "Sandy Alomar Jr."
- 124695: live "Eric Young", milb.com/player/124695 gives "Eric Orlando Young Sr."; MLB.com's bio is the same player
- 150285: live "Danny Kolb", milb.com/player/dan-kolb-150285 slug "Dan Kolb" (B-R uses "Danny Kolb")
- 408193: live "Kazuhisa Ishii", API "Kaz Ishii"; mlb.com/player/408193 bio text says "Kazuhisa Ishii": inconclusive
