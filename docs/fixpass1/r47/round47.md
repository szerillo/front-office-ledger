# Round 47 (Nov 12): grades on published control end (pre-registered, failed), control-end mark, counter codes

## 1. Pre-registered run (prereg d845b74, run I1, evaluated by eval_i1.py exactly as written)
846 published players have a control end different from the debut rule (CH).
| Metric | I1 | Bar | |
|---|---|---|---|
| Channel letters changed | 59 of 662 | <= 150 | ok |
| Overall grades changed | 23 | <= 40 | ok |
| Untraced letters + overall | 12 + 1 = 13 | <= 5 | FAIL |
| Untraced trade-side nets moving > 0.2 | 72 | <= 50 | FAIL |
| Band: Toronto 2012-13 | 2nd from bottom, margin 31.6 (live 1st, 31.7) | 1st/2nd, >= 90% margin | ok |
| Untraced pages | 90 | <= 50 | FAIL |
Result: FAIL. Nothing deployed from it, no variants. Ten of the 12 untraced letters are extension channels (two draft); the
calibration refit and the tracer's reach (extension lists by name, winter rows list top decisions) are the likely
sources, but that is not tested and changes nothing: the run failed as written.

## 2. "Depends on control end" mark (index, computed on live grades since step 1 failed)
The 133 channel letters that change when every player's control runs one season longer (round 45 dry run C1 vs the
live engine) carry a "depends on control end" chip on their front office pages; all 133 land on page regimes. One
methodology sentence added. index fec1e64 (live md5 5babcf5c = staged), t_build re-pin bea710a, 19/19 before (live) and after (fresh clone); staged run 19/19 (t_leak rerun alone after a browser crash under two parallel runs).

## 3. Counter codes (engine/svc_fetch.py, no rerun, no regrade)
Rule 5 draft (DR, December, major league club) and contract purchase (PUR, major league club) now put a player on.
plant_svc.py: before the fix rule5_draft_puts_on false, purchase_puts_on false (exit 1); after, all four plants true
(exit 0). Recount: Herrera 2015-18 now 172 each; Walden 2010 43 days. Walden also shows a further gap: "elected free
agency" (DFA code) is not read, so he stays on after 2016 (not fixed, noted).
Calhoun 2023: explained. Traded from the Dodgers' Triple-A club to Cleveland on Aug 4 and played 43 MLB games from
Aug 5 to Sep 30; the feed has no separate selection, and the counter keeps a traded player's prior roster state.
A rule gap for trades straight onto the active roster, not missing data.

## 4. Challenges
A. Skenes: MLB Trade Rumors, Projected Arbitration Salaries For 2027 (Oct 2, 2026): "Paul Skenes (3.000)". Rule:
top-two Rookie of the Year finish by a qualifying prospect without a full service year = full year retroactively;
Skenes won the 2024 NL award with 142 days. Other credited players: Rutschman and Harris (2022), Bibee (2023), Skenes
(2024), Kurtz and Horton (2025). Handled: Rutschman, Skenes (published), Harris, Bibee (contracts cover control).
Not handled: Kurtz and Horton show control through 2031 (estimated); with the credit it is 2030. 2026 runner-ups
(NL: Carson Benge) not yet checked.
B. 28 extended players with no arbitration figure and a public free-agent year (seed 20261147, chalB_sample.json;
Iwakuma dropped as a posted free agent, Bummer had no usable source): debut rule right for 21, off by a year or more
for 7 (25%), all early: Gonzales -3, Kluber -2 (MLBTR; AP says -1), Crawford, Díaz, Olson, Barnhart, Craig -1.
Truths are statements made at signing, before any later option time.
C. The premise does not hold: 18 of the 32 dropped same-name rows have a candidate on the Desk (ambiguous.json), e.g.
Luis García Jr. (2027 list, 5.142), Will Smith (LAD), Austin Adams, Diego Castillo, Josh Bell. Fix proposed: resolve
by the MLBTR team header against each id's club that season.
D. Untested assumption: the MLBTR column is final official service at the end of the prior season. Two checks:
(1) 16 of about 1,250 consecutive-year pairs are impossible (a gain over 172 days or a loss), 1 of them changes a
control end (Joey Lucchesi 5.112 then 5.047); (2) the 2027 post itself says service data is not finalized. Five full
2026 seasons (Sulser, Steele, Hentges, Bender, Gilbert) gain exactly 1.000, matching our 172-day count.
