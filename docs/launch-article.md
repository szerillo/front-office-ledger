# We Scored Every MLB Front Office
### Introducing the Front Office Ledger: every trade, draft pick, signing, and waiver claim since each regime took over, graded against expectation

*Draft for publication · numbers as of the 2026 All-Star break*

Anyone who has played Out of the Park Baseball knows the Decision History screen: every move you ever made, with the wins it gained or lost printed next to it, forever. Real general managers have never had to look at that screen. Beat writers grade trades the week they happen and rarely revisit them; fans argue with anecdotes; the actual ledger, the thing that would settle the argument, has never existed in public.

So we built it. The Front Office Ledger ingests every transaction from the MLB Stats API (108,000 rows across all 30 clubs, reliable back to 2005), assembles them into decisions, values every player involved with an open, self-computed metric (Ledger WAR, built from the same public feed, validated within about a win against published WAR), and grades each front office's channels against what those transactions were supposed to return: draft picks against the historical value of their slot, trades symmetrically from both seats over matched windows, waiver claims against zero. Every grade is clickable down to the individual decisions that produced it. Nothing is a vibe.

## The leaderboard

Among regimes with five or more full seasons, the top of the board reads: **Andrew Friedman** (Dodgers, +78 net value above expectation, .614, 12 division titles), **Brian Cashman** (Yankees, +83 since 2005, the longest ledger in the sport), **Alex Anthopoulos** (Braves, +68), **Mike Elias** (Orioles, +58), and among the short-tenure regimes **Matt Arnold** (Brewers, +38 in under four years) grades highest per season. At the bottom: **A.J. Preller** (Padres, −42 over eleven-plus years), **Jed Hoyer** (Cubs, −23), and the small-sample rebuilds in Chicago and St. Louis.

Some of that confirms what everyone believes. The value of a ledger is what it says that nobody's been saying:

**Brian Cashman has quietly run the best draft room in baseball.** His draft channel since 2005 is +58 wins above slot expectation, the highest figure in the sweep, anchored by Aaron Judge at pick 32 but far from carried by him alone. The public narrative about the Yankees is checkbook-first; the ledger says the drafting is the machine.

**The Elias gap is real, quantified, and the whole debate in one row.** Baltimore's front office grades A on decisions (elite drafting at +23 above slot, the best waiver and scrap-heap channel in the sport at +38) and C on results: a .446 winning percentage across the tenure, one division title, and zero playoff game wins. Whether you weight the machine or the harvest is a values question. The Ledger's job is to make sure both numbers are on the page.

**One trade, two winners, and the accounting agrees with itself.** The December 2022 three-team Sean Murphy deal shows up as the worst trade of the Anthopoulos era on Atlanta's card (−13 from their seat, driven by what William Contreras became) and as the best trade of the Arnold era on Milwaukee's (+20 from theirs). Same deal, opposite seats, generated independently by the same rules. When a methodology starts confirming itself like that, you can begin to trust the rows you didn't already have opinions about.

**Preller's grade is really a style diagnosis.** San Diego's −34 draft channel doesn't mean bad scouting; it means his drafted players produce almost nothing *for San Diego*, because they get converted into trade chips, and his trade channel doesn't earn the conversion back. The ledger doesn't hate the aggression. It prices it.

**Selling works.** Arnold's Milwaukee card is a portrait of a front office that sells stars at the peak of their windows (Burnes, Williams, Adames all graded near-even or better from the seller's seat), keeps finding money in other clubs' discards, and extended Jackson Chourio before his debut. Four seasons, four winning teams, and the sweep's best per-season value creation.

## What the grades are, and aren't

Everything here is versioned methodology, not gospel. Free agency is deliberately ungraded in this release: signing value only means something against contract price, and the contracts feed ships next. Sweep windows are calendar approximations of team control. The value metric has documented gaps (no fielding or framing yet, which is why catchers run cold). Grades will move as the methodology improves, and every methodology version is archived so you can see exactly what moved them. Three cards (Orioles, Brewers, Dodgers' Betts decisions) have been promoted to curated precision, with control-window accounting, win-curve leverage, retention-rights option value, and three-lens verdicts; the Betts trade alone has three defensible answers to "who won," and the site shows all of them rather than averaging.

The honest disclosure that matters most: this measures front-office *output against expectation*, not executive souls. Budgets, owners, and luck all live inside these numbers. That's why every regime carries two grades, decisions and results, and why the gap between them is usually the most interesting thing on the page.

The ledger is live, every number is clickable, and the receipts go back decades. Argue with it. That's what it's for.

*Methodology, code, and data: github.com/szerillo/front-office-ledger*
