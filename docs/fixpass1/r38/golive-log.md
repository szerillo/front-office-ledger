# Go-live log, Nov 12 (times UTC)
11:34:50 pre-flight: live = main = dry-run copy for index 5f430172, book 1ca8d7c2, deals 67118358, cards d7787e13,
  moves 564030f0, offseasons 1a4a4a5e, trade_parts d14ed16a, share.json 063631b1; cards2 404. main HEAD df6405e.
  Staged = good7: 279c1e66 / 4e6757e8 / a8327e0c / d3e5a831 / d7fb83c8 / 3be8d310 / ec6b882c / 9f438cf9.
  verify_stamps 7 green; size check green; note check 17 ok.
~11:36 deploy commit 8de35fd (8 files, 4 upload calls). At SHA: 8/8 MATCH.
11:37:29 first poll: cards, cards2, book, moves, offseasons new; index.html still old at one edge (MISS, age 0).
11:37:57 all 8 new, busted and plain URLs.
T+10 verify: 8/8 live md5 MATCH; verify_stamps 7 green; TARGET=live t_launch, t_wire, t_cards, t_nullgrades PASS;
  t_build first FAIL (it hashed /work/front-office-ledger-prototype.html, the Nov 11 file, because the runbook command
  left out PAGE); rerun with PAGE = the downloaded live index.html: PASS (codeHashMatches, codeLineCount, zeroPageErrors).
  letters census on live bytes == L_g7 byte for byte (102 vs old live); tier labels changed: 18.
2b: share job vs live: 28 winters (of 44), 28 o/ pages identical to the dry run. Commits f2bd7dd (o/ 28), ee7227b
  (og/o 28), 95a8183 (share.json). 11:45:42 live: images 0/28 mismatched, share.json dacafe7f; winter pages 44
  checked, 0 differ.
Note page 0f661e3: 200 at 11:47:38, md5 0d9d3880; note check green; key lines present.
Tests commit: 2645656 (tests 9), 1cebaee (fixtures 3), fa9adec (tools 3), 88a61b0 (docs), 101004c (engine).
  Main vs staged: 0 of 17 differ. From main's tests: TARGET=live t_cards, t_nullgrades PASS; t_build, t_datashape
  PASS on the live bytes.
11:52:28 final poll: all 6 checked files consistent on busted and plain URLs.
