# Round 36 (Nov 12, ~03:30 ET): wrong-seat check, data-block shape check, offsExplorer explained, share pages. Nothing deployed

## 1. Grades that exist but could be credited to the wrong seat (handover path)
Source: each seat's own dates in regimes.json / regimes_hist.json, and the trades in the trade book (book.js). Census
over all 152 seats, live and good7 (seat3.mjs, gap.mjs):
- Trade count on the card equals the trades dated inside the seat for 151 of 152 seats on both builds.
- 0 trades credited to two seats. 17 trades credited to no seat (between one front office's exit and the next one's
  start), |net| 22.2 wins, identical on live and good7.
- Card trade net (the engine's own score, copied as is) vs the sum of that seat's rows in the trade list: differs by
  more than 0.5 in 17 seats on live and 18 on good7, at most 4.2 (Melvin MIL: card +18.1, list +13.9) on both. The
  two numbers come from two scripts that group and round trades differently (hist_score per filing, unrounded;
  trade_book merges filings within 3 days and rounds each player to 0.1).
Three hand traces (card n / book n / card net / book net), live then good7:
- TOR Alex Anthopoulos, 2009-10-04 to 2015-10-29: 81/81/-12.5/-11.6 on both. The 2009-07-31 deal (-1.9) is on
  Ricciardi's card. The 2015-11-20 deal (-5.0) sits between his exit and Atkins's start (2015-12-03): on no card.
- MIA Kim Ng, 2020-11-13 to 2023-10-16: 40/39/6.6/5.7 live, 40/39/6.5/5.7 good7. The ledger has 40 trade filing dates in
  her window; the book files the 2020-12-10 Zach Pop Rule 5 pick-and-trade and four one-way filings differently.
- PIT Cam Bonifay, to 2001-06-11: 16/16/20.0/20.2 on both. Marte for Wilson (2001-06-13, +7.1, the largest uncredited
  deal) falls between his exit and Littlefield's start (2001-07-13). LAD's 2001 interim months (3 deals, about -2.4
  each) are uncredited too, while LAD's 1998 interim (Lasorda) has its own card.
Verdict: no seat in good7 gets a trade from the wrong seat; nothing here changed from live. The uncredited gap trades and
the two nets for one seat are pre-existing and on the after-launch list.

## 2. Shape check on the 24 named data blocks (tests/t_datashape.mjs)
A block under 200 characters (the empty defaults: TRADE_BOOK, QUIZ_CTX, PLAYER_FATE, CURATED_EXTRA, PLAYER_ORIGIN)
must match its pinned text exactly; a larger block must keep its shape (type, key set of fixed-key objects, element
shape of arrays, value shape of id-keyed maps, 3 levels).
Green (data changes): live, the 4 stage builds RV3/W3/E3/X0, the X0 site, both clean rebuilds, good5, and a seed with
values changed inside EXT_MAP and AUTO_REGIMES. Red: TRADE_BOOK default names {} to {"1": "x"}; QUIZ_CTX {} to {a: 1};
a new field on the first AUTO_REGIMES entry.

## 3. t_fun offsExplorer
My earlier "fails on live too" was wrong. On the live build with its own offseasons.json, offsExplorer passes (15
cards, #1 2011-12 Oakland Athletics, +34.3, 5 links). On good7 the explorer renders correctly; the test hard-codes
Oakland as #1, and the 2020 salary fix moves WSH 2014-15 to +33.9, above Oakland's +33.4. Broken test, not a page bug,
but it marks a public change: the best winter on the site changes. The check now takes #1 from the data: t_fun 112/112
on good7 and on live.

## 4. Launch list
launch-list.md: 13 steps, one line each, owner and status.

## 5. Assumption tested: share pages carry the new numbers after the deploy
They don't, as the job stands. engine/share_live.mjs with --only-new skips any winter page that exists. Run locally
against good7: 20 existing winter pages differ (14 with a different number in the title, e.g. OAK 2011-12 +34.3 to
+33.4) and 4 new winters enter the top/bottom 20. Against the live files the same run rebuilds 0 winter pages, so
the change comes from the deploy. Club pages (4) changed on both runs: today's feed, not the deploy. Patched rule:
a winter page is rebuilt when its description changes, as club pages already are. New checklist step 2b. 4 pages
that leave the top/bottom 20 still keep old numbers: open item.
