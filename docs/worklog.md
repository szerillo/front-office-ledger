# Work log

Newest first. One entry per push to the live site: what changed, why, what was checked, what is still open.
Kept by Claude; every push goes through the GitHub web upload page, never a token.

## 2026-11-10 (Tue)

### Evening 3: heist previews, the year-one check
- Uploaded the 64 rebuilt heist share pages and images. Big trades are now named for the best-known player on
  each side with the rest counted ("Marlins got Yunel Escobar and 6 others from the Blue Jays for Mark Buehrle
  and 4 others"), matching the cards on the site. The other 52 previews were unchanged.
- Year-one projections for stars: tested, not changed. `engine/y1_bt.py` runs the page's own rule walk-forward
  on 2016-2026. Starters coming off an ace season (5.5+ wins per full season, n 15): projected 3.6, actual 3.4.
  Hitters coming off a star season (6+, n 92): 5.4 vs 5.0. One real bias: the tier just under the stars comes
  in about a quarter of a win low (starters off a 4.5+ season, n 73: 3.1 vs 3.4; hitters projected 3-4, n 281:
  3.5 vs 3.7). Left alone before launch: fixing it reopens the playing-time rules fit on Nov 9.
- Methodology page: one paragraph on why an ace projects around four wins.
- Open: extension's number on the trade line of a player page; phone load size; the quarter-win mid-tier bias.

### Evening 2: aging curve, stays calls, beta labels, club cards
- Aging backtest (`engine/aging_bt.py`, `aging_fit.py`, `aging_fit2.py`): every regular and star since 1990,
  six seasons forward. Hitters: for 2010-19 cohorts projected totals land within 3% of actual, stars included;
  no change. Pitchers were aged too fast (2010-14 and 2015-19 cohorts 12% and 9% under); the extra yearly
  pitcher attrition went from 6 points to 3 (now 6% and 3% under).
- "Stays" calls in trade pick'em settle on Opening Day (constant `TP_SETTLE`, assumed 2027-03-25).
- Beta labels on the Deal Desk and the Offseason Simulator.
- All 30 club share cards rebuilt: "#N of the 23 ranked front offices".

### Evening 1: rankings, Org DNA, home order
- Org DNA ranks all 30 clubs; front offices under two seasons sit at the league middle.
- Rankings: one line under each name, no "seasons in the seat" under the bar, a plain sentence on what the
  +/- under Overall means, regimes under two seasons listed below a divider and not ranked (23 ranked).
- Home Play card order: Deal Desk, Offseason Simulator, Scenario of the day, Pick'em, Trade Grade, Remember
  Some Dudes. Tree of the day walks down to where the tree branches (the Ortiz chain). Champion of the week
  anchored to the 2026 Brewers.
- Player pages have their own link; search finds near-miss spellings; report card tiles three and three;
  channel bars green or red by sign; phone Deal Desk rosters start folded.

### Afternoon: launch-day QA (Kirk's report)
- B1: salary charged at what a win costs on the market (1.45x hitters, 1.53x pitchers), Ohtani at present
  value, a star's trade value never below one season of his production. Cornerstones are off the table unless
  in trade reports.
- B2: "Make it fair" starts a rebuilding club from a sale, never pays with a cornerstone or a non-contender's
  young regulars, does not sweeten a salary dump, undoes a fill that cannot reach the price, never blank.
- B3: one acceptance test for the note and the verdict; a free-agent deal graded against the board's fair
  value on one projection; qualifying-offer advice follows the player's market; one posture function.
- S1-S15 fixed (S5 partly). Regression suite `tests/t_qa.mjs`.

### Overnight and morning
- Trade pick'em with price and best fits; trade reports in `rumors.json` with a twice-daily scheduled task;
  one daily streak; tale of the tape; readers' grades; RSS feed; home-screen install; 404 page.

## Standing rules
- No GitHub tokens or credentials. Uploads only through the web upload page in Sean's Chrome.
- No em dashes. No player headshots. Steamer and Depth Charts projections are not redistributed.

## Next
- NHL edition after MLB is settled (Sean, Nov 10). Not started; see the plan entry when it is written.
