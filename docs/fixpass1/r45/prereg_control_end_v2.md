# Pre-registration: service-time control end, retry (round 45, written before the sample is drawn or any player looked up)

## What changed since round 44, and why (training data only)
Round 44's counter missed 3 of the 7 players looked up. Day-by-day ledgers of those three (round45.md) show:
- Ryan McMahon: a real counting error. The feed has "assigned to Albuquerque Isotopes" on 2018-06-03 with no option;
  the counter took him off the roster, but he played 12 MLB games from Jun 3 to Jun 20 and was optioned on Jun 21.
  18 days lost (106 counted, 124 real). Fixed: v2 below.
- Chris Archer: not a miss. Round 44 recorded the truth as "after 2018"; MLB Trade Rumors (Apr 3, 2014) says he
  entered 2014 with 156 days of service and was under club control through 2019. The counter has 157 days and 2019.
- Matt Moore: unresolved. The counter has 1,031 days after 2017, one short. His Aug 3 to Aug 31, 2015 option (29
  days) is lost under the rule. The "after 2017" truth was written when he signed in Dec 2011, before that option;
  no later published service figure was found. Not used to tune anything.
Corrected round 44 tally: 5 of 7 right (still short of its 19 of 20 bar; round 44 stays a fail).

## The rule under test (v2, frozen: docs/fixpass1/r45/svc_classify_v2.py)
Round 44's rule (prereg_control_end.md) with one change: a bare "assigned to <minor-league club>" record does not take
a player who is on the active roster or injured list off it; only an option, outright, release or restricted-list
placement does. No other change. The day an option is filed stays off (Moore's one day is not tuned for).

## Sample (draw_sample_v2.py, seed 20261145)
Frame: round 44's 184 players minus Donaldson, Olson and all 20 of the round 44 sample. Groups, drawn in order:
5 late arrivals (MLB debut after June 1), 5 optioned in a season after their debut season (not already drawn),
10 from the rest. Seeded replacement lists per group.

## Truth
The last season of club control on service time alone (ignoring contract options), from, in order of preference:
(1) a published service-time figure (X.YYY) dated after his last option stint of 20 days or more, carried forward;
(2) a public report (MLB Trade Rumors, MLB.com, ESPN, AP, CBS, The Athletic) stating the season he would reach free
agency or the season he is under control through. A statement dated before a later season in which he lost 20 or
more days to an option is not used. If no usable source is found in two searches, the next player on that group's
replacement list is used and the replacement is reported.

## Pass bar
At least 19 of 20 correct. Training players are reported separately and do not count.

## If it passes
v2 goes into the regrade, then docs/fixpass1/r44/prereg_grades_ranks.md runs as written.

## If it fails (fallback, fixed now)
Stop counting service from transactions. Control end comes from published service-time figures where they exist
(a file listing each player, the figure, its date and its source). Where none exists, the old rule stays and the
control end is labelled "estimated" on every page that shows it (player pages, trade pages with control years, the
Deal Desk control column and the simulator), with one line in the methodology. No retuning of the counter after a
failed run.
