# Pre-registration, round 21: what happens after the fa97 field check failed

Written Nov 11 2026 before any new search for these rows. Committed before the first new search; the
commit time is the proof of order.

## Context

Round 20 (`a94dd4b`, results `986f616`) failed the fa97 bar on years (3 unverified) and total (4 unverified,
1 mismatch). The four rows without a listed source:

| Row | Club, date | Card terms |
|---|---|---|
| Jeff Conine | BAL, 2006-01-11 | 1 yr, $1.7M |
| Dustin Hermanson | SF, 2003-12-02 | 1 yr, $0.8M |
| Elmer Dessens | LAD, 2004-12-08 | 1 yr, $1.6M |
| Antonio Alfonseca | ATL, 2003-12-23 | 1 yr, $1.4M |

Already seen in round 20, disclosed so it is not mistaken for a new finding: unlisted sites gave Conine
$1.7M (thisdayinbaseball), Hermanson $800K and Dessens $1.3M (a salary aggregator), Alfonseca "over a
million" and $1.5M (blogs); AP said Alfonseca's terms were not disclosed. Dessens may therefore turn out to
be a mismatch, and the re-score can fail on mismatches as well as on missing sources.

## Hypothesis

With a further fixed search, the four rows can be sourced, and fa97 then meets the round 20 bar on years
and total.

## Method (fixed now)

- Same 20 fa97 rows as round 20 (seed 20261134). No new draw, no rows added or dropped.
- Only the four rows above are re-searched. The other 16 keep their round 20 scores.
- Same source order as `a94dd4b`: (a) AP, a newspaper, CNN/SI, ESPN or MLB.com; (b) a salary table
  (Baseball-Reference by WebFetch, Baseball Almanac); (c) Spotrac. Wikipedia, blogs, aggregators and repo files
  still do not count. A newspaper page reprinting the AP "free agent signings" list counts as (a).
- Same tolerance: years exact; total within max($0.1M, 2%); guaranteed buyouts count toward the total.
- Search budget: at most 6 web searches and 4 page fetches per row. When the budget runs out, the row stays
  "unverified".
- A listed source that disagrees with the card is a mismatch, even if another listed source agrees: take the
  highest-ranked source; within a rank, a disagreement makes the row "disputed", scored as a mismatch.

## Metric and pass bar (unchanged)

Per field (years, total) over the 20 fa97 rows: mismatches at most 1 and unverified at most 2.

## Decision rule

- Both fields pass: fa97 terms stay on the site as they are. Fassero, Furcal and any new mismatch go in as
  proposed overrides for Sean.
- Either field fails: recommend labelling pre-2009 free-agent terms from the fa97 source "unverified" on the
  site (contract line and grade tooltip) until a per-row check exists. Deploying that label is Sean's call.
- Not allowed after the fact: widening the tolerance, adding source types, re-searching rows that already
  scored, or changing the bar.
