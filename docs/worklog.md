# Work log

Newest first. One entry per push to the live site: what changed, why, what was checked, what is still open.
Kept by Claude; every push goes through the GitHub web upload page, never a token.

## 2026-11-10 (Tue)

### Evening 5: qualifying-offer wording, NHL value stat first cut
- Deal Desk free-agent verdict: when a qualifying offer is attached it now says how many wins the forfeited
  picks account for and what the same contract grades without them (Suzuki to LAD at 4 years, $92M: F, and C
  with no pick). The fine print said "a flat 1.0 win"; the Desk actually charges the club's real forfeit
  (about 0.95 wins for most clubs, 1.5 over the tax line), so the sentence was corrected. No grade changed.
- Checked the pick'em settle date: MLB's 2027 schedule has one game on Wed March 24 and Opening Day on
  Thu March 25, so `TP_SETTLE` (March 25) stands.
- Every-view sweep, desktop and phone: no errors, no blank views.
- **NHL step 1 done as a first cut.** Pulled every skater, goalie and club season since 1998-99 from the
  league's stats service and built a wins-above-replacement stat from them. Write-up with the test numbers
  in `docs/nhl-value-v0.md`; scripts in `engine/nhl/`. Short version: believable for forwards and scoring
  defensemen, too low on defensive defensemen, noisy for goalies, and no better than last year's standings
  at predicting clubs. A test of players who changed clubs showed that club-level defense does not follow
  the player, so it was removed.
- **NHL step 2 done as a first cut: the draft channel.** Every pick 1998 to 2017 against what its slot and
  position return over the control years, by class and by general manager. Write-up in
  `docs/nhl-draft-v0.md`, script `engine/nhl/draft.py`. Two finds: the league's records site has general
  manager tenures with dates (332 stints), and the draft data carries each pick's trade trail.
- Next for the NHL: the shift-level model (fixes defensemen), then a decision from Sean on a source for
  trades and contracts.

### Evening 4: extension on the trade line, NHL plan
- A player's trade line now carries the extension that followed ("traded BOS to LAD, control years only.
  Under the LAD extension that followed: +34.7 WAR in 6 seasons so far"). Closes the last partial from the QA.
- Load size (QA S16) looked at again: `cards.js` and `moves.js` are already injected after the page parses,
  so the page works before they arrive. Left as is.
- `docs/nhl-plan.md`: what carries over, which NHL data sources were checked today (stats and draft work,
  no official trade or contract feed), what has to be built and in what order. Nothing built.
- Open: the quarter-win mid-tier bias in year one; Kirk's re-walk; one real link posted on X.

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
- NHL edition (Sean, Nov 10). Plan in `docs/nhl-plan.md`; value stat v0 and draft channel v0 are built and written up, nothing is on the site.
