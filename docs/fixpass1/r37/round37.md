# Round 37 (Nov 12, 06:15 to 07:00 ET): everything up to the deploy commit, staged and dry-run

Decisions applied (Kirk): note A with the GM-line clause; tier line in (it passes the test bar); split cards route;
one-off rebuild of the 4 winters leaving the top/bottom 20; dry run instead of the repo rehearsal.

## Note
note-final.md. Version A, restructured: the old table's fix-pass rows no longer matched the final build (PHI waivers
now -0.5 to +0.2, PIT waivers 1.3 to 3.2, TOR international +4 with new data), so the table lists the six overall
grade changes with their cause. Rule counts recomputed by stage: 120 trade entries (re-sign 120, 2020 fix 0),
155 signing/extension entries (2020 fix 107, re-sign 48), 97 grades (2020 fix 47, re-sign 50). The old note's 122
mixed in data and seat-label moves. note_check.py recomputes every number from the live build and good7: 17 checks
green; seeded red for a wrong count, a wrong tier count, a wrong letter, a missing table row, a wrong winter total;
the old note A also fails it. The note is published as its own page (corrections/2026-11-12.html), a new file, so
the deploy's index.html stays as tested.

## Tier line: IN
"Eighteen winters change tier, among them WSH and LAA 2019, Catastrophe to Disaster": the count and both named
winters are recomputed from good7's offseasons.json by note_check (via offs_stamps.py).

## Winter pages
share_live.mjs now rebuilds every existing winter page whose text changed, including pages that leave the top/bottom
20. winter_pages_check.py: every o/ page's number equals offseasons.json. Live pages vs good7 data: 14 differ (red).
After 2b on the dry tree: 44 checked, 0 differ.

## Dry run (dry-run.log)
Local copy of the live tree served like Pages. Deploy 8 files, verify (md5s, stamps, 5 suites with TARGET=live
against the copy, letters census = good7, tiers 18, note check), 2b (28 winter pages), tests commit (all 18 suites
from the tree's own tests folder), rollback (rb5 files, cards2 part kept, census = live, winter pages 0 differ).
0 failures. Rollback of winter pages works by rerunning the same job: 44 checked, 0 differ.

## Challenge: WSH 2014-15 as the new No. 1 (wsh-trace.md)
+33.9 traces exactly from the contract book (Scherzer +11.1 to +12.2 from the 60-game 2020 charge). But WSH passes
Oakland only because Oakland's 2011-12 fell 0.9, and that comes from crediting Ryan Sweeney's 2013 Cubs season to
Boston after a pre-season release (the re-sign rule exposes an existing release-year rule). With the release-month
fix Oakland stays No. 1. So the No. 1 sentence is out of the note and no post claims it. Pre-existing on live for
50 pieces; after launch.

## X drafts
x-drafts.md: 3 drafts (2020-fix winters, the six grade changes, the Scherzer regrade). None claims a new No. 1.
