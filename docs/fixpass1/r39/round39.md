# Round 39 (Nov 12, ~07:05 to 08:00 ET): post-deploy checks, pre-season release run (FAILED bar 2, not shipped)

## 1. Live suites rerun, PAGE set explicitly, cache-busted live files (fresh index 279c1e66)
First attempt ran from a folder holding only tests/: t_wire crashed before any check (ENOENT ../dudes.json, exit 1).
Rerun from a full checkout of main plus the downloaded live files:
TARGET=live PAGE=/tmp/golive/tree2/index.html t_build exit=0 PASS
TARGET=live PAGE=/tmp/golive/tree2/index.html t_launch exit=0 PASS
TARGET=live PAGE=/tmp/golive/tree2/index.html t_wire exit=0 PASS
TARGET=live PAGE=/tmp/golive/tree2/index.html t_cards exit=0 PASS
TARGET=live PAGE=/tmp/golive/tree2/index.html t_nullgrades exit=0 PASS
Runbook fixed (go-live-runbook.md): every live suite sets PAGE and runs from a full checkout.

## 2. Pre-season release rule, run under dd3d4a8: BAR 2 FAILS. Not deployed, not rerun, nothing tweaked
Engine g = engine f plus the one pre-registered line. Two runs (P0, P1) on ledger_v3, names pinned.
BAR 1: window end changed for 52 pieces; listed 52; missing 0; extra 0. PASS.
BAR 2: FAIL. The bar says any seat that moves without a listed piece fails. 2 seats move in a trade with no listed
  piece: 2022-07-11 KC -0.1 and ATL +0.1 (the Drew Waters trade; every piece in it is unchanged in trade_parts).
  Cause: the rule also shifts the prospect calibration (trade_calib.json: unranked 0.453 to 0.452 and the maturity
  curve m; draft_calib.json too), which moves the expected value of open trades that hold prospects. The rule is not
  local, as the pre-registration assumed.
  Also: 36 seats moved 0.5+ where the estimate gave a direction, 0 against it; 18 more moved 0.5+ where the WAR-only
  estimate was under 0.05 (it missed salary in the dropped season), so they have no estimated direction.
  Disclosure: my first bar-2 script counted seats missing from the estimate's seat list (24) instead of seats in a
  trade with no listed piece (2). Either way bar 2 fails.
BAR 3: P0 vs P1, 9 published files, 0 differing. PASS.
Bars 4 and 5 not run (stopped at the first failure, per the go).
For the record (not shipped): with the rule, WSH 2014-15 33.9, ATH 2011-12 33.8 (25.4 + 8.4).

## 3. Challenge A: do the 102 grades and 18 tiers trace to logged causes?
Grades (letters census, stage builds): 2020 fix 47, re-sign rule 50, fix pass 1 (PHI overall 45 to 50),
newer data 4 (SF overall 50 to 55, SF trade 65 to 70, WSH overall 55 to 50, and NYM Omar Minaya trade 45 to 40).
grade-changes.md logs the two rules and the fix pass (98). The 3 SF/WSH data changes are in the note.
Does not trace: NYM Omar Minaya (2004-10) trade grade C to D+. His trade net (-8.9), deal count (39) and seasons (6.2)
are identical on live-before and now; the letter moved at the ledger-rebuild stage. Probable cause: page grades are
scored against all regimes, so other regimes' changes moved his band. Not verified; open.
Tiers: 18 = 2020 fix 15 (all 2018-19 winters) + re-sign 3 (MIA 2010, MIA 2014, ATL 2022). All trace to logged rules.

## 4. Challenge B: the ~30 s mixed window (old index.html, new data files), tested locally over http like Pages
No error and no loading banner (0 page errors, 152 clubs, cards ready). But a card could contradict itself: the old
page carries the old grades inline (CHC overall 60, waiver -2.3) while cards.js, book.js, moves.js and
offseasons.json load the new details (CHC waiver ledger row "Megill -4.4", 4,178 trades, new winter totals).
So during the window a visitor saw old letters next to new rows; no wrong letter was computed, but the page was not
self-consistent. Cause: the page asks for data files by ?v= query and Pages ignores the query. Fix for next
deploys: name every data file by content hash (as cards2 already is) and never delete the old ones.

## 5. Challenge C: WSH vs Oakland
Displayed: WSH 2014-15 +33.9 (21.9 + 12.0), ATH 2011-12 +33.4 (25.0 + 8.4). From display rounding alone the gap is
0.4 to 0.6, so rounding cannot flip it. Model choices can: each known single choice moves one side 0.3 to 0.5
(the pre-season release rule run puts Oakland at 33.8; a day-based 2021 share for Scherzer is about -0.3 for WSH).
No statistical interval exists for these totals (WAR has no error term in the model), so the honest range is "too
close to rank". Live "#1" wording about winters, all from data, none from the note:
- o/2014-wsh.html description: "The #1 best offseason since 1998, under Mike Rizzo ..."
- og/o/2014-wsh.png (the X/link preview image): "The #1 best winter since 1998 · Mike Rizzo"
- o/2011-ath.html description and image: "The #2 best offseason since 1998"
- the offseason explorer's rank chip on the page (#1 Rizzo, #2 Beane), computed live
- the corrections page and the X drafts: no #1 claim
Other "#1" on live are draft picks and prospect ranks, unrelated. Recommendation (Kirk's call): soften the top two
share pages to "one of the two best offseasons since 1998" while the gap is under 0.5.

## 6. Challenge D: a check that only compared against my own staged files
"Live data equals the engine output" was only shown by md5 against my staged build. Independent check: the live
page's regime data (read from frontofficeledger.com) against the pinned engine run's own output files
(sweep_results.json, hist_results.json): 152 of 152 regimes, 0 channel nets and 0 deal counts differ. Shown grades
are recomputed on the page by design (relWeights composite, MIN_N, new seats), so they differ from the engine's raw
grades (382 channel, 123 overall); the page side is what the letters census covers.
