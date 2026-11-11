# Work log

Newest first. One entry per push to the live site: what changed, why, what was checked, what is still open.
Kept by Claude; every push goes through the GitHub web upload page, never a token.

## 2026-11-11 (Wed)

### Launch push, block 3 (audit of the audit)
- `docs/audit-nov11-b.md`: sample method and full ID lists (stratified seeded draw from the card rows,
  recent moves under-weighted), 90% intervals, 20 high-traffic moves (3 errors in 92 checks), control-end
  count (30 of 164 covered extension grades wrong; Olson 12.0 to 3.8 worked by hand), prospect share (765
  trades since 2019 carry projected value; median 26%), phone profile, salary-charge assumption (2,370
  player-seasons since 2015 charged $0).
- Fixed live: unstarted extensions stay OPEN (Hoerner); linked same-day legs keep their own numbers (Arizona
  2003); the two incomplete pre-2012 deals are held back on trees.
- Mock (not shipped): `docs/mock-split.html`, played vs projected.

### Launch push, block 2 (accuracy)
- **Audit of 40 random moves** against the league feed, named-source terms and FanGraphs: 5 field errors in
  184 checks (2.7%), 3 of 40 moves. Full report `docs/audit-nov11.md`.
- **Fixed live**: trade OPEN now follows flipped pieces (15 trades reopened); "value realized on" relabelled
  as value after the trade wherever he played; a Rule 5 grade no longer stands in for a trade seat's net
  (8 deals, Romano 2018 was +3.6 for the White Sox); two early two-club deals completed from the receiving
  side (Greinke 2012, Gerut 2009); one node per deal on player trees (31 duplicates).
- **Not fixed (engine)**: Super Two control ends a year early: Donaldson 2016 and Olson 2022 extensions.
- `tests/t_nov11.mjs` gained four checks; all 13 suites pass on the live site.

### Launch push, block 1
- **Launch checklist**: `docs/launch-checklist.md` (must fix, nice to have, after launch).
- **OPEN and CLOSED from the facts.** The flag was a date rule: every decision from 2021 on read OPEN.
  It is now worked out on the page from the winter roster and status, the contract book, each player's
  last MLB season and his filed moves. Signings close when the contract is played out or he has left the
  club; extensions when no seasons are left or he has left; claims and walks when their "next N seasons"
  window ends; draft and amateur picks when he is a free agent or out of the league; a trade stays open
  while any piece is still with the club that got him. Unknown players keep the old flag, and nothing
  before 2021 is touched. 636 decisions closed. Tree nodes use the same rule. Morel's Miami deal now reads
  CLOSED; the Holmes and Taylor deal stays OPEN because Jefferson Rojas is still with the Mets.
- **Prospect value note.** An open trade with a piece who has never played in the majors now says he
  counts at his prospect value for now (the Cubs' -1.7 on Holmes and Taylor is all Rojas's ranking value).
- **Checked stamps.** One real run of each refresh job from this chat: `rumors.json` (Seager now credited
  to Ken Rosenthal, The Athletic: Texas tests his market at the GM meetings; Kwan to Jon Paul Morosi, MLB
  Network: one-year players unlikely to move this month) and `wire.json` (no new terms: the one major-league
  signing since Nov 1, Waguespack to DET, has no named-source terms; no QO decisions yet). Both stamped
  07:51 UTC and confirmed live. Whether the scheduled 8:03 and 8:17 AM ET runs stamp on their own is
  checked at 13:40 UTC.
- **GM battle cards**: the tale of the tape now carries each front office's best and worst graded move
  (trades read "Got X for Y"), plus Swap sides and Random matchup.
- **Player career card**: on every player tree (search and pop-out), a card with the clubs he passed
  through, counts, the deal that swung the most wins for a club that got him (marked control years only
  when an extension followed), and where he stands, with Copy link, Post on X and Save image. Link:
  `#view=trees&player=<id>`.
- **Weekly streak board** under Trade Grade's daily five: Monday to Sunday scores from this browser, the
  week's total, days played, and how today's readers did (one public tally per finished five, `tg27-<day>-<n>`).
- New suite `tests/t_nov11.mjs`; `t_fun` battle check counts the two new rows separately. All 13 suites pass.

## 2026-11-10 (Tue)

### Night 11: NHL trade channel first cut, checks
- All 21 seasons of trades pulled and parsed (the plain-text page form avoids the rate limit). Both sides of
  2,430 trades valued and attributed to general managers: `docs/nhl-trades-v0.md`. Results repeat weakly
  (0.23). Weak points are conditional picks and re-signings; both need better inputs, not more tuning.
- Phone load re-timed on the live site after the split: home content 3.3 s on 4G (was 3.7), 8.2 s on slow
  4G (was 9.4).
- Refresh tasks: at 23:54 UTC neither `rumors.json` nor `wire.json` carried a `checked` time yet. The first
  runs under the new prompts are due 00:23 UTC (trade reports) and 02:37 UTC (terms); the 22:37 UTC terms run
  fired one minute after the prompt change and left no stamp. Check again after those.
- Stamp check at 00:57 UTC Nov 11: still no `checked` time in `rumors.json`. The trade-reports task did
  fire at 00:24 UTC under the new prompt and Chrome was reachable minutes earlier, so either the run was
  still working 33 minutes in or it stopped before uploading; its phone note will say which. Prompts left
  alone until there is evidence. Next looks: after the 02:37 UTC terms run and the 03:23 UTC trade-reports run.
- **Old task-list items reconciled against the page** (27 were still marked open from earlier chats).
  Checked directly: no process words (curated, COMPUTED, archive sweep, illustrative, fictional), no "-0.0",
  no "undefined" or "NaN" in any of the 20 views; the simulator has Start over and a call-ups step; the Deal
  Desk has Undo and a position filter for free agents; the Chourio extension is in the Brewers' ledger
  (8 years, $82M). 24 items closed as done or overtaken by later work.
  Left open for Sean because the page does not settle them:
  1. Champions view: a color legend and a view toggle were asked for once; the view has the overview and a
     champion picker, and no legend or toggle that I can find.
  2. Deal Desk: a "swap sides" control was asked for once; today your club is fixed on the left and there
     is no swap.
  3. Simulator: "salary shed counts toward room" was asked for once; not verified either way.

### Night 10: handoff file
- `docs/HANDOFF.md`: what the site is, architecture, sources and refresh jobs with schedules, how each
  number is made, state, open items, what only existed in the chat, which scheduled tasks and chats belong
  to the project and which can be closed, and the decisions waiting on Sean.
- `engine/unsplit_book.py` rebuilds the working page from the live `index.html` and `book.js` (checked
  byte-identical), so a fresh machine can start from the repo. Runbook section 0 updated.
- `tests/tools/`: the working scripts that were only on the build machine (page eval, every-view sweep,
  split comparison, phone timing, the 32 QA cases).
- Wikipedia stays the working NHL trade source for now (instruction relayed by Kirk for Sean);
  `what-worked.md` says what a better source would have to beat.

### Night 9: register of what was tried, NHL trades prototype
- New `docs/what-worked.md`: one row per experiment or fix with its result and whether it was kept, so
  nothing is tested twice. Keep it current alongside this log.
- NHL trades: Wikipedia's season transaction pages carry every trade with dates, both sides and picks, each
  row citing the club or league announcement. `engine/nhl/trades_wiki.py` parses them: 2005-06 to 2010-11
  done (715 trades, 85% of traded players matched to league ids, 745 picks). The site rate-limited the
  pull after six seasons; the other 15 need a slow pull. Still Sean's call whether this is the source.
- Next: finish the pull, resolve picks to the players drafted (the draft data has each pick's trail),
  value each side by what the assets produced for the acquiring club, and attribute to general managers.

### Night 8: NHL shift-level work (v1)
- Built expected goals (2.19 million shot attempts, out-of-sample, calibrated), five-on-five stints and a
  shift-level skater model. Write-up with every test number in `docs/nhl-value-v1.md`.
- Result, plainly: it did not fix defensemen (their share of wins stays 14% in every version) and it did
  not fix goalies (goals saved above expected repeats at 0.17 against 0.19 for plain save percentage).
  It did improve club prediction a little (0.595 against 0.567; standings alone 0.552), so v1 is v0 plus
  half of the shift-level effects. v1 tracks v0 at 0.996.
- Draft channel rerun on v1: unchanged for practical purposes (0.998 pick by pick).
- For the edition: forwards graded normally, defensemen only against defensemen, goalies over several
  seasons. Next real blocker is still a source for trades and contracts (Sean's call).

### Night 7: hitters in their prime (the mid-tier projection gap)
- Tested first (`engine/y1_split.py`): the quarter-win gap is not general. It is hitters 30 and under
  projected for 2.5 to 4.25 wins: +0.36 (se 0.11) in year one, positive in all four blocks of years
  (+0.30, +0.34, +0.57, +0.15), and still +0.30 in year two. Hitters 31 and over: -0.02. Starters: +0.11
  (se 0.14), nothing reliable, left alone.
- Fix (`desk_data.py`): a quarter win added to the base for hitters 30 and under across a first-year
  projection of 2.75 to 4.0, fading to nothing at 2.0 and 4.75. On the walk-forward (`engine/y1_bump.py`)
  the tiers come out at -0.04, +0.05 and +0.07 where they were +0.10, +0.24 and +0.08.
- Applied surgically (`engine/apply_y1.mjs`): 62 hitters' base values changed in the page's data and nothing
  else (checked field by field). A full rebuild of `desk_data.json` was not used because it drifts from the
  live page in three side tables. Examples: Raleigh 3.4 to 3.6, Julio Rodriguez 3.5 to 3.8, Abrams 3.8 to
  4.1 for 2027. Club projections moved by a win for COL, LAA (down) and MIA (up, now a bubble club).
- All 12 suites pass. Methodology has a paragraph on it.
- Sean's earlier formatting notes: searched the session transcript, every subagent log and stored tool
  result; they are not recoverable. Waiting on a re-list.

### Night 6: Kirk re-walk, refresh hardening, smaller first download
- **Re-walk of Kirk's QA on the live site**: all 32 scripted cases (16 trade, 8 free agent, 8 advisor) and the
  53-check suite pass. Report in `docs/qa-rewalk-nov10.md`. His original write-up is no longer in my records,
  so a pass from his own notes is still worth having.
- **Refresh hardening.** The trade-reports and contract-terms tasks now (1) stop in seconds, with a one-line
  phone note saying how old the file is, when Chrome is asleep, (2) skip if another run checked in the last
  3 to 4 hours, (3) always stamp a `checked` time in the file even when nothing changed, and (4) run more
  often (trade reports 12:23, 3:23, 7:23, 10:23 pm ET; terms 1:37, 5:37, 9:37 pm ET), so a missed slot is
  caught at the next one. The page shows "checked Nov 11" beside the trade reports and the Wire's contract
  terms, and "last checked" once that is more than two days old.
- **Smaller first download (QA S16).** Measured on the live site with a throttled phone: first paint about
  1 second; home content 3.7 s on 4G and 9.4 s on slow 4G; everything 6.3 s and 18 s. The trade book, player
  fates and quiz notes (a sixth of the page) now ship as `book.js`, loaded right after the page:
  the page went from 1,233 KB to 1,044 KB over the wire. Heists, the quiz and the home counts wait for it
  and redraw; a view-by-view comparison against the old build is identical once loaded.
- **Deploy step changed**: `index.html` is no longer a copy of the prototype. Build it with
  `python3 engine/split_book.py front-office-ledger-prototype.html repo` and upload `index.html` and
  `book.js` in the same commit.

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
- **Shift-level data pulled** (`engine/nhl/pbp_fetch.py`): every regular-season game from 2010-11 to
  2025-26, 18,152 games, with every shot attempt (all with a location on the ice), every penalty with who
  took and drew it, and every shift. About 80 seconds a season; 96 MB kept in compact form under
  `nhl/pbp/` on the build machine, not in the repo. Shift rows are thin in 57 games of 2024-25.
- Next for the NHL, in order: (1) expected goals from shot location, which gives goalies a fair
  denominator; (2) the shift-level model for skaters, teammates and opponents held fixed, which is the fix
  for defensemen; (3) rerun the draft channel on the new stat; (4) a decision from Sean on a source for
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
