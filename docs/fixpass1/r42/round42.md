# Round 42 (Nov 12, 08:24 to ~09:00 ET)

## Call 2: content-hash data names. DEPLOYED, gates green
Data first (3 commits, files added beside the old ones, nothing replaced): 390e360 moves, 2dd26a3 cards/book/deals/
offseasons, 13b7efd trade_parts/dudes. Gate against the live site (gate_live_hashnames.txt): 8 files, 0 bad, CLEAR.
Then index.html 0e21fa8 (e8a6c72d), tests 9f30261 (t_hashnames.mjs; t_build masks hashed names), pin 34f2e10.
Before: live = main for all 9 served files; staged tree served locally: t_build, t_launch, t_wire, t_cards,
t_nullgrades, t_hashnames all exit 0. After: live = staged 15/15 at 13:43 UTC; fresh clone + cache-busted live:
TARGET=live PAGE=/tmp/r42/hpost/index.html t_build exit=0 PASS
TARGET=live PAGE=/tmp/r42/hpost/index.html t_launch exit=0 PASS
TARGET=live PAGE=/tmp/r42/hpost/index.html t_wire exit=0 PASS
TARGET=live PAGE=/tmp/r42/hpost/index.html t_cards exit=0 PASS
TARGET=live PAGE=/tmp/r42/hpost/index.html t_nullgrades exit=0 PASS
TARGET=live PAGE=/tmp/r42/hpost/index.html t_hashnames exit=0 PASS
Live page probe: loads offseasons.ec6b882c53.json, book.4e6757e8f6.js, cards.d3e5a83173.js, moves.3be8d3107f.js,
cards2.d7fb83c8d5.js, all 200, 0 errors. The plain-named files stay for tools and old pages; never delete them.
Rule from here: every data deploy = data commits, gate_index.py CLEAR, then index.html, then tests.

## Call 1: pre-registered rank threshold. RUN as written; ranks replaced by bands. DEPLOYED, gates green
Before the run (Check C) I found my r41 spot-check compared single cache rows: the cache keeps a pitcher's batting and
pitching as separate rows. Fixed in the unit, declared in run_notes.md and committed with the script (79632bb) before
the run. Result (sim_results.txt): no adjacent pair of winters keeps its order in 90% of 2,000 draws (best 0.715 as
written; 0.876 in the independent-seasons sensitivity). Median gap needed for a 10% flip rate: 11.2 wins.
So every rank on a winter page goes: 40 pages say "Among the 20 best/worst offseasons since 1998" (under the stop line
of 50); the 4 pages outside the 20s keep no rank. Numbers unchanged; image links get a new ?v= date.
Commits: 9814782 og/o (40), b0716fe o (40), 8c7bc25 corrections, 816b53f generator. Staged 82 files.
Before: staged tree served locally, 6 suites exit 0. After: live = staged 82/82 at 13:51 UTC; fresh clone + live files:
TARGET=live PAGE=/tmp/r42/bpost/index.html t_build exit=0 PASS
TARGET=live PAGE=/tmp/r42/bpost/index.html t_launch exit=0 PASS
TARGET=live PAGE=/tmp/r42/bpost/index.html t_wire exit=0 PASS
TARGET=live PAGE=/tmp/r42/bpost/index.html t_cards exit=0 PASS
TARGET=live PAGE=/tmp/r42/bpost/index.html t_nullgrades exit=0 PASS
TARGET=live PAGE=/tmp/r42/bpost/index.html t_hashnames exit=0 PASS
Not changed: the offseason explorer chip and the front office leaderboard on index.html still show exact ranks.

## Check A: ties, live
Every live winter label recomputed independently from live offseasons.json before the band deploy: 0 mismatches of 42;
the only tie group with pages (1998-sd, 2006-sd, 2012-mia at +19.5) read T-18 on all three. Moot now (bands).

## Check B: Phil Hughes 2015, traced
The -0.08 was my error, not the Ledger's: the cache has two 2015 Twins rows for him, batting (3 PA, -0.08) and
pitching (+0.68). His Ledger WAR is 0.61. Pitching line, engine/lvm15.py with live feed values:
155.1 IP, 29 HR, 16 BB, 2 HBP, 94 K. Raw FIP (13x29 + 3x18 - 2x94) / 155.1 = 1.567; + cFIP 3.453 = 5.020;
park (Twins 2015 PF 1.0258) 5.020 / 1.0258 = 4.893; league RA9 4.282, runs per win 9.375;
(4.282 - 4.893) / 9.375 x 155.1/9 = -1.124; replacement 0.105 x 155.1/9 = +1.810; total +0.686 (cache 0.684).
B-R gives 1.77 because bWAR runs off runs allowed with defense support, not FIP. Design difference (ledger_war.py
says pitchers are FIP-flavored), not a bug. Small real bug found on the way: innings are read as 155.1, not 155 1/3
(the feed writes outs after the dot); worth under 0.01 win a season; fix with the next engine change.
Count, corrected unit: 1,021 of 21,911 pitcher seasons (4.7%) differ from bWAR by more than 1.5 (590 Ledger lower),
spread over all eras. Public reach: 298 trade pieces, 250 settled winters, 31 of the 40 top/bottom-20 winters include
at least one. So yes, public grades and winter totals depend on them; that is the FIP-vs-runs choice, now covered by
bands on the winter pages.
r41 spot-check, corrected unit: still 18/20; Hughes now 0.61 vs 1.77 (fails on size), Kennedy unchanged.

## Check C: model choice vs noise, and the independence assumption
Assumption named: the per-season differences between Ledger WAR and bWAR are independent across players and seasons.
The 20 r41 rows cannot test it (one team-season pair: MIN 2015). Tested on the full join, 41,960 player-team-seasons:
- residual mean +0.05, SD 0.60 (not 0.64; full-time pitchers SD 1.11)
- role x playing time groups explain 2.6% of the variance (systematic offsets are small)
- a player's consecutive seasons correlate 0.18 (a stable player-level part, e.g. a pitcher whose runs beat his FIP)
- two players in the same club-season correlate 0.02 (no team-level clustering)
So independence holds across players and teams, not within a player. The disagreement is two models measuring the same
season; it bounds model choice plus data error, and cannot separate them. Rough spread for WSH vs ATH with SD 0.60
and ~76 seasons: about 5.2 wins if independent; the pre-registered run (full within-player correlation) needs 11.2.

## Check D: launch status
See the table in the reply; the short answer: launched; known wrong or unproven items remain (ranks on index.html,
the pre-season release rule, trade-season proration, arb salaries, 17 trades on no card, 1998-2014 extension file).
