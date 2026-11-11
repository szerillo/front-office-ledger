# The 44 unordered SELECTs, ranked by what row order can reach (Nov 11, round 23)

Classified by reading the code after each SELECT, not by running it. Buckets:
(a) order reaches a sort with ties, or an output list in input order;
(b) order decides a top-N, "first" or "last" pick (dedupe keeps the first row, `[0]`, `break`, a dict that keeps
the last write, `max()` over ties);
(c) only aggregates or order-free lookups (sum, count, min, max over values, sets, sorted afterwards).
Only (a) and (b) can change a published file. Whether a script feeds a published file at all is tested in Step 0.

**Counts: (a) 4, (b) 12, (c) 28.**

## (a) Sort with ties or ordered output (4)

| file:line | Why |
|---|---|
| engine/sweep_score.py:153 | regime rows feed `dedupe_rows` and `group_trades`; decision lists come out in input order and the top lists sort by net, ties keep input order |
| engine/hist_score.py:109 | same as sweep_score.py:153, archive regimes |
| engine/trade_book.py:73 | `seat_groups` order sets the union-find order and the order of trades in `trade_book.json`; also (b): `names[pid]` keeps the last name seen. **Confirmed by Step 0:** player order in seats and 2 display names vary |
| engine/scenario_build.py:166 | `recv` and `sent` lists keep row order (shown in the simulator); `seller_tid` is the first match |

## (b) First, last or top-N pick (12)

| file:line | Why |
|---|---|
| engine/sweep_score.py:139 | dedupe on (date, person, type) keeps the first row; the kept row's other fields can differ |
| engine/hist_score.py:94 | same, archive |
| engine/sweep_score.py:164 | draft-pick dedupe keeps the first row |
| engine/hist_score.py:120 | same, archive |
| engine/champions_build.py:169 | has `ORDER BY date desc` (the scan flagged it from the first string part), but same-day rows are unordered and the loop breaks on the first match |
| engine/champions_build.py:212 | `alts` descriptions in row order feed the shown "how acquired" text |
| engine/prospect_bio.py:35 | `draft[pid] = r` keeps the last row per player |
| engine/r5_conduit.py:17 | `final = tr[0][2]`: the first trade row wins, and the result is written back into `sweep_tx` |
| engine/ret2.py:77 | first row per (player, year) keeps its team. **Confirmed by Step 0:** 82 filings sit under two teams; the league expectation curve shifts and 13 of 30 current regime totals vary by up to 0.2 |
| engine/ext_grade.py:50 | candidate order decides `max(cands, key=fit)` when two candidates fit equally |
| engine/drs_ingest.py:70 | `cands[0]` is used when a name maps to several players |
| engine/tradegroup.py:62 | dedupe keeps the first row; `_LEGS` lists keep row order |

## (c) Aggregates or order-free (28)

archetype.py:124, :167, :193, :202, :222; asset_rules.py:313 (min); champions_build.py:68 (max of a filter);
contract_book.py:144 (min); controlled_market.py:28 (sorted after), :63; desk_data.py:719 (set);
hist_score.py:129 (set); ifa_score.py:48, :52; proj_v1.py:153, :187 (min), :226 (sets, sums);
r5_conduit.py:15 (driver loop, per-row update), :41 (group by, unique-match test); rental_baseline.py:39 (any),
:72; ret2.py:164; savant_fingerprint.py:83; sweep_score.py:173 (set); trade_comps.py:49 (sorted after), :97,
:126 (max); tradegroup.py:187 (`sorted(set(...))` after).

Note: `group_trades` itself sorts groups by date and compares every same-day pair, so the merge is order-free on
dates; the PTBNL join and the group's representative row are where order can still enter.

Step 0 (`tests/tools/step0_results.json`) confirmed two of these as causes; the rest of the published differences are not yet traced.
