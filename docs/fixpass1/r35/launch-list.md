# Launch list: good7 to launch (Nov 12)

[Sean decides] Note A or B, plus the GM-line clause · Winter tier line in or out · Cards route: split build (ready) or unsplit files dragged in by hand · Go: approve the deploy commit in the session

| # | What | Owner |
|---|------|-------|
| 1 | Freeze the candidate: /tmp/deploy/good7. Rebuild it once more from the pinned run and confirm byte-identical. | Claude |
| 2 | Pre-deploy checks (checklist step 0): suites, letters/tiers/Wire/Desk censuses, size check, stamp check. | Claude |
| 3 | Put the census numbers from step 2 into the note Sean picks (see round35.md item 6). | Claude |
| 4 | The four [Sean decides] items above. | Sean decides |
| 5 | Optional rehearsal of the upload route: Sean creates a private throwaway repo by hand; then Claude runs the four-call upload there. Skip if not wanted. | Sean by hand, then Claude |
| 6 | Deploy commit: 8 files, four upload calls, one "Commit changes" (checklist step 1). | Claude, after Sean's go |
| 7 | Verify live (checklist step 2): md5 at the commit SHA, live md5, verify_stamps on live files, TARGET=live t_build/t_launch/t_wire/t_cards/t_nullgrades, letters census, returning visitor. | Claude |
| 8 | Rollback if a trigger fires (checklist "Rollback"). The rollback commit is a site change, so it needs Sean's word in the session too. | Claude, on Sean's word |
| 9 | Tests commit (fixtures, t_build, t_cards, t_nullgrades, grade-changes entry). | Claude |
| 10 | Publish the correction note on the site. | Claude, after Sean's pick |
| 11 | X posts. | Kirk |

After launch (decided, not blockers): B-R salary pull, 1998-2014 extension file, signing-bonus sourcing, offsExplorer test fix, cleanup of the slow-3G loading banner timing.
