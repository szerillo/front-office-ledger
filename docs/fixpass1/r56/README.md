# Round 56 (Nov 14 re-audit fixes)

1. Ranks: no rank numbers in card or club share text or previews (the site publishes none). The club trading card
   shows no front-office rank and no 2031 rank.
2. Leverage copy: Heists intro and every card trade table now say every win counts the same.
3. Next five years: hzLeague is reset when the day's transactions are applied (it could be computed before and kept),
   and ranks use values rounded to 0.01 with the club code as tie-break. hz_check renders twice (one computing early).
4. New seats (HOU, ATH): club share text and preview say "too new to grade", not a wins figure.
5. 2020: the 60-game total is shown with its 162-game pace, changes use the pace (explorer, winter previews
   2019-laa/phi/wsh, 2020-nym, simulator comparable winters).
6. Methodology section id=method-review explains the label; labels link to it; it links /corrections/.
7. Trades: FZ0 (frozen, debut+6 rule) reproduces the live trade book byte for byte (md5 b86f4bfc); F1 (published
   control end) changes 631 trade keys (date|clubs) by 0.1+ on some seat. Those carry the label on the Heists list
   (636 rows) and on 40 of the 116 h/ pages. trade_review_expected.json has current and expected values.
preview_check now also checks: no ranks, club wins/too-new wording, club image vs og/t/clubs-manifest.json, h/ labels.
No grade or value changed: Desk c25bca11a598, grades 28cf6541870f before and after.
