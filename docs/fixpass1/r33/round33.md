# Round 33 (Nov 12, ~01:30 ET): split hardened, Desk text traced, checklist. Nothing deployed

## 1. Caching of the second part
Round 32's cards.js loaded `cards2.js?v=<md5>`: a stamp, but a cached cards.js could still get the wrong part from
the server across a rollback (Pages ignores the query). Now the part is named by its content hash:
`c.src = 'cards2.d7fb83c8d5.js' + (tries ? '?r=' + tries : '')`.
Returning-visitor test (Pages-style max-age=600, no request interception), truth = fresh browser fingerprint:
- unstamped cards2.js: return visit fingerprint 809e6454, truth 6a860196: RED (new part 1 + cached old part 2,
  152 clubs, no error shown, silent).
- hash-named part: return visit 6a860196 = truth: GREEN.
Rollback race (visitor holds the candidate cards.js, never got part 2, server rolled back):
- query-stamped part: 809e6454, mixed data, silent: RED.
- hash-named, rollback keeps the candidate part: 6a860196 = truth: GREEN.
- hash-named, rollback deletes it: 404, retry 404, banner shown, no data merged: visible, never mixed.

## 2. Part 2 missing
Merge needs both parts and all 152 clubs (CARD_CLUBS written by the build). A page never shows 63 clubs: with part 2
blocked, 0 regimes get card details and CARDS_READY stays false. Round 32 build: banner after 21.4 s. Now: one
retry after 1.5 s, then the same "did not finish loading" banner with Retry at 3.2 s (screenshot
part2_blocked_screen.png). New suite tests/t_cards.mjs (both parts ran, 152 clubs = CARD_CLUBS, every card
merged, no banner): PASS on good5; seeded RED with one club dropped from part 2 and with part 2 deleted.

## 3. Deal Desk text that changes (26 trades; letters and numbers 0)
Traced by grading the 50 deals on every stage build (live, RV3 data, W3 fix pass, E3 2020 fix, X0 re-sign, G5):
- Comp boxes (11 trades): data 5, fix pass ordering (rule 7 trade_comps) 6. Different example trades listed;
  no letter or number moves. A reader's conclusion does not change.
- GM lines (25 trades), all data except one:
  - deal counts +1 to +3 (new trades since Nov 1: BOS 60 to 63, DET 57 to 58, TB 230 to 231, STL 13 to 14, WSH 20 to 22, SF 24 to 26)
  - SF Buster Posey trade grade A- to A (in the 102: rc|sf|trade.g)
  - ATH Taylor Smith "new in the seat, no trades graded yet" to "trade grade F over 1 deal": NOT in the 102
    (no live grade to compare, so letters.mjs has no key for it)
  - style tags change for 6 GMs (Dombrowski, Getz, Harris, Anthopoulos, Stearns, Picollo; e.g. "plays the slot book
    straight" to "shops for arms"); they change at the data stage (ledger rebuilt from the MLB API plus the feed
    after Nov 1): NOT in the 102 or 18
  - TOR vs LAD head to head +2.8 to +2.7 (re-sign rule): NOT in the 102
Outside the note: a new F for Taylor Smith, GM style tags, comp lists, deal counts, one head-to-head number.
The F on a new GM after one deal is the one a reader would notice. Suggested clause for either note:
"New trades since Nov 1 are now graded, so a few GM summaries and style tags also update."

## 4. Names
Keep the live Baseball-Reference style, pinned. Not a blocker, no decision needed.

## 5. Rollback order
Deploy is one commit (four upload calls, one "Commit changes"); Pages publishes a commit whole. Every cards.js ever
served names its own part by hash, so a request can only miss a file if that file is deleted. Rule: the rollback
commit adds cards2.bc21eaa482.js and deletes nothing; old parts are cleaned up later (10+ min) or never. Tested above.
Rollback build rb5: letters census = live exactly, Desk 50/50 identical to live, size check green.

## 6. Deploy-day assumption tested: the split does not slow a phone into the error banner
Cold load, gzip like Pages, 4x CPU, no cache:
- Slow 4G: live 18.2 s, unsplit 18.2 s, split 18.1 s to cards ready; no banner.
- Slow 3G: live 66.8 s, unsplit 66.6 s, split 66.7 s; banner at ~47 s on all three, cleared at ready (pre-existing).

## Same numbers on the hardened build (good5)
Suites 15/16 PASS incl. t_cards; t_fun offsExplorer (pre-existing). letters L_g5 == L_g3 (102). Tier labels 18.
Wire 0/121. t_grades 0 changed vs good3 fixture (277). Desk 50/50 HTML identical to good4. X0 to X6 rebuilt: 7
identical sites; Z_X6 rebuilds good5 byte for byte. Size check green.
