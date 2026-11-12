# Round 48 (Nov 12, 2026)

Published-control-end grades stay held. Nothing was re-scored. No variants of I1 were run.

## 1. The 13 untraced I1 changes: recalibration or tracer reach

Method (diag48.py, reads the saved Z_X6 and I1 runs only): for each untraced letter or overall grade, list the
entries that moved between runs and look for a changed-control player among them after folding accents and
matching ids. Result: 1 tracer reach, 12 recalibration (diag48.json).

Tracer reach, worked example: Phillies current regime, extension channel. Jesus Luzardo's 2026 extension moved
from +2.1 to -0.8 (channel net 3.0 to 0.4). Luzardo is a changed-control player, but the evaluator matched
extension rows by name, and the engine row says "Jesus" while the player file says "Jesús". The accent broke the
match, so a traced change was counted as untraced.

Recalibration, worked example: Tigers under Dave Dombrowski, extension channel (4.1 to 6.3). Ten extensions moved
and none involves a changed-control player. The engine re-fits the league-wide extension class rates from all
outcomes; with 846 control ends changed, the rates moved (veteran 0.370 to 0.347, arb 0.167 to 0.152), so every
extension is now measured against a lower expected return. Miguel Cabrera's 2008 arb extension: 22.3 to 22.7.
The draft side works the same way: draft_calib k_pooled 1.511 to 1.544 and the per-class factors moved (2004:
1.502 to 1.525), which is why Joe Garagiola Jr.'s Arizona draft net fell 30.2 to 29.4 (Stephen Drew 2004 expected
4.8 to 4.9) and his overall grade dropped 70 to 65. Two letters moved with no entry moving at 0.1 precision
(phi-matt-klentak ext, bos-dan-duquette draft): the grading spread itself shifted.

Reading: the bar failed mostly because the engine re-fits its calibration from the outcomes the change touches,
not because of the tracer. A traced design would have to freeze the calibration files or count calibration as a
traced path. That is a new prereg, not part of this round.

## 2. Kurtz and Horton award service credit (deployed)

Rule: a top-two Rookie of the Year finisher without a full first service year is credited with one.
Nick Kurtz (AL winner 2025, 159 days) and Cade Horton (NL runner-up 2025) both had full 2026 seasons on the
active roster or MLB injured list (no options in the feed), so each is 2.000 at the end of 2026: control through
2030, not 2031 (MLBTR; CBS Sports says Kurtz's free agency moves to the 2030-31 offseason).

2026 top two checked before touching anyone: Sal Stewart and Carson Benge (NL), Kevin McGonigle and Parker
Messick (AL). MLB.com (BBWAA results) has Benge second with 7 first-place votes. Benge's contract was selected
Mar 25, 2026 and he was never optioned; the counter already gives him a full 2026 year (1.000). The same is true of
the other three. The credit changes nobody from 2026.

Desk diff, live vs staged (desk_live.json, desk_staged.json): 2 of 1,982 players changed, exactly as predicted.
Kurtz: control end 2031 (estimated) to 2030 (not estimated), surplus 12.23 to 11.26. Horton: 2031 (estimated) to
2030, surplus 2.58 to 2.49. Club horizon 2031 wins: ATH 18.9 to 15.7, CHC 16.4 to 15.9; ATH's 2031 rank goes 5 to
14 and seven clubs move up one. No card letter or grade reads Desk control ends, so no letter or grade moved and
no corrections entry is required.

## 3. Counter and published-figure fixes (built, dry run only, no regrade)

Elected free agency (engine/svc_fetch.py): the feed files "elected free agency" under the DFA code, which the
counter read as limbo, so a player left unsigned kept accruing. New line: DFA plus "elected free agency" takes the
player off. Plant plant_efa.py: fails on the old code (exit 1), passes on the new (exit 0); the r47 Rule 5 and
purchase plants still pass. Dry run on the 184-player frame (dry_efa.json): 36 players change, 33 stay at six
years or more either way, 2 cross six (Walden 15.0 to 5.0; Sergio Santos 14.119 to 3.115), 1 stays under six
(Logan Ondrusek 4.121 to 3.002). 25 of the 36 change in 2026. Counter-example found in the dry run: Tyler Kinley
elected free agency in Nov 2025 and came back to Atlanta, filed only as "assigned to Atlanta
Braves"; the new rule takes him off and he loses 65 days (172 to 107). Not fixed: needs its own prereg.

Team-heading match (build_pub_v2.py): a same-name row keeps the candidate whose last club before the post matches
the team heading. Plant plant_heading.py: fails on the old build (exit 1), passes on the new (exit 0).
Dry run: 26 rows resolved, 13 players added, 0 control ends changed, 0 Desk changes (none is on the 2027 list).
The motivating case is not resolved: Luis García Jr. (2027 list, Yankees heading, 5.142) still ties with Luis
Garcia the pitcher (677651), because the feed has both last with the Yankees. Breaking that needs the Jr. suffix,
which the name normalizer strips. New prereg if wanted.

## 4. Suites one at a time

allsuites.sh now takes an exclusive flock on /tmp/fol_suites.lock and exits 75 if another run holds it. Inside a
run the suites go one after another. lockdemo.txt: a second run started 3 seconds after the first refused to
start ("second exit=75"). The Desk diff harness also ran under the same lock.

## Challenges

A. The premise mixes two estimates. The 7 of 28 misses (25%, Wilson 95% interval 13% to 43%, all early) measure
the grading rule (debut plus six seasons). The Desk's "estimated" label sits on the transaction counter, which
leans the other way: against 778 published figures it is off by a year or more for 146 (18.8%, interval 16.2% to
21.7%), and 126 of the 146 run late (counter says control lasts longer). The live label does not say which way
either one leans. Proposed methodology lines, disclose only:
- "Desk control ends marked estimated come from our own count of roster transactions. Checked against 778
  published service figures, 19% are off by a year or more (95% range 16% to 22%), and most of those run late."
- "Grades count control from a player's debut. On 28 extended players with a public free-agent year, 7 (25%,
  95% range 13% to 43%, small sample) ended earlier than the real control, never later."

B. Yes. The CTRL_FLIP mark asks what happens if control runs one season longer, and every measured miss of the
grading rule runs early. J.P. Crawford: the debut rule (Sept 2017 debut) ends control in 2023, his real control
ran through 2024; one more season lands exactly on it. Marco Gonzales (-3) is only a third covered by +1.

C. The 2026 Super Two cutoff (2.133) was reported on Nov 5, 2026 (ESPN). The MLBTR 2027 post still carries
the "not finalized" caveat on a Nov 12 re-pull, and diff_mlbtr.py finds 0 of 296 figures changed against the
Oct 2 copy. Plan: re-pull daily through the non-tender deadline, then weekly until the caveat is gone; any
changed figure rebuilds PUB_SVC and goes through the deploy gates as a data change with a corrections entry if a
displayed control end moves. Lucchesi test case: he is not on the 2027 list. The 2026 post re-pulled today still
shows 5.047 (no caveat, unchanged), against 5.112 the year before, an impossible drop that MLBTR has not revised.
Our build keeps the latest list, so 5.047 stands; he is not on the Desk's published set.

D. Untested assumption in the r47 Rule 5 fix: that Rule 5 picks reach the counter as a December DR record.
Tested on 10 spring returns (seed 20261248, chalD.json): of the 8 with an acquisition record, 7 were filed as
"claimed off waivers" (CLW) and 1 as R5; none as DR. The assumption fails, but harmlessly: CLW and R5 were already
read. The returns themselves (code RTN) leave the player on until his next minor league assignment, so 2 of 10
picked up phantom days with 0 MLB games (Tyler Jones 1, Drew Ferguson 7, the 2019 Tokyo opener). Both predate
r47 (same count before and after the fix).

## Deploy record

Gates: 19/19 suites on live before (fec1e64 page), 19/19 on staged (t_build after the re-pin), gate_index CLEAR
(8 data files live with the right bytes). Commits: index.html 9c6a0fc (md5 973bf104), t_build fixture b12ebc1,
engine/svc_fetch.py 71c7200 (no rerun, no regrade). Live md5 matched staged after about a minute.
Pages changed: the Desk for Kurtz and Horton, the ATH and CHC club horizons and the league 2031 column, all as
predicted.
Post-deploy: 19/19 on a fresh clone at 71c7200, run under the new lock.
