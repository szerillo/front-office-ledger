# Fix pass 1, iteration 1: traced patches added under rule 4 (written before the patched runs)
- debut26.py:25 and :28. Trace: Step 0 repeat R0c (same inputs, PYTHONHASHSEED=12345) stopped at debut26.py; the
  fetch URL listed player ids in set order, so batches follow the hash seed. Rule: sort the ids.
- trade_book.py:115-116 (`for p in ins`, `outs.items()`) and :122 (`out.sort` on date only). Trace: Step 0 R0 vs R1
  trade_book.json differs only in player order inside seats and in same-day trade order. Rule: sort players by id,
  seats by club, same-day trades by their content. (Same file as pre-registered rule 3.)

## Iteration 2 traces (written before the iteration 2 runs, after iteration 1 F0 to F6)

Iteration 1 result: offseasons.json, trade_parts.json, trade_book.json one md5 each; cards.js, moves.js, prototype, sweep_results, hist_results, desk_data still differ in VALUES.
sweep_results F0 vs F1 multiset diff: 9 paths.
- led.waiver.best/worst (ARI, ATL, CHC, LAD, PIT, SEA, TOR): top-4/top-5 lists cut at a tie on net. sweep_score.py:432-433, hist_score.py:350-351, fa_grade.py:206-207 sort by net only, so Python's stable sort keeps input (SELECT) order among equal nets. Also decs.sort(-abs net) and walk.sort(net) in both files, and fa_tops = decs[:4] in fa_grade.py:204-205.
  Rule 5: every best/worst/tops sort breaks a net tie by date ascending, then headline text, then the pid list. Same sets, only which tied decision makes the cut changes.
- chan.intl.n SEA 201/202, TOR 360/359: one record, Felipe Bello (806593), filed as signed to a minor league deal by both Toronto (141) and Seattle (136) on 2022-08-02, no tx_id, no other row for him. ifa_score.py:92 keys _seen_ifa by (pid, date), so the first row in SELECT order takes him. It is the only same-day two-club minor-league signing in the ledger. LVM rows for him: none (value 0.0).
  Rule 6: a minor-league signing filed by two clubs on the same day, with no other record to say which club holds him, is contradictory data: it counts for neither club and is listed as a data issue. Effect: n only (his value is 0.0), SEA and TOR each one lower than whichever got him before.
New silent drop noticed (not fixed in this pass): ifa_score.py:69-70 `except Exception: d = {"people": []}` on the bio fetch. In these runs it made one batch call, served from the frozen record (http-replay), so the except did not fire.
- hist_results F0 vs F1: 43 paths. Besides the rule 5 ties: (a) trade decisions' "comps" lists differ; (b) one walk row name differs (CLE Shapiro, 2003-12-21, pid 424725: "Carl Sadler Jr." vs "Carl Sadler").
  (a) trade_comps.py:96-97 reads each club's trades with no ORDER BY; the deal list order, the tie in `best = max(acq, ...)` and `gave = max(outs...)` (first max wins), the name from `next(...)`, and `cands.sort(key=score)` at :141 all follow SELECT order. deal_archive.json (F0 9d01b8aa, F1 11545c06, F6 0d2893b7) feeds desk_data.json deals (12 rows differ F0 vs F1, the "who"/"gave" names in tied deals).
  Rule 7: trade_comps reads trades ORDER BY date, description, tx_id, person_id, from_team, to_team; acq and outs are taken in person_id order, so a value tie for "who"/"gave" goes to the lower id; comp candidates sort by (score, date, club id, who).
  (b) sweep_score.py:152-155 and hist_score.py:108-111 read regime rows with no ORDER BY, and mirror_losses (sweep :139, hist :94) likewise. The feed and the Retrosheet archive both file Sadler's 2003-12-21 departure under two spellings; seen_walk keeps whichever comes first.
  Rule 8: the regime and mirror reads in sweep_score.py and hist_score.py are ORDER BY date, then feed rows before archive rows (description not ending "(Retrosheet archive)"), then tx_id, description, person_id, from_team, to_team. Justification from the data: archive rows exist to fill gaps in the feed (the v5.9 comment at the dedupe), so when both file the same event the feed's row is the one kept. Effect: the Sadler row shows the feed's spelling.
  Rule 8 also covers tradegroup.py:62 (_LEGS, per-player leg lists appended in SELECT order) and :187 (_COMPL completions), the two reads behind dedupe_rows: both get ORDER BY date, person_id, from_team, to_team (and description at :187).

## Iteration 3 traces (written before the iteration 3 runs; from iteration 2 F0 vs F1, the first two runs done)
Iteration 2, F0 vs F1: trade_book, hist_results, desk_data, offseasons, trade_parts one md5. sweep_results differs in ORDER only (multiset diff 0 paths): allx_intl for 4 clubs.
- ifa_score.py:166 sorts each club's signings by date only; two signings on one date (PIT 2021-01-15, Antwone Kelly 699008 and Esmerlyn Valdez 699013) keep SELECT order.
  Rule 9: allx_intl sorts by (date, person id). Order only; no value changes.
  Rule 9 also covers ifa_score.py:165 (intl tops cut at 5 by value only): ties go to the earlier date, then lower id. Same in F0/F1 so far; patched before it can bite.
Iteration 2 stopped by me after F0 and F1 finished (F2, F3 partial, F4 to F6 not started) once rule 9 was found; its results are superseded and not used for the bar.

## Round 4 traces (written before the round 4 runs; from round 3 G0 vs G1)
Round 3 (iteration 3), G0 vs G1: cards.js, offseasons.json, trade_parts.json and every mid file one md5. moves.js and the prototype page still differ, VALUES: 85 players' move lists.
- ingest/regen_v3.py:538 reads each player's moves ORDER BY date only. The feed often files one event twice the same day with two texts (Kinley 641755, 2019-12-09: "claimed RHP Tyler Kinley, and off waivers" vs "claimed P Tyler Kinley off waivers"). The dedupe at :555-559 swaps in the other text only if its garble score is strictly better, so on an equal score the row read first wins, and its from/to clubs stay.
  Rule 10: that read is ORDER BY date, type_desc, team_id, description, from_team, to_team, person_id. The garble-score choice is unchanged; this only settles exact ties. Order also fixes PLAYER_MOVES key order.
Round 3 stopped by me after G0 and G1 finished (G2, G3 partial; G4 to G6 not started). Under 5e81190 it is already a FAIL (two md5s for moves.js and the prototype).

## Round 5 traces (written before the round 5 runs; from round 4 H0 vs H1)
Round 4, H0 vs H1: every published and mid file one md5 except front-office-ledger-prototype.html: one line, SCEN (scenario_build.py), Cabrera 2007 trade: the recv list order (Cabrera, Willis vs Willis, Cabrera).
- scenario_build.py:165-167 reads a deal's pieces with SELECT DISTINCT and no ORDER BY; recv and sent keep that order, and seller_tid is the first seller seen. :296 sorts comps by score only.
  Rule 11: that read is ORDER BY person_id, person_name, from_team, to_team; the comps sort breaks score ties on the comp row's text. Order only for recv/sent.
Round 4 stopped by me after H0 and H1 finished (H2, H3 partial). Under 5e81190 it is a FAIL (two md5s for the prototype page).

## Rule 6 amended (after the second-source check, before any v2 run)
Felipe Bello (806593): MLB.com's transaction log for him shows both 2022-08-02 filings, then "assigned to DSL Blue Jays" on 2022-08-03, and every minor-league line after (DSL, FCL and Dunedin Blue Jays, 2022-24) is a Toronto affiliate. He signed with Toronto; the Seattle row is a feed error.
Rule 6 (amended): a same-day minor-league signing filed by two clubs is resolved by a sourced override (SAME_DAY_CLUB in ifa_score.py, one entry: Bello to Toronto, source above); without an override it still counts for neither club. Effect: TOR intl n counts him, SEA does not; value 0.0.

## Round 6 engine (after amendments 2 and 3)
Rule 12 (as replaced in amendment 3) in trade_book.py: seats ordered by value then higher id; display name from the archive row when one exists. Round 5 (rules 1 to 11 on ledger_v2) stopped by me before any run finished; not judged.
Guard change before round 6: the /people batch rebuild covers every query suffix (hist_score asked a 37-id batch the record pass had fetched as 38 ids); it still aborts on any id never asked in the record.

## Round 7 traces (written before the round 7 runs; from round 6 W0 vs W1 on ledger_v2)
Round 6, W0 vs W1: offseasons.json, trade_parts.json, trade_book, desk_data one md5; sweep_results and hist_results differ in VALUES: PHI waiver channel (Mike Vasil 678024, 2024-12-11, "lost in Rule 5", in W0 only) and MIN Falvey (Daniel Susac 691740, 2025-12-10, in W1 only).
- r5_conduit.py:15-27 (chain step 0, rewrites the ledger in place). On a production-shaped ledger one Rule 5 selection is filed under both the selecting and the losing club. The loop takes rows in SELECT order: if the losing club's copy comes first, it is the row re-filed to the final club (team_id overwritten), and the selecting club's copy is left; if the selecting club's copy comes first, the losing club's copy only gets its to_team changed. Which club keeps the loss row depends on read order. The trade lookup takes tr[0] with no ORDER BY.
  Rule 13: one pass per selection (person, date), ORDER BY date, person_id; the row re-filed is the copy filed under the selecting club; every other copy keeps its team_id and gets to_team = the final club; the conduit trade is the earliest within three days (ORDER BY date, rowid-free: date, to_team). The frozen ledger (one row per receiving club) never exposed this.
Round 6 stopped by me after W0 and W1 finished (W2, W3 partial). Under 5e81190 it is a FAIL (two md5s for cards.js, moves.js, the prototype, sweep_results, hist_results).
