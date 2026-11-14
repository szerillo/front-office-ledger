# Round 54 (Nov 14, 2026): launch path A labels. STOPPED before deploy.

Built (staged, not deployed): "under review: control-end data being corrected" labels on every value on the
known-wrong list (round 50 F1 vs live): a page note, the net value, the overall grade where it would move, each
channel whose number would move, and a letter label where the letter would move; the same label on the 19 winter
cards in the explorer and on the 19 winter share pages (title, description, preview image). No value changes.
The share generator (engine/share_live.mjs) writes the label too, so the daily share job keeps it.

Gates on the staged build:
- allsuites_v3: 19/19 (staged_suites.txt).
- Freeze check: Desk c25bca11a598, grades 28cf6541870f, published-service map 8ef3fd0a1c31, all identical to live.
  The 19 rebuilt winter pages keep every number (title, description and preview change only by the label).
- Index gate: CLEAR.
- Planted unlabelled page (ari card and o/2014-wsh.html without labels): review_check fails and names both
  (plant_result2.txt).
- review_check on the real staged build: FAIL, 107 + 19, not 108 + 19 (staged_result.txt).

Why it fails: one of the 108 listed regimes, sd-omar-minaya-/-aj-hinch-/-fred-uhlman-jr-(interim) (0.2 seasons,
2014), is shown on the site as a new seat with nothing to grade: no grade, no net, no channel. The engine computes an
overall grade for it, which is why round 50 counted it, but the page never displays one. So the live count of card
pages showing a value we believe is wrong is 107, not 108. Every one of the 107 is labelled exactly as listed.

Needs Kirk: approve 107 + 19 as the bar (and the check's expected list without that regime), then deploy as staged.
