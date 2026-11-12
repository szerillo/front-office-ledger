# Round 30 (Nov 12, early): reconciling counts, coverage, spelling, caching

## 1. Counts
The t_grades fixture holds values (13,223 trade-seat nets and card-row numbers); letters.mjs holds grades (letters
and 20-80 grades). They are different populations:
| t_grades value moved (277) | page grade also changed |
|---|---|
| 122 trade-seat nets | 26 trade letters changed, 96 the same letter |
| 155 card rows | 16 move letters changed, 139 the same letter |
Page grades with no fixture key: 58 report-card grades (channel and overall grades are not in the fixture) and 2 move
letters that moved because the 2020 fix shifted the move percentile bands, not their own value. 102 = 26 + 16 + 58 + 2.
97 in the note = the two rule updates (re-sign 50 + 2020 47); the other 5 are data (4) and the fix pass (PHI, 1).
Headlines 36 vs 35: 36 was counted on the v2 build without the re-sign rule; on the final build the ARI 2014-12-12
Miley trade's value moved (re-sign rule), so it no longer pairs with live by date and value and drops out of the
"same value, different name" count.

## 2. CHC 60 to 55, by hand
Only CHC's waiver channel moves: -2.3 to -6.7, one row: Trevor Megill, lost on waivers to MIN 2021-11-30 (0.0 to
-4.4). He elected free agency that day and re-signed with MIN on a minor-league deal on 12-01; the re-sign rule
(asset_rules.py:326 _resign_skip, used at :356) keeps his window open, so his next four seasons (MIN 2022 0.86, MIL
2023-25 1.24 + 1.03 + 1.41, before salary) now count. Page composite (index.html applyGradePolicy/compGrades):
live gn = 0.706(-2.9) + 0.5(-3.0) + 0.591(-2.3) + 0.68(9.6) + 0.5(0.2) + 0.667(3.4) + 0.5(11) = 9.489; /8 = 1.186;
/SD 3.308 = z 0.359 -> 60 (z >= 0.30). Candidate: waiver -6.7 and the ext weight 0.660: gn = 6.865; /8 = 0.858;
/SD 3.303 = z 0.260 -> 55 (0.12 <= z < 0.30). Matches letters.mjs.

## 3. Coverage
letters.mjs reads data after load, not rendered tabs: 149 regimes' report-card grades (982), 1,003 decision letters,
8,395 trade-club letters. It does not read: the 816 winter tier labels (offsStamp), Deal Desk letters, the live
2026-27 Wire and winter letters (computed from the live feed). Seeded test: BOS 2004 winter set to 25.0 ("A wash" to
"All-timer"): letters.mjs saw 0 differences; offs_stamps.py went red. offs_stamps.py on the candidate: 18 winter
tier labels change (all from the 2020 fix and the re-sign rule; e.g. WSH 2019 Catastrophe to Disaster).

## 4. Spelling (amendment 5, f745dbe, pre-registered before coding)
Expectations met: exactly 13 names changed against the candidate, all back to the live spelling (R.A. Dickey,
A.J. Burnett, Ivan Rodriguez, Michael Morse, Jerry Hairston Jr., ...); 0 of 5,534 differ from live; spelling-only
headline differences 10 to 0; winter numbers unchanged; X0 and X6 reruns give one md5 (offseasons ec6b882c).

## 6. Caching (untested assumption, now tested)
Pages serves everything with max-age=600. offseasons.json and trade_parts.json were requested as ?v=1. With a local
server sending the same header and Chrome's cache on: a visitor who loaded the old site and comes back after the
switch got the new page (CHC waiver -6.7) with the old winter data (WSH 2019 -22.7). build_site.py now stamps both
files with their content hash; the same test then gives -6.7 and -17.4.
