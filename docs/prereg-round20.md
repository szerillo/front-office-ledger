# Pre-registration, round 20: field check of 1998-2008 signings

Written and committed before any row is drawn. Commit time is the pre-registration time.

## Why
The round 18 check (d8f8910) drew from 1,717 rows built without the Retrosheet backfill, so no 1998-2008 signing
could be drawn. The 675 contracts (674 in this frame) whose terms come from the `fa97` source have never been checked against
anything outside the repo.

## Population (frame)
`tests/tools/prereg20_frame.json`, committed with this file: every graded free-agent signing dated 1998-2008 in
the deterministic rebuild, 899 rows (674 with `fa97` terms, 225 with `espn` terms), Dreifort LAD 2000 excluded
because it was in the round 18 frame.

## Draw
Stratified, seed 20261134, `tests/tools/prereg20_draw.py`: 20 from the 674 `fa97` rows and 5 from the 225 `espn`
rows. Weighted toward `fa97` because it has never been checked; the 5 `espn` rows give a small comparison with the
source checked in round 18. Results are reported per stratum, never pooled without weights.

## Fields and sources
1. **Sign date.** Against the Retrosheet transaction file (internal check of the backfill) and against one outside
   report (AP or another newspaper, CNN/SI, ESPN, MLB.com). Match: outside date within 7 days of the row
   (agreement and announcement dates differ). Retrosheet must match exactly.
2. **Club.** Against Retrosheet and the same outside report. Exact.
3. **Years and guaranteed total (so AAV).** Counts as a source for `fa97` terms, in this order:
   (a) a contemporaneous news report naming years and guaranteed dollars (AP or another newspaper, CNN/SI, ESPN,
   MLB.com); (b) a salary table whose seasons under the deal sum to a total (Baseball-Reference player page read
   with WebFetch, not the Baseball-Reference tab in Sean's Chrome; Baseball Almanac); (c) Spotrac. Not a source: Wikipedia alone, fan
   blogs, the repo's own files. Match: years equal and total within $0.1M or 2%, whichever is larger. Options and
   buyouts count only if guaranteed. A row with no source after (a) to (c) is **unverified**, reported
   separately, never counted as a match.

## Pass bar
Per field, per stratum: mismatches with Wilson 95% intervals. The `fa97` source passes a field if it has at most 1
mismatch in 20 (upper bound about 24%) and at most 2 unverified rows. Anything worse means `fa97` terms need a
full check before launch.

## Not allowed
Changing the frame, seed, strata, fields, tolerances or sources after the draw, or dropping rows by hand.
