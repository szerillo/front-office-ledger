# We Scored Every MLB Front Office
### Introducing the ledger: every trade, draft pick, signing, extension, and waiver claim since each regime took over, graded against expectation

*Draft for publication · numbers as of the 2026 All-Star break · sweep v2*

Anyone who has played Out of the Park Baseball knows the Decision History screen: every move you ever made, with the wins it gained or lost printed next to it, forever. Real general managers have never had to look at that screen. Beat writers grade trades the week they happen and rarely revisit them; fans argue with anecdotes; the actual ledger, the thing that would settle the argument, has never existed in public.

So we built it. The ledger ingests every transaction from the MLB Stats API (108,000 rows across all 30 clubs, reliable back to 2005), assembles them into decisions, values every player involved with an open, self-computed metric (Ledger WAR, built from the same public feed, validated within about a win against published WAR), and grades six channels against what those transactions were supposed to return: draft picks against the historical value of their slot; trades from both seats over control windows, with each delivered season weighted by pennant-race leverage and discounted back to the deal date; free agency against 1,594 real contracts net of cost, with qualifying-offer signings charged the draft pick they forfeit and deferral-heavy deals costed at CBT value; extensions against the extension market for the player's service class; international signings against their bonus-pool class; waiver claims against zero. Player development is its own grade, marked to market from sixteen years of top-100 prospect lists. Every grade is clickable down to the individual decisions that produced it. Nothing is a vibe.

## The leaderboard

Per season of tenure, the board reads: **Matt Arnold** (Brewers, +14 wins above expectation per year across three and a half seasons, the sweep's best rate), **Alex Anthopoulos** (Braves, +94 total, +11 per year), **Andrew Friedman** (Dodgers, +91, with an A+ in development and three rings), **Mike Elias** (Orioles, +56), and **Chris Antonetti** (Cleveland, +51 on the sport's thinnest payrolls). At the bottom: **A.J. Preller** (Padres, −66 over eleven-plus years), **Jed Hoyer** (Cubs, −28), and the early returns on the Getz and Bloom rebuilds.

Some of that confirms what everyone believes. The value of a ledger is what it says that nobody's been saying:

**Brian Cashman has quietly run the best draft room in baseball.** His draft channel since 2005 is +58 wins above slot expectation, the highest figure in the sweep, anchored by Aaron Judge at pick 32 but far from carried by him alone. The public narrative about the Yankees is checkbook-first; the ledger says the drafting is the machine, and the checkbook actually grades below water: the FA channel is −32 net of cost, and the Severino and Hicks extensions burned another 12.

**The Elias gap is real, quantified, and the whole debate in one row.** Baltimore's front office grades A on decisions (elite drafting at +23 above slot, the best scrap-heap channel in the sport at +38, a farm the development grade loves) and D on results: a .446 winning percentage, one division title, two playoff trips, zero playoff series wins. Whether you weight the machine or the harvest is a values question. The ledger's job is to make sure both numbers are on the page.

**Leverage changed the verdicts, and it should have.** Sweep v2 weights every delivered season by where the receiving club sat on the win curve: wins handed to an 89-win team count nearly double, wins on a 70-win roster count two-thirds. Deadline adds to contending Braves and Brewers teams got more valuable; selling badly while contending got uglier. The same upgrade flipped the Burnes trade from "worst decision of the tenure" to a fair playoff-push price on Baltimore's card.

**Preller's grade is really a style diagnosis.** San Diego's −35 draft channel doesn't mean bad scouting; it means his drafted players produce almost nothing *for San Diego*, because they get converted into trade chips, and the conversion doesn't earn it back. The extensions channel adds another −21, anchored by Tatis at −15 so far against even the early-career extension market. The development grade, +37, is the counterweight: the machine keeps making prospects. The ledger doesn't hate the aggression. It prices it.

**The best extension ever signed is not close.** Graded against what arb-years extensions typically pay, Cleveland's 2017 José Ramírez deal (five years, $26M) returns +20 wins against the class market, the best single extension in the book. Atlanta's famous 2019 pair (Acuña, Albies) grades merely good, because the class baseline already expects extensions to be team-friendly; the skill is picking the right player, and Ramírez was the rightest.

**The rental market is cheaper than the anguish.** From 237 deadline rental deals classified exactly from the league feed: a star rental win costs about 0.8 wins of eventually-realized value, the median deadline rental costs approximately nothing that ever materializes, and more than half of rental buys deliver under 0.3 wins. Boston's return for one expected year of Mookie Betts was roughly market rate. The criticism was never the price; it was choosing to be a seller of that asset at all.

## What the grades are, and aren't

Everything here is versioned methodology, not gospel. Control windows are derived from actual roster continuity, not service-time records. The value metric has documented gaps (no fielding or framing yet, which is why catchers run cold). Extension-market discounts are documented assumptions until the book is big enough to fit them empirically. Recent-era rental ratios are right-censored while surrendered prospects mature. Grades will move as the methodology improves, and every version is archived so you can see exactly what moved them.

The honest disclosure that matters most: this measures front-office *output against expectation*, not executive souls. Budgets, owners, and luck all live inside these numbers. That's why every regime carries three grades: decisions, development, and results, and why the gaps between them are usually the most interesting thing on the page.

The ledger is live, every number is clickable, and the receipts go back decades. Argue with it. That's what it's for.

*Methodology, code, and data: github.com/szerillo/front-office-ledger*
