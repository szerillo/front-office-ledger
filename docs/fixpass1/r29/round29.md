# Round 29 (Nov 11, late): checks before deploy

## Grades: the correction note's "No letter grade changed" was wrong
tests/tools/letters.mjs (this folder) reads every report-card grade (forGrade, each channel's g, success g),
every card decision's letter (gmMoveLetter) and every trade club's letter, using the page's own functions, on the
live page (eb310ee, index.html 5f430172) and on the deploy candidate. 102 grades differ (of 10,367):
- re-sign rule: 50 (21 report-card grades, 26 trade letters, 3 move letters)
- 2020 fix: 47 (32 report-card grades, 15 move letters)
- data (newer ledger): 4 report-card grades
- fix pass rules 1-14: 1 (PHI overall 45 to 50; Vasil's Rule 5 loss moved to the Mets)
Current clubs' overall grade: CHC 60 to 55, MIL 65 to 70, PIT 50 to 55 (re-sign rule), PHI 45 to 50 (fix pass),
SF 50 to 55 and WSH 55 to 50 (data). Full list: grade_changes_by_cause.json.

## t_grades regeneration (dry run on a copy)
UPDATE=1 with the reason below gives "277 grades moved, 558 new, 544 removed (of 13223)"; the 277 moved keys are
exactly the attributed set (163 re-sign + 107 2020 + 7 seat-label swaps), 0 extra, 0 missing.
Reason: Nov 12 deploy: re-sign rule (a same-club re-sign within 60 days keeps a trade open) and the 2020 charge
prorated to 60 of 162 games, plus fix pass 1 (deterministic reads; seat-label order).

## t_fun offsExplorer on eb310ee
PAGE = eb310ee index.html (5f430172): "offsExplorer": false, FAIL: offsExplorer (tfun_live.txt). Pre-existing.

## Headline names vs live
Current rule (ties to the higher id): 35 headlines name a different player from the same deal, 12 list the same
players in another order, 4 differ in spelling. "Most career WAR, then id" gives 39 different players: not better.
Spelling note: the archive spelling rule writes "R. A. Dickey" where live has "R.A. Dickey".

## Trade-reports content check
check_rumors.py: a fresh "checked" stamp is not enough; a listed player traded or extended since "updated" fails it.
Baseline on the current file: OK (40 rows).

## Ledger
data/ledger/draft_picks.jsonl.gz is now ledger_v3 (TEXT columns); restore_ledger.py rebuilds sweep_tx 6add0088 and
draft_picks b4564256, equal to ledger_v3.
