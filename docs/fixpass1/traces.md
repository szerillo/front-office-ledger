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
