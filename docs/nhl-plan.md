# NHL edition: plan

Written Nov 10 2026, after Sean said the NHL comes next once MLB is settled. Nothing here is built. The data
checks below were run that day from the build machine; everything else is a proposal.

## What carries over from MLB as is
- The idea: every decision a front office makes, graded against what a typical club got from the same kind
  of move, in wins, by channel (draft, trades, free agency, extensions, waivers), rolled into a score.
- The page: one file, the five-door nav, report cards, rankings, heists, winters, the Wire, the games, share
  pages with previews, the test suites, and the upload-only deploy.
- The upkeep pattern: small JSON files a scheduled task can refresh without touching the page.

## What was checked on Nov 10
| Need | Source | Result |
|---|---|---|
| Skater seasons (goals, assists, shots, ice time by situation) | api.nhle.com/stats/rest/en/skater/summary, /timeonice | Works back to 1998-99 (814 skaters that season) |
| Goalie seasons (shots against, saves, starts) | .../goalie/summary | Works (2005-06 checked) |
| Hits, blocks, giveaways | .../skater/realtime | Works for recent seasons; start year not checked |
| Team seasons (points, goals for and against) | .../team/summary | Works |
| Every draft pick | api-web.nhle.com/v1/draft/picks/<year>/<round>, records.nhl.com/site/api/draft | Works, 1979 to 2026 |
| A player's club by season, draft details | api-web.nhle.com/v1/player/<id>/landing | Works |
| Trades (who for whom, dates) | records.nhl.com/site/api/trade | Not there (404). No official feed found yet |
| Contracts and cap hits | none official | Not checked; lives on cap sites with their own terms |

## What has to be built, hardest first
1. **A value stat in wins.** Hockey has no public WAR we can republish. Build one from the league's own
   season lines: scoring and shot rates by situation, ice time as the coach's vote, a defense share from
   team goals against, goalies from saves above the league rate; scale so each season's total matches
   standings points. Test it the way Ledger WAR was tested: does last year's value predict next year's, and
   does a club's summed value track its record. This decides whether the rest is worth doing.
2. **The trade book.** With no official feed, the choices are a licensed source, a public trade history
   that allows reuse, or rebuilding trades from club-by-season changes plus news. Needs Sean's call on
   sourcing before any scraping.
3. **Contracts.** Cap hit, term, clauses, retained salary. Same sourcing question.
4. **Hockey's rules of control.** Entry-level deals, restricted free agency, a hard cap instead of a tax line,
   retained salary, no-move clauses, long-term injured reserve. The MLB surplus model does not transfer; the
   cap makes cheap good players worth more, and that has to be priced.
5. **Front office tenures.** General managers for 32 clubs since 1998-99, with dates.
6. **The page.** A copy of the MLB shell with hockey positions, a 32-club grid, and the calendar turned
   around (draft in June, free agency July 1, the deadline in March).

## Order I would work in
1. Value stat and its backtest (no outside data needed).
2. Draft channel end to end (official data exists): the first graded NHL channel, on a page nobody links to.
3. Sourcing decision for trades and contracts, then those channels.
4. Rankings and report cards, then the live season pieces.

## Decisions for Sean
- Where it lives: a section of frontofficeledger.com or its own address, and whether the name stays.
- Whether paying for a trades and contracts source is on the table.
- How far back: 1998-99 matches MLB; the 2005-06 cap era is the cleaner line for contracts.
