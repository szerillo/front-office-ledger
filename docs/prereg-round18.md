# Pre-registration, round 18: field-level check of the rebuilt sweep_tx regrade

Written and committed before any row is drawn. Commit time is the pre-registration time.

## Population
The 1,717 priced free-agent signing rows produced by `fa_grade.py` when run on the `sweep_tx` table rebuilt from
the public MLB transactions feed (`tests/tools/sweep_tx_build.py`), current and archive regimes together
(`/tmp/sweep/allfa.json`, key: signing date, player id, club, regime start).

## Draw
25 rows, `random.Random(20261132).sample(sorted(rows), 25)`, script `tests/tools/prereg18_draw.py`.

## Fields and sources
1. Sign date: the rerun row's date against the published card row for the same player and club (cards.js) and
   against the league feed's transaction for that signing. Mismatch: any day's difference from the feed.
2. Team: the rerun row's club against the club in the feed transaction. Mismatch: different club.
3. Years and total (so AAV): the rerun row's years and total against one outside source (AP, a club release,
   MLB.com, or Spotrac when none of those gives the terms). Mismatch: years differ, or total differs by more than
   $0.1M (guaranteed money, signing bonus included, options and incentives excluded).

## Report
Mismatches per field out of 25 with Wilson 95% intervals, each mismatch with its source.

## Not allowed after this commit
Changing the population, seed, fields, tolerances or sources, or dropping rows by hand.
