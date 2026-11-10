# NHL trade channel, first cut (v0)

Built Nov 10 2026 (night). Nothing here is on the site. Scripts: `engine/nhl/trades_wiki.py` (pull and
parse), `engine/nhl/trades_value.py` (value and attribute). Runs on the v1 wins stat.

## Source
Wikipedia's season transaction pages, 2005-06 to 2025-26 (21 pages; text is free to reuse with credit, and
each row there cites the club or league announcement). This is the working source until Sean decides
otherwise; `what-worked.md` says what a better one would have to beat. Pull the plain-text form of each
page (`index.php?action=raw`), a few seconds apart; the other interface rate-limits after two pages.

## What came out of the parse
- 2,435 trades, 4,535 players, 2,881 picks (420 marked conditional), 481 other items (future
  considerations, cash, rights).
- 84% of traded players match a league id by name. The rest are mostly prospects who never played, plus a
  few name variants (Michael for Mike, Steven for Steve) that still need an alias list.
- Five sides name a club the parser does not know; those trades are skipped (2,430 valued).

## How a side is valued
- A player: the v1 wins he produced for the acquiring club from the trade until he left it, seven seasons
  at most.
- A pick: what its slot usually returns (the draft channel's table), so drafting well or badly is not
  counted twice. Tied to the actual selection for 2,027 of 2,873 picks; a conditional pick, or one that
  cannot be placed, gets its round's average.
- A side's net is what it got minus what the other side got. The general manager is whoever held the chair
  that day (none found for 144 of 4,860 sides).

## First results (trades through June 2022, so the players have had time)
- Biggest wins: Flyers getting Voracek and picks from Columbus, June 2011 (+27.0); Canucks getting Luongo,
  June 2006 (+26.5); Columbus getting Bobrovsky, June 2012 (+24.3); Ducks getting the pick that became
  Gibson, June 2011 (+23.9); Blues getting the pick that became Tarasenko, June 2010 (+18.8); Rangers
  getting Zibanejad, July 2016 (+15.9).
- General managers with 25 or more trades, net wins: Gorton +53 (43 trades), Shero +38 (95), Pleau +38
  (33), Fletcher +36 (78), Sakic +35 (50). Bottom: Poile -65 (127), Waddell -59 (71), Burke -46 (87).
- Most trades are small: 72% of sides land within one win of even; one side's spread is 3.0 wins.
- **Do results repeat?** For the 44 general managers with 30 or more trades, the first half of their
  trades against the second half correlates at 0.23; alternating trades at 0.35. Weaker than drafting
  (0.38), but not nothing.

## What is wrong with it
- **"Until he left" counts re-signings.** A player traded with one year left who re-signs keeps crediting
  the trade. The MLB edition stops at the control the trade came with; this needs contracts to do the same.
- **Conditional picks are approximate**, and some conditions live in footnotes the parser drops, so a pick
  can be tied to the wrong selection. The Arizona-Montreal trade of September 2021 shows +22.1 for Arizona
  largely for that reason. Treat any pick-heavy result as unchecked.
- **Draft-day pick swaps** lean on the page naming the overall number; where it does not, the pick falls
  back to its round's average.
- No salary retained, no cap room, no rentals priced as rentals: a deadline rental that helps win a Cup
  shows as a loss.
- It inherits the wins stat: defensemen run low and goalies are noisy, and several of the biggest wins
  above are goalies.
- Three-club trades are entered on the source pages as separate two-club rows and are valued that way.

## Next
Alias list for unmatched names; read conditions from the footnotes; a contract source so value can stop at
the control traded; then put drafts and trades together into a first general manager card.
