# Fix pass 1, amendment 3 (Nov 11, 2026): rule 12 result and its replacement

## Rule 12 as pre-registered (d6656e3), counted on a copy of V0rec (trade_book, h2h_deals, offseasons_build rerun)
- Winter move texts differing from live: 66 (rules 1 to 11 alone: 48). Head-to-head deal texts: 173 of 1,051
  (rules 1 to 11: 181). Values changed: 0.
- 12b made spelling worse: for 1985-2008 players the Retrosheet row carries the accents and the later feed row
  does not (Ramón Hernández 2003 archive rows vs "Ramon Hernandez" on the 2013 feed row). Live shows the archive
  spelling because production reads rows in insertion order and the backfill was appended after the feed.
- What produces live's choice: storage order ("first read" for ties, "last read" for names). That is the same
  nondeterminism class as rules 1 to 11: a shuffled or rebuilt ledger changes it. No content rule reproduces it
  (production seats: 1,112 ascending by id, 951 descending, 593 mixed).

## Exploration after the count (disclosed: chosen after seeing the numbers above)
| Variant | Names | Tie order | Winter texts vs live | H2H texts vs live |
|---|---|---|---|---|
| rules 1-11 | latest row | id as text | 48 | 181 |
| 12 (pre-registered) | feed first | value, higher id | 66 | 173 |
| A | archive first | value, lower id | 59 | 167 |
| B | archive first | id as text | 59 | 181 |
| C | archive first | value, higher id | 51 | 173 |

## Rule 12 (replaced)
- 12a unchanged: players ordered by value, highest first; equal values go to the higher MLBAM id.
- 12b replaced: a player's display name is the Retrosheet archive spelling when an archive row exists (it keeps the
  accents), otherwise the latest-dated feed name.
Reason for the change is spelling quality, not matching live; 0 values change under any variant. The md5 bar runs
on this engine (round 6). Round 5 (rules 1 to 11) is stopped and not judged.
