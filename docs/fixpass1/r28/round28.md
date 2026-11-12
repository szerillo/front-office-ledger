# Round 28 (Nov 11, late): deploy candidate checks

Final engine (deploy-candidate.diff, rules 1-14 + 2020 held rates + re-sign rule + regen swap fix + explicit
headline tie-break) on ledger_v3 (amendment eb310ee), 7 runs in resumable chunks (no command over 10 minutes):
one md5 per published file across X0-X6, 0 guard aborts: cards.js 7e6428d9, moves.js 3be8d310, prototype 83621de8,
offseasons.json a662b840, trade_parts.json 9f438cf9.

Headline pick: offseasons_build.py:36-37 (star: most career WAR, else most value) and :50 (small trades: by value);
ties were broken by max()/sort stability, i.e. by the seat order trade_book wrote. Now explicit: ties go to the
higher MLBAM id (also h2h_deals.py:37-38). Output identical on X0 and X6; with seat lists reversed on purpose the old
code gives 2f9b8b6b, the new code a662b840 (unchanged).

draft_backfill.py: fetch all 7 years first; fail loud (exit 2) on a failed or empty fetch; then delete+insert in one
transaction. Network blocked: old script exit 0 and 1998-2004 picks 10,316 to 0; new script exit 2, table unchanged
(10,316 rows, content 87a21277). Network on: new script exit 0, 10,316 rows.

t_build.mjs (page code hash over non-data lines + zero JS errors + helpers present): PASS on the candidate; on the
build with the old swap (339 lines dropped): FAIL (codeHashMatches, codeLineCount, helpersPresent, reportCardsBuilt,
zeroPageErrors; "$ is not defined").

t_grades: 277 changed keys by stage (live -> unpatched on v3 -> rules 1-14 -> 2020 fix -> re-sign rule):
re-sign rule 163, 2020 fix 107, seat-label swaps 7 (4 + 2 + 1; trades with two seats for one club, same values,
index swapped). Total 277, none without a cause. By trade (order-free): 68 trades change value: 61 re-sign rule,
7 new trades (data). Keys missing 544 / new 558: card and seat labels renamed (headline text, seat order), values
unchanged.

t_winter holmesPiecesCurrent: Tyrone Taylor's Oct 29 free-agency filing (newer than live's data) made the tree
rewrite "Finished 2026 with CHC" to "Back with CHC by 2026". Fixed in the page (a filing after the 2026 season keeps
"Finished 2026"); t_winter 82/82.

Suites on the final candidate: 13 of 15 PASS. t_fun offsExplorer fails on the live page too (pre-existing).
t_grades fails until the fixture is regenerated at deploy with the REASON above. Over HTTP (local server, like
Pages): t_build, t_launch, t_wire PASS, all 39 requests 200.

Rollback: the live files are pinned at eb310ee (index.html 5f430172, book.js 1ca8d7c2, deals.js 67118358, cards.js
d7787e13, moves.js 564030f0, offseasons.json 1a4a4a5e, trade_parts.json d14ed16a, each equal to live).
