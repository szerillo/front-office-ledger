# Round 55 (Nov 14 audit fixes)

New checks (each with one planted failure, plant_results.txt):
- preview_check.mjs: card share pages and preview images (via og/cards-manifest.json md5) match the live cards; club share pages match the team view.
- tradetotal_check.mjs: the "Every trade" table states its true sum and explains any gap to the trade grade.
- corrlinks_check.mjs: footer and review labels link the corrections log; sitemap lists log, c/, t/, s/, o/, h/ and no noindex page.
- rawtxt_check.mjs: no "traded player, " placeholder or cut "St. Louis Cardina".
- method_check.mjs: methodology numbers equal the chart and the weights the grades use.
- winterlink_check.mjs: #view=winters&id= opens any winter (season form and old club codes too); a bad id says so.

First deploy went red (t_grades, keys built from headline text the tidy changed; values unchanged), so index.html and
the fixture were rolled back (c2e9956, ee468b4), the test key was fixed (aae64bd, old test fails on the staged page:
plant_t_grades_old.txt), gates re-run (staged 19/19), and index redeployed (2b47aca, 791f847). Post: 19/19.
Rollback: python3 rollback_r55.py <out dir> (tested, rollback_test.txt).
