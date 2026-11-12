# Round 49 (Nov 12, 2026)

Grades on published control end stay held. No engine run this round.

## 1. Disclosure lines (deployed)
Two methodology lines, each naming its own estimate and its measured error:
- Grading rule (control from the debut): early for 7 of 28 extended players with no arbitration figure and a public
  free-agent year (25%, 95% range 13% to 43%, small sample), late for none.
- Estimated control ends on the Deal Desk, simulator and club pages (our transaction count): off by a year or more
  for 146 of 778 published figures (19%, 95% range 16% to 22%); 126 of the 146 run late.
Intervals are Wilson 95%.

## 2. Calibration-freeze prereg (written, not run)
prereg_calib_freeze.md, committed b2477dc before any build or run. Freezes every fitted file at the live version
(trade, draft, extension-class, blend, arbitration rows, chart, plus the letter cutoffs and per-channel spread),
makes any fit-step write an error, and measures the re-fit path as its own run (R1) that is never deployed.
Bars: 0 untraced letters, 0 untraced overall moves, every changed number attributed, plus the round 47 bars.
Order: freeze check (byte-identical to live), spread plant, then F1.

## 3. Tracer fix (tracer only, no regrade)
eval_i1_v2.py folds names on both sides (NFKD, accents stripped, case folded) and stops escaping non-ASCII before
matching. Plant plant_tracer.py ("Jesus Luzardo" in the engine row, "Jesús Luzardo" in the player file, plus an
unrelated name that must not trace): old evaluator exit 1, new exit 0. Not re-run on I1. From the round 48 diagnosis,
the fix moves exactly one item (Phillies extensions) from untraced to traced, so I1 would still fail.

## 4. Kinley prereg (no build)
prereg_kinley.md, committed b2477dc. After an elected-free-agency exit, an ASG to an MLB club between Nov 1 and Opening
Day counts as on only if the player is on that club's 40-man roster the next day (league roster service; Kinley is
on Atlanta's 40-man on Jan 15, 2026 and the active roster on Mar 26, 2026). Sample of 20 drawn only after the file is
committed; bar 19 of 20, Kinley 2026 at 172, all existing plants pass.

## Challenges
A. Every name-based join that can reach a live number, and how many accented players fail today:
- Trees page projection (treeProj, exact name against the Desk): 15 names, 1 with diacritics, 0 accent misses.
  3 names miss outright (Cobb Hightower, Tyson Neighbors, Tanner Smith: prospects not on the Desk; the node shows no
  projection rather than a wrong one).
- Deal Desk and simulator search (dkFindPlayer): exact, then accent-folded, then unique prefix. 0 misses by design.
- Trade-tree side values: folded and substring matched. 0 accent misses.
- Trade reports (rumors.json), Wire (wire.json), share pages (share.json): joined by MLBAM id, not by name.
- Service-time fallback (published figures): NFKD name match. 31 accented MLBTR rows, 0 unmatched for accents; the 13
  unmatched rows are nicknames or name changes (Dee Gordon, Zach Britton, Nori Aoki, Felipe Rivero and others).
- Engine contract book (feeds every signing and extension grade): 3,608 contracts, all carry an id; 84 accented names,
  0 failures. 13 names differ from the player file only by a suffix (Jr., Sr., III); checked by era, all on the
  right player (Tony Gwynn 1997 and 2000 on the father, 2010 and 2011 on the son).
- One name-matched script that is not on a live path: engine/arnold_ledger.py (a proof of concept, LIKE match on
  names, so an accented name in its crosswalk would not match). Nothing on the site reads it.
Live wrong numbers from accents: none found. The only accent miss was in the round 47 evaluator.

B. No. The deploy path never re-fits: it uploads index.html (and once rumors.json) and never runs the engine. Byte diff
of every graded letter and number (152 cards, 942 channels: letters, nets, overall grades, totals) before and after
each deploy, served locally from the exact commits:
- 9c6a0fc (r48 Kurtz/Horton) vs a48e27b: 0 changes.
- fec1e64 (r47 control-end mark) vs d845b74: 0 changes.
- 6477985 and b91f777 (r46 published service, rumors) vs af2df70: 0 changes.
- 0ece84c (r45 band-test line) vs f508434: 0 changes.
All eight dumps hash to the same md5 (28cf6541870f), and every content-hashed data file is byte-identical across the
four pairs. The re-fit only happens inside an engine run, and none of these four deploys ran one.

C. Three Luis Garcias, all keyed by MLBAM id on every live page:
- 671277 Luis García Jr. (1B, Yankees since the Aug 3, 2026 trade): Desk row NYY, counter 5.143; MLB Trade Rumors lists
  him at 5.142 under the Yankees, but the name match could not place it (two Yankees fold to the same name).
  Hand-checked and fixed: a hand-resolved figure (HAND_SVC) now gives him 5.142, control end 2027 unchanged, the
  estimated tag drops. His 2026 trade card and 2020 contract selection carry id 671277.
- 677651 Luis Garcia (RHP, minor league deal with the Yankees, Scranton): Desk row NYY, counter 5.083, estimated. Not
  on the 2027 MLBTR list, so nothing published to apply.
- 472610 Luis García (RHP, born 1987, Desk row MIN): every card entry (2020 to 2026 signings, the 2024 Angels to Red Sox trade,
  the 2025 Nationals to Angels trade, waiver and walk rows) carries 472610.
Name-only rows (no id) were checked by hand: deals.js 2018 PHI to LAA (Jose Alvarez trade) is 472610, matching his
transaction record; the 2023 Angels free-agent row (1 yr / $4M, age 37) is 472610. No page shows one player's numbers
under another's name.

D. Untested assumption in the freeze design: that the calibration files are the only fitted state. The grading spread
(per-channel standard deviation and the letter cutoffs) is also fit from the run's own outcomes; round 48 showed two
letters move with no entry moving (Phillies under Klentak, Red Sox under Duquette). Plant (step 2 of the prereg): with
the freeze on, add +5.0 to one extension entry of one front office and re-grade. Pass: that front office's net moves by
exactly 5.0 and no other front office's letter, net or rank moves. On a design that freezes only the calibration files
the plant fails (the spread re-fits and other letters can move), which is why the prereg freezes the spread too.

## Deploy record
Gates: 19/19 suites on live before (e5ce7ec), 19/19 on staged (fixture re-pinned locally first), gate_index CLEAR.
Desk diff live vs staged: 1 of 1,982 players changed, as predicted (Luis García Jr.: estimated flag 1 to 0, control end
2027 unchanged, surplus unchanged). Graded letters and numbers: staged dump md5 28cf6541870f, identical to live.
Commits: preregs b2477dc (before any run), index.html 4b8538a (md5 d4baadb7), t_build fixture fbec748. Live md5 matched
staged within a minute. Post-deploy: 19/19 on a fresh clone, run under the suite lock. No corrections entry: no
letter or grade moved.
