# Round 57 (Nov 14, Auditor verdict on r56)

1. Next five years: the report card's "next five years" box (and the club page and home club card) was drawn before
   the day's transactions arrived and never redrawn; hzLeague was recomputed after them. liveWinter now redraws every
   view that shows these ranks once the feed is applied (and sets HZ_FEED_DONE). Ranks keep the round 56 tie-break.
   hzpage_check: 5 clubs x 6 fresh loads, every other load with the feed held 4 s; fails on any difference between
   loads or between the drawn ranks and the league table. On the r56 page it reproduces the Auditor's flip
   (BOS 2031 #9 drawn vs #10 table; SF #10 vs #9); on r57 30/30 loads agree.
2. Trade labels: key = date|clubs|every player received (unique across 4,162 trades). 632 trades labelled (the r56
   count of 631 merged the two SD/SEA 2020-08-31 trades into one key and labelled 4 others: Francisco 2009,
   Spruill/Smith 2014, Marsh/O'Hoppe 2022, Wright/Kowar 2023). r56_page_check now asserts labelled set == list and
   that those 4 are not labelled; on r56 it fails on exactly those 4. Share pages labelled: still 40 of 116.
3. HOU/ATH club previews: stray dot removed (og/t hou.png, ath.png, clubs-manifest.json).
4. Simulator 2020: r56 paced the 2020 comparable winters. Verified by replaying the simulator's own comp rule (gmReport
   distance formula, empty winter) for all 30 clubs: raw 2020 totals were never picked (0 of 150 picks), paced they
   took 25 picks and moved 14 clubs' "history's base rate" by up to 11.8 wins. r57 leaves winters across 2020 out
   (450 of 480 remain), which reproduces the r55 base rates exactly for all 30 clubs (sim2020_check against
   sim_base_rates_r55.json, taken from the r55 page 0aa79ede). The explorer keeps the 162-game pace display.
No grade or value changed: Desk c25bca11a598, grades 28cf6541870f. Rollback: rollback_r57.py (to r56, tested).
