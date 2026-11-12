# Go-live runbook (fixed Nov 12 after the deploy: every live suite sets PAGE and runs from a full checkout)


Everything below was run end to end on a local copy of the live tree at 06:15 ET (dry-run log: dry-run.log, 0 failures).
All uploads go through the GitHub web upload page in Sean's Chrome. Nothing is deleted at any step.
Staged files: /tmp/stage/deploy (8), /tmp/stage/tests_commit (17), /tmp/stage/note/corrections/2026-11-12.html,
/tmp/stage/rollback (8 + 40 o/ + 40 og/o + share.json). U = https://frontofficeledger.com/

## T-30 (10:45 ET) Pre-flight, Claude, no site change
| Command | Expect | Abort if |
|---|---|---|
| curl -s "$U?t=$(date +%s)" \| md5sum | 5f430172... (live unchanged) | anything else: stop, find out who changed the site |
| main commits page | top commit is a docs/fixpass1 notes commit or 88fefaf-era notes only | a site file changed since 5f4dc44: stop |
| cd /tmp/stage/deploy && md5sum * | index 279c1e66, book 4e6757e8, deals a8327e0c, cards d3e5a831, cards2.d7fb83c8d5 d7fb83c8, moves 3be8d310, offseasons ec6b882c, trade_parts 9f438cf9 | any mismatch |
| python3 /tmp/deploy/verify_stamps.py /tmp/deploy/good7 ; python3 /tmp/deploy/size_check.py /tmp/deploy/good7 /home/claude/fol-main | both green | red |
| python3 /tmp/note/note_check.py /tmp/note/note.md | NOTE CHECK GREEN, 17 ok | any WRONG |

## T+0 Sean says go. Deploy commit (Claude, about 4 min)
1. Open U-repo upload page: github.com/szerillo/front-office-ledger/upload/main
2. file_upload call 1: index.html (3.32 MB). Call 2: moves.js (3.08 MB). Call 3: cards.js, book.js, deals.js (3.18 MB).
   Call 4: cards2.d7fb83c8d5.js, offseasons.json, trade_parts.json (2.72 MB).
3. Expect 8 rows in the file list. Message: "Deploy fix pass 1, re-sign rule, 2020 fix". Commit changes. Record the SHA.
Abort: fewer than 8 rows before commit: reload the page and redo the four calls (nothing is committed yet).
If the reply is lost: check the commits page and raw at the SHA before ever uploading again.

## T+4 Verify at the commit SHA (2 min)
for f in the 8 files: curl -s https://raw.githubusercontent.com/szerillo/front-office-ledger/<SHA>/<f> | md5sum: same 8 md5s.
Abort and roll back: any mismatch, or a file missing from the commit.

## T+6 Wait for Pages (poll every 30 s, up to 10 min)
curl -s "$U?t=$(date +%s)" | md5sum until 279c1e66. Not live after 10 min: wait and report; do not re-upload.

## T+10 Verify live (step 7, about 6 min)
| Command | Expect |
|---|---|
| download the 8 live files to /tmp/golive/tree (plus the rest from the live copy); md5sum | the 8 md5s |
| python3 /tmp/deploy/verify_stamps.py /tmp/golive/tree | green, 7 stamps |
| build /tmp/golive/tree = full checkout of main + the cache-busted live files (incl. dudes.json); cd /tmp/golive/tree && for t in t_build t_launch t_wire t_cards t_nullgrades: TARGET=live PAGE=/tmp/golive/tree/index.html node tests/$t.mjs | PASS each. PAGE is required: t_build and t_datashape hash the file in PAGE (default is a local working copy), and t_wire reads ../dudes.json from the checkout |
| PAGE=/tmp/golive/tree/index.html OUT=/tmp/golive/L.json node /tmp/deploy/letters.mjs; cmp with /tmp/deploy/L_g7.json | identical (102 vs old live) |
| python3 /tmp/deploy/offs_stamps.py /home/claude/fol-main/offseasons.json /tmp/golive/tree/offseasons.json | tier labels changed: 18 |
Rollback triggers: any md5 mismatch; stamp check red; any of the 5 suites red; letters census differs from L_g7;
JS errors on load; "did not finish loading" banner on a normal connection; live md5 wrong after 10 minutes.

## T+16 Share step 2b (about 6 min, same go)
node /tmp/share/share_live_r36.mjs /tmp/golive/share $U --only-new /tmp/golive/tree
Expect: "28 winters (of 44)"; the 28 o/ pages identical to the dry run's /tmp/dry/share/o except the og:image ?v= date.
Upload: o/ (28 html), then og/o (28 png), then share.json at the root last (it lists the 4 new pages).
Check: download live o/ into /tmp/golive/tree/o; python3 /tmp/deploy/winter_pages_check.py /tmp/golive/tree:
"44 checked, 0 differ". The club pages (s/) are the daily share task's job, not this step.

## T+24 Correction note page
Upload /tmp/stage/note/corrections/2026-11-12.html to corrections/. Check it returns 200 and its text equals note.md
(note_check already green). New file only; no existing page changes.

## T+28 Tests commit (5 folder uploads)
tests/ (t_build, t_cards, t_nullgrades, t_datashape, t_fun, t_wire, t_ui2, t_grades, t_nov11), tests/fixtures/
(page_code.json, grades.json, data_shape.json), tests/tools/ (verify_stamps.py, size_check.py, winter_pages_check.py),
docs/grade-changes.md (main's file plus the Nov 12 entry; baseline kept), engine/share_live.mjs.
Check: from a full checkout of main, TARGET=live PAGE=<downloaded live index.html> for all five live suites plus t_datashape.

## T+35 Done. Kirk queues the X drafts (x-drafts.md) once corrections/2026-11-12.html returns 200 and o/2019-wsh.html shows -17.4 live.

## Rollback (on Sean's word; about 8 min)
1. One commit from /tmp/stage/rollback, four calls: index.html | moves.js | cards.js, book.js, deals.js |
   cards2.bc21eaa482.js, offseasons.json, trade_parts.json. Delete nothing (cards2.d7fb83c8d5.js stays).
2. Poll live index md5 to 4dc3393b. verify_stamps on the downloaded files green; letters census equals
   /tmp/deploy/L_live.json.
3. Share pages: rerun node /tmp/share/share_live_r36.mjs ... --only-new (rebuilds every winter page whose text
   changed, the 4 new ones included, with live numbers); upload o/, og/o, share.json; winter_pages_check 0 differ.
   Tested on the dry tree: 44 checked, 0 differ.
4. The note page and the tests commit stay unless Sean asks; the note page would then need a one-line update.
