# NHL draft channel, first cut (v0)

Built Nov 10 2026. Step 2 of `nhl-plan.md`, run on the v0 value stat (`nhl-value-v0.md`). Nothing here is
on the site. Script: `engine/nhl/draft.py`.

## Data, all official
- Every pick from the league's records site, 1995 to 2026 (7,472 picks), with the player's id, birth date,
  the club that made the pick, the date, and the trail of clubs that held the pick before it was used.
- **General manager tenures are on the same site**: 332 regular-season stints by franchise with start and
  end dates. That settles plan item 5 without outside sourcing.

## Method
- A pick's return is the v0 wins he produced while the drafting club could control him: seasons through
  age 26 (on the June 30 that ends the season), or his first seven full seasons, whichever ends first.
- What a slot returns comes from drafts 1998 to 2017 (4,754 picks), the classes whose control years are
  over: averages by pick range, forced to fall as the pick gets later, read off on a log scale.
- Each pick is then held to its own position at that part of the draft. This matters because v0 runs low
  on defensemen: a defenseman returns 45 to 49% of his slot's average in v0 wins, a forward 105 to 130%.
- Net for a pick is return minus expectation. A class is the sum of its picks. The general manager is
  whoever held the chair on draft day.

## What a pick returns (v0 wins over the control years)
| Pick | Wins | Played 100 games in those years |
|---|---|---|
| 1 | 16.6 | 100% |
| 2 | 11.4 | 100% |
| 3 | 7.9 | 100% |
| 4 to 5 | 6.2 | 90 to 95% |
| 6 to 10 | 3.5 to 5.2 | 83 to 90% |
| 11 to 30 | 2.5 to 3.3 | 63 to 78% |
| 31 to 60 | 1.0 | 35 to 37% |
| 61 to 120 | 0.4 to 0.6 | 17 to 23% |
| 121 on | 0.1 to 0.3 | 7 to 12% |

## First results (drafts 1998 to 2017)
- Best picks: Kucherov (2011, 58th, TBL) +19.6; Jamie Benn (2007, 129th, DAL) +18.3; Vasilevskiy (2012,
  19th, TBL) +17.8; Pastrnak (2014, 25th, BOS) +17.8; Gaudreau (2011, 104th, CGY) +17.3; Jason Robertson
  (2017, 39th, DAL) +17.2.
- Worst picks: Yakupov (2012, 1st, EDM) -16.7; Stefan (1999, 1st, ATL) -14.4; Nolan Patrick (2017, 2nd,
  PHI) -13.2; Svitov (2001, 3rd, TBL) -10.6.
- Best classes: DAL 2017 +32.8, ANA 2011 +30.0, TBL 2011 +27.7, CAR 2010 +24.5, MTL 2005 +23.4.
- Worst classes: EDM 2012 -19.7, ATL 1999 -19.6, PHI 2017 -17.6.
- General managers with four or more drafts, net wins per draft: Yzerman +4.8 (8 drafts), Treliving +4.4
  (4), Ferguson Jr. +4.3 (4), Cheveldayoff +4.3 (7), Nill +4.1 (5), Bob Murray +3.7 (11). Bottom:
  Tambellini -11.7 (4), Dudley -6.4 (6), Milbury -4.6 (8).
- **Does drafting repeat?** For the 40 general managers with six or more drafts, the first half of their
  drafts against the second half correlates at 0.38. Some of it is skill.

## What is wrong with it
- It inherits v0. Holding picks to their own position removes the level problem for defensemen but not the
  ranking among them: a shutdown defenseman still looks like a miss.
- A first overall pick is held to 16.6 wins (19.5 for a forward), so a merely good one grades badly:
  Nugent-Hopkins comes out -10.5.
- No chair was found for 212 of the 4,754 picks (gaps between one general manager's end date and the
  next one's start). Those picks count for the club and for no one.
- Credit goes to the general manager alone; scouting directors are not in the data.
- The draft lottery and where a club picks are not the general manager's doing; this version grades the
  pick against its slot, which already removes that.
- Classes after 2017 are not graded because their control years are still running.

## Next
Trades and contracts still need a source (see the plan). The pick trail in the draft data means every
traded pick can be followed once trades exist.
