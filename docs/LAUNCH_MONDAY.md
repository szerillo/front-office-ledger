# LAUNCH MONDAY (Nov 16, 2026)

## Status
- Live: index.html 73a1aab (md5 a47cecdea9574a0469e9266f8fb71c4b), fixture cddc599, winter pages 2cc2e9a, previews 294c7f3,
  corrections 85e7f1f, share generator 246b57c. Deployed Sat Nov 14.
- Post-deploy: live md5 = repo; label check on the live site PASS (107 cards, 320 explorer winters, 19 winter pages,
  0 problems); value dumps unchanged (Desk c25bca11a598, grades 28cf6541870f); index gate CLEAR; allsuites_v3 on a
  fresh clone: see docs/fixpass1/r54/post_suites.txt.

## Launch blockers
None. Every value we believe is wrong is labelled "under review: control-end data being corrected".

## Known wrong, labelled (control end counted from the debut)
- 107 front-office report cards: page note and net value labelled; 58 channel letters and 25 overall grades carry a
  letter label; every channel whose number would move is labelled.
- 320 winters in the explorer, 19 of them with share pages (title, description, preview image labelled).
- Lists: docs/fixpass1/r54/review_expected.json (what must be labelled) and believed_wrong.json (current value and
  the value the corrected re-grade is expected to show, from round 50's frozen run; provisional).
- Left out on purpose: the 2014 Padres interim (Minaya / Hinch / Uhlman, 0.2 seasons): the site shows it as a new
  seat with no grade or numbers.

## Known open items, disclosed (not control end)
- Pre-season release rule: on the Nov 12 corrections page (92 trade-side numbers, 59 winters, up to 1.9 wins).
- Innings read as decimals (155.1 not 155 1/3): small (at most 0.4), not labelled, fixed after launch.
- Desk control ends marked estimated for players without published service time (error disclosed in the methodology).

## Sean does these himself
- X posts for launch: the drafts are his; nothing has been posted.
- The trade-reports skill card (rows must carry club and date): his to accept.
- Any announcement (X, newsletter, Action Network).
- X preview cache: for the 19 winter pages, X may show the old preview image (no label) until it re-crawls. Posting
  a link fresh after Monday, or re-validating the card, refreshes it.

## One-command rollback
    python3 docs/fixpass1/r54/rollback_r54.py rollback_out
Downloads the pre-deploy files (commit 579b86d) into rollback_out with their repo paths and checks the index md5
(c3e08d1c...). Then upload rollback_out through the GitHub web upload page, folder by folder (o/, og/o/, corrections/,
root index.html, tests/fixtures/, engine/), and run the label check: it should report 0 labels. Tested Nov 14 on a
local copy: md5 matched and 0 cards, 0 winters, 0 pages labelled.

## After launch, in order
1. Control-span prereg (draft: docs/fixpass1/r54/postlaunch_item1_control_span_prereg_DRAFT.md), then F2, then the
   re-grade that removes the labels.
2. Innings decimals.
3. Kinley rule build (truth v2 passed 19/19), same-day option order, under-20-day option rule.
4. Pre-season release rule (new prereg).
