# Before a new rule ships

Written Nov 11 2026, after 5 of the day's 9 root causes turned out to be rules written that same day (the trade
OPEN rule twice, the unstarted-extension rule, the pre-2021 cutoff, the arbitration-season assumption). A "rule"
is any new condition that decides a label, a grade, a window or which records count: a page function such as
folDecOpen or folTradeOpen, an engine change, or a data transform.

Every step below goes in the commit's worklog entry. A rule that skips a step does not ship.

1. **State the rule in one sentence, and the engine rule it must agree with.** If the page and the engine
   disagree (the engine ends a trade window at a release; the first page rule did not), the engine's rule is
   the reference unless the change is to the engine itself.
2. **Write the failing tests first.** At least one real case the rule must change and one real case it must
   leave alone (Utley 2015 CLOSED and Trammell 2019 OPEN; Vieira released and Baker claimed). Show both against
   the current page: the first fails, the second passes.
3. **Count what moves.** Run the rule over the full population, not a sample: how many decisions, labels or
   grades change, by year. A count far from what the change intends is a stop (694 trades reopened is not
   "a few").
4. **Hand-check 10 of the changed items, seeded.** State the seed before drawing. Check each against a source
   outside our data (Baseball-Reference transactions or salaries, the league feed, a named report). Report how
   many of the 10 are right. Two or more wrong means the rule is not done.
5. **Hand-check 10 of the items it did not change, from the same population,** when the rule can also miss
   (an OPEN rule can wrongly keep something open). Same seed rule, same bar.
6. **Plant one wrong case in a copy and show a suite fails.** If no suite fails, add the check that does.
7. **Run all suites, including `t_grades`.** If grades move, regenerate the snapshot only with
   `UPDATE=1 REASON="..."`, which writes the diff and the reason to `docs/grade-changes.md`. If grades should
   not move and do, stop.
8. **Ship, then re-run the suites against the live page.**

Lower the bar only for a rule that changes wording and nothing else. Data transforms (a research file, a
contract book row) follow the same steps, with step 4 checking rows against the original source.
