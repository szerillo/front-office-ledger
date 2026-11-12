# Fix pass 1, amendment 2 (Nov 11, 2026, before the rule is coded or counted)

Amends `docs/prereg-fixpass1.md` (5e81190) and amendment 1 (8e79455). The md5 bar is unchanged.

## What was found (V0rec, the patched build on ledger_v2, against live)
49 trade headlines in the winter table differ from live with the same value. Two kinds:
- Spelling (9 cases): rule 3 takes the display name from the latest-dated row. For 1985-2008 deals that is often
  the Retrosheet row, which has no accents ("Joaquin Arias" for live's "Joaquín Arias").
- Ties (40 cases with both ids known): two players with the same value; live picked the one read first from the
  production ledger. Live's pick is the higher MLBAM id in 39 of 40. Production's seat order is not a rule
  (1,112 seats ascending by id, 951 descending, 593 mixed), so "first read" cannot be reproduced and is the
  same nondeterminism class as rules 1 to 11.

## Rule 12 (pre-registered here, coded after this commit)
- 12a. Wherever players are listed or one is picked by value (winter headline lead, the "Got X and Y" text, the
  head-to-head deal text), they are ordered by value, highest first; equal values go to the higher MLBAM id.
- 12b. A player's display name is the latest-dated name on a feed row (not a Retrosheet archive row); the
  archive spelling is used only when the feed has no row for him.

## What is counted (no threshold; the counts go to the correction note)
1. Of the 49 headline pairs, how many still differ from live after rule 12.
2. Head-to-head deal texts that differ from live, before and after rule 12.
3. Any value change from rule 12 (expected: none; any value change fails it).
Rule 12 joins the round 6 engine; the md5 bar is rerun on it.
