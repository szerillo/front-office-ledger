# Round 31 (Nov 12, ~00:15 ET): deploy step 2 done; deploy step 3 blocked by an upload limit

Final build (good3): engine deploy-candidate + pinned names + data-file hash stamps + tree-text fix.
index.html 507b2e47, book.js 4e6757e8, deals.js a8327e0c, cards.js 7e6428d9, moves.js 3be8d310,
offseasons.json ec6b882c, trade_parts.json 9f438cf9.

Suites (15): 14 PASS; t_fun 111/112 (offsExplorer, same failure on eb310ee). t_build fixture regenerated (reason:
data-file stamps), t_grades fixture regenerated (277 moved, the attributed set). Census: letters.mjs 102 grades vs
live (unchanged), offs_stamps.py 18 winter tier labels, Wire census 0 of 121 current-winter items differ.

Pinned names, independent check against the MLB people API: 5,333 of 5,534 exact, 165 differ only in accents,
periods or spacing, 35 in form (Jr./Sr., nicknames such as Al Reyes for Alberto Reyes), 1 not in the API.
8 players are not pinned (new since the live build) and take the latest feed name.

Data URLs in the built page: cards.js, moves.js (md5 prefix), book.js, deals.js (sha1 prefix), offseasons.json,
trade_parts.json (md5 prefix, new); rumors.json and share.json (?h= hourly), wire.json (no-store), dudes.json (?v=3,
fixed; not part of this deploy). Returning-visitor test (Pages-style max-age=600, no interception): unstamped build
mixes new report cards with old winter data (WSH 2019 -22.7); stamped build gives the new data (-17.4).

Census gaps, seeded: a Wire data change (waiver move bands +0.6): Wire census RED (16 items), letters.mjs green,
offs_stamps green, t_build green. A Deal Desk letter cutoff change (page code): t_build RED, the rest green.
A Deal Desk data change would be caught by none of them; DESK data differs live vs candidate (newer players).

Deploy-day assumption tested: cards.js (3,970,686 bytes) is over the Chrome upload bridge's 3.6 MB per call, so it
cannot be uploaded the way the runbook says. Staging it in two parts was stopped by the permission check as a
production-deploy step; nothing was committed (HEAD stayed 0c929bd).
