# Deploy checklist: Front Office Ledger fix pass 1 + re-sign rule + 2020 fix (one pass)

[Sean decides] Note A or B (and whether to add the GM-line clause, round33.md section 3) · Winter tier line in or out · cards route: Option A split build (ready) or drag the unsplit files in by hand · Go: approve the deploy commit in the session (the permission check treats it as a production deploy)

Build: /tmp/deploy/good7 (rebuilds byte-identical from the pinned runs Z_X0 and Z_X6 with build_site.py; good6 plus the null-grade fix, round 35).
Rollback: /tmp/deploy/rb5 (the live eb310ee site, cards split the same way).

## 0. Before (5 min, nothing public)
1. main HEAD is still 5f4dc44 or a later notes-only commit; live index.html md5 = 5f430172 (nothing deployed since).
2. Candidate md5s: index.html 279c1e66, book.js 4e6757e8, deals.js a8327e0c, cards.js d3e5a831,
   cards2.d7fb83c8d5.js d7fb83c8, moves.js 3be8d310, offseasons.json ec6b882c, trade_parts.json 9f438cf9.
3. `python3 size_check.py good7 <live clone>` green; `python3 size_check.py rb5 good7` green;
   `python3 verify_stamps.py good7` and `python3 verify_stamps.py rb5` green (every ?v= stamp and the cards2 name
   recomputed from the bytes on disk; a one-byte change to either cards2 file goes red).
4. Suites on good7: 18/18 PASS (incl. t_cards, t_nullgrades, t_datashape), t_fun 112/112. Census: letters 102, tier labels 18,
   Wire 0/121, Desk 0 letter/number changes on 50 deals.
5. Note text final (A or B per Sean), staged, not posted.

## 1. Deploy commit (one commit, root upload page)
https://github.com/szerillo/front-office-ledger/upload/main . Four file_upload calls into the same page (limit 3.8 MB a call):
- call 1: index.html (3.32 MB)
- call 2: moves.js (3.08 MB)
- call 3: cards.js (2.01), book.js (0.76), deals.js (0.41)
- call 4: cards2.d7fb83c8d5.js (1.96), offseasons.json (0.33), trade_parts.json (0.43)
Wait until the page lists 8 files, then one "Commit changes". Message: "Deploy fix pass 1, re-sign rule, 2020 fix".
Delete nothing in this commit. Record the commit hash.

## 2. Verify (within 10 min)
1. Commit page shows the 8 files; raw at the commit SHA: md5s match step 0.2.
2. Live, poll with ?t= until index.html md5 = 279c1e66 (Pages lag 1 to 3 min); then `verify_stamps.py` on the
   downloaded live files.
3. `TARGET=live node tests/t_build.mjs`, `t_launch.mjs`, `t_wire.mjs`, `t_cards.mjs` (152 clubs, both parts, no banner), `t_nullgrades.mjs`.
4. letters.mjs against live = 102 vs the old live census; offs_stamps 18; Wire 0/121.
5. Returning-visitor test (cache_return_visit.mjs logic): a browser that loaded the old site gets the new card data.

## 2b. Winter share pages (after step 2 passes, separate commit, same go)
The share job skips any winter page that already exists (`--only-new`), so 20 of the 40 o/ pages would keep the old
text, 14 of them with an old number (OAK 2011-12 +34.3 instead of +33.4, WSH 2014-15 +32.8 instead of +33.9).
Run the patched engine/share_live.mjs (winter pages rebuilt when their description changes, like club pages) against
live: `node engine/share_live.mjs <out> https://frontofficeledger.com/ --only-new <repo>`. Expected: 24 winter pages
(20 rebuilt, 4 new: 2001-wsh, 2012-mia, 2014-cws, 2016-mia), og/o images, share.json. Upload o/, og/o, then
share.json last. Check: every o/ title number equals the live offseasons.json total.
4 pages drop out of the top/bottom 20 and keep old numbers (2019-laa -20.6 vs -16.8, 2019-wsh -22.7 vs -17.4,
2020-nym -19.6 vs -19.1, 2021-tex +19.6 vs +18.2): open item on the launch list.

## 3. Tests commit (after step 2 passes, separate commit)
tests/fixtures/page_code.json, tests/fixtures/grades.json, tests/t_cards.mjs, tests/t_nullgrades.mjs, tests/t_datashape.mjs + fixtures/data_shape.json,
tests/t_build.mjs (named data blocks rule), tests/t_fun.mjs (offsExplorer from data), tests/t_wire.mjs, tests/t_ui2.mjs, engine/share_live.mjs,
docs/grade-changes.md entry.
Then the note goes up per Sean's pick. X posts are Kirk's.

## Rollback (any red in step 2, or on Sean's word)
One commit, same four-call pattern, files from /tmp/deploy/rb5:
index.html 3.29, moves.js 3.06 | cards.js 2.00, book.js 0.76, deals.js 0.40 | cards2.bc21eaa482.js 1.96,
offseasons.json 0.33, trade_parts.json 0.43.
Never delete any cards2.*.js file, in the rollback or later: a browser holding the candidate cards.js still asks for it.
Tested: kept, it gets its own matching part; deleted, it gets a visible "did not finish loading" banner, never mixed data.
Old cards2.*.js files are never deleted. Each is about 2 MB in the repo; no cleanup step, no owner needed.
Verify: live index.html md5 = 4dc3393b (rb5), cards.js 6478c403, cards2.bc21eaa482.js bc21eaa4; letters census equals
the old live census (0 differences; tested locally on rb5), Desk 50/50 identical to live.

## Rollback triggers
Any suite red on live that is green on good7; letters count not 102; t_cards red; JS errors on load; banner on a
normal connection; md5 mismatch after 5 minutes.

## Known, not blockers
- Old cached page plus new data for up to 10 minutes after the deploy (same for every data file, every deploy).
- Slow 3G: the "did not finish loading" banner shows at about 47 s and clears when the cards land at about 67 s,
  on live today too; the split does not change it.
- Names stay in the live (Baseball-Reference) style, pinned.
- A part that never answers (no error) gets no retry; the page's 20 s banner covers it, as today for cards.js.
