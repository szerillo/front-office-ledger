# Pre-registration, round 11 (Nov 11, written about 16:45 UTC)

Committed before any of the runs or checks below. What was already done before this commit is listed so the
order is on the record.

Already done before this commit:
- The list of trades the release / free-agency rule closed (147 on the current page) and a draw of 15 from it,
  seed 20261121 (`tests/tools/closed_by_release.mjs`). None of the 15 checked yet.
- Three 2017 deadline deals worked by hand for the proration test (Martinez, Darvish, Upton; part 1 of
  `tests/tools/proration_check.py`). The population run (part 2) has not been run.

## A. $0 seasons: random 40
Draw 40 of the 802 seasons with seed 20261122 (LCG as audit_sample.mjs, over the sorted population from
`zero_salary_sample.py`). For each: salary from Baseball-Reference (one fetcher, under 10 requests a minute,
honoring Retry-After) and a second source (Spotrac or Cot's) for at least 10 of them. Report: share paid above
$0.75M with a 95% Wilson interval, the extrapolation to the 802 with that interval, and the same for the
pull-order 40 so the two can be compared. If the random share's interval excludes the pull-order share, say the
pull order is biased.

## B. 15 trades closed by the release / free-agency rule
For each of the 15: confirm the ending event (release, free-agent filing, free-agent or minor-league signing)
against a source other than the league feed, and that no piece in the deal still has a live window. Error = the
trade should still read OPEN, or the event did not happen as dated. Report errors / 15 with a 95% Wilson interval.
A special check: a free-agent filing followed by re-signing with the same club (a non-tender and re-sign) counts
as an error if the window should have continued.

## C. Proration of the trade season
Part 2 of `tests/tools/proration_check.py`: every in-season trade's trade-season charge re-prorated by the days
left in the season instead of the share of stint rows. Material on the same four tests as
`docs/prereg-arb-shadow.md` (42+ sides move 1 win; any top/bottom-25 change; any club 2+ ranks; 10+ flips).
