# Front Office Ledger: handoff

Written Nov 10 2026 (night) so the project can be picked up from a new chat with nothing but this repo.
Companion files: `worklog.md` (what changed, newest first), `what-worked.md` (every experiment and its
result), `refresh-runbook.md` (the data chain step by step), `tests/README.md`.

## 1. What it is
frontofficeledger.com grades MLB front offices decision by decision: every trade, signing, extension, draft
pick and international signing since 1998 is set against what a typical club got from the same kind of
move, in wins, and rolled up by general manager. Around that ledger sit the live winter pieces (The Wire,
which grades this offseason's moves the day they happen, trade reports, pick'em), tools (Deal Desk,
Offseason Simulator, Scenario Room, 5-Year Horizon) and games (Who Won the Trade, Remember Some Dudes).
Owner: Sean Zerillo (@SeanZerillo, site account @FrontOfficeLdgr). Repo: `szerillo/front-office-ledger`,
served by GitHub Pages on the custom domain.

## 2. Rules that do not bend
- Never use or ask for GitHub tokens or any credentials. Ship only through GitHub's web upload page in
  Sean's own Chrome (signed in), driven by Claude in Chrome. If Chrome is asleep, wait; do not find another way.
- No em dashes anywhere (site, docs, posts). No player headshots.
- Steamer and Depth Charts projections may be compared against, never redistributed.
- Sean's standing preferences: the masthead is settled; he does not want a persistent "my club" feature;
  say "need", not "hole"; plain language, bullets over long paragraphs; no version strings or process
  notes in public copy.

## 3. Architecture
- **One page.** `index.html` holds all code and most data. Views are sections switched by a hash route
  (`#view=wire`, `#view=report&id=...`, `&player=<id>`).
- **Data that loads after the page**: `book.js` (trade book, player fates, quiz notes), `cards.js` (report
  card detail), `moves.js` (player origins and moves). The page waits for `book.js` before merging cards;
  views that need them redraw when they arrive.
- **Small JSON files beside the page**, each refreshable without touching the page: `rumors.json` (trade
  reports), `wire.json` (contract terms, qualifying-offer decisions, moves the league feed lacks),
  `share.json`, `offseasons.json`, `dudes.json`, `trade_parts.json`, `feed.xml` (RSS of the Wire).
- **Live in the browser**: the league's public transaction feed (statsapi.mlb.com), read every two minutes
  by The Wire and graded on the spot.
- **Share pages**: static pages with their own preview image so a posted link shows a card. `w/` moves,
  `s/` clubs, `o/` winters, `t/` and `h/` trades and heists, images under `og/`.
- **Counters and polls**: abacus.jasoncameron.dev, namespace `frontofficeledger` (pick'em `fa27-*`,
  `tr27-<id>-y|n`, readers' grades `wg-<move id>-<A..F>`). Analytics: GoatCounter.
- **Other**: `404.html` sends club-name paths to the club page; `manifest.webmanifest` and `icons/` for
  home-screen install.

## 4. Where things live
- **In this repo**: the live site, `engine/` (every build script, paths written as `/work/...`),
  `ingest/`, `data/` (seed files), `tests/` (12 suites plus `tests/tools/`), `docs/`.
- **Not in the repo** (they lived on the build machine and must be rebuilt on a fresh one):
  `ledger.sqlite` (runbook section 0), caches, and the NHL raw pulls (about 700 MB; every script that
  makes them is in `engine/nhl/`).
- **The working page** is `index.html` with the book inline. Rebuild it with
  `python3 engine/unsplit_book.py <repo dir> front-office-ledger-prototype.html` (checked: byte-identical
  to the page the live build was made from).

## 5. How to ship
1. Edit the working page. Run the suites four at a time (all twelve at once makes `t_wire` flake):
   `PAGE=<working page> node tests/t_qa.mjs` and the other eleven.
2. Build: `python3 engine/split_book.py <working page> <repo dir>` writes `index.html` and `book.js`.
   Run a few suites against `PAGE=<repo dir>/index.html`.
3. Upload through `https://github.com/szerillo/front-office-ledger/upload/main/<folder>` in Chrome: find
   the file input, upload (under 10 MB a call), wait until the page lists every file, press "Commit
   changes", wait until the page leaves "Processing your files". `index.html` and `book.js` go in the
   same commit whenever the book changed.
4. Verify: `git fetch` and `cmp` each file against `origin/main`; after about two minutes `curl` the live
   page and `cmp`; then `TARGET=live node tests/t_qa.mjs` and two or three others.
5. Add a dated entry to `worklog.md`, and a row to `what-worked.md` if anything was tested.

## 6. Data sources and refresh jobs
| What | Source | How it stays current |
|---|---|---|
| Transactions since 1998, drafts, rosters | MLB's public stats API; Retrosheet transactions before 2009 | Full chain (`refresh-runbook.md`), run by hand at season end and after big winters |
| This winter's moves | MLB's transaction feed, read live by the page | Nothing to do |
| Contract terms, qualifying-offer decisions | Reported terms (MLB.com, ESPN, MLB Trade Rumors, The Athletic), written to `wire.json` | Scheduled task "Ledger: contract terms and QO decisions", 1:37, 5:37, 9:37 pm ET |
| Trade reports | MLB Trade Rumors' candidates list and named reporters, in our own words, in `rumors.json` | Scheduled task "Ledger: trade reports", 12:23, 3:23, 7:23, 10:23 pm ET |
| Share pages, RSS | Built from the live site by `engine/share_live.mjs` | Scheduled task "Ledger: share pages for new moves", 1:11, 5:11, 9:11 pm ET |
| Draft X posts for Sean's phone | The live Wire | Scheduled task "Ledger: drafted posts for big moves", 1:41, 5:41, 9:41 pm ET (drafts only, never posts) |
| Site health | The live site and the league feed | Scheduled task "Front Office Ledger weekly winter check", Mondays 1:41 pm ET (report only) |
| Arbitration estimates | MLB Trade Rumors' projections as the anchor | By hand each October |
| Statcast fingerprints, park factors, defense | Baseball Savant and public defensive metrics | With the full chain |
| Contract history | The contract book (`data/`), built from public contract tables | With the full chain |

The three tasks that upload need Sean's laptop awake with Chrome signed in to GitHub. They stop in
seconds when it is not, send a one-line phone note, and the next run catches up. `rumors.json` and
`wire.json` carry a `checked` time that the page shows.

## 7. How each number is made (pointers, not the full method)
- **Ledger WAR**: the site's own wins measure with park factors, defense and a leverage adjustment
  for relievers. `docs/methodology-v15-addendum.md` and the methodology view on the site.
- **A move's value**: what the players produced for the club while it controlled them, against what a
  typical club got from the same kind of move (same contract year and size for signings, same slot for
  picks, both sides of the same deal for trades). The trade book holds every trade from every seat.
- **Letters**: a move's percentile among moves of the same type; a general manager's channel grade from
  the sum; **Overall** weights channels by how reliably each one repeats. Regimes with under two seasons
  are listed unranked (23 ranked today). Org DNA ranks all 30 clubs on each trait.
- **Projection**: three seasons weighted 5, 3, 2, pulled toward the population by sample size, times a
  playing-time model, then an aging step each year and attrition from year two. Backtested walk-forward
  2016 to 2026. Recent changes: pitcher attrition penalty halved; a quarter win added for hitters 30 and
  under in the 2.75 to 4.0 band. `engine/desk_data.py`, `engine/y1_bt.py`, `engine/aging_bt.py`.
- **Trade value at the Deal Desk**: projected wins minus salary charged at what a win costs on the market
  (1.45 times for hitters, 1.53 for pitchers), Ohtani at present value, a star never below one season of
  his production. Cornerstones are off the table unless reported as available. The other club says yes
  when it gets at least 95% of its asking price or is within 0.3 wins. Club posture (contender, bubble,
  fringe, rebuilding) comes from last year's wins and the 2027 projection.
- **Free-agent grade**: the contract against the Ledger's fair value for the same years at what clubs
  have actually paid per win produced, minus the draft picks a qualifying offer costs that club.
- **Assistant GM**: the same functions, used to complete or advise a deal; one acceptance test shared by
  the note and the verdict.

## 8. State on Nov 10 2026
- Live and passing all 12 suites. Kirk's launch QA (3 blockers, 16 should-fix) is fixed and was
  re-walked on the live site: `docs/qa-rewalk-nov10.md`.
- First download 1,044 KB over the wire after the book split; measured before the split at 3.7 s to
  home content on 4G and 9.4 s on slow 4G. Not re-timed since.
- The refresh tasks were re-timed tonight; their first runs on the new schedule have not been observed.

## 9. Open items
- One real link posted on X to confirm the preview card (only Sean can).
- Sean's earlier formatting notes were lost with the old chat; a re-list is needed.
- Old task-list items from earlier chats have not been reconciled against the live site.
- Player names and the Desk's player table still ride in the first download (about 8% and 35% of it).
- `TP_SETTLE` assumes Opening Day on March 25 2027 (confirmed against MLB's schedule).
- After Nov 17: qualifying-offer decisions close; the terms task marks unaccepted offers as declined.
- Season rollover steps are in the runbook, section 1.

## 10. NHL edition (not on the site)
Plan `nhl-plan.md`. Built: a wins stat (`nhl-value-v0.md`, `nhl-value-v1.md`), a draft channel
(`nhl-draft-v0.md`), general manager tenures from the league's records site, and a trade history parsed
from Wikipedia's season pages (six of 21 seasons pulled; the site rate-limits). Honest limits: defensemen
are 14% of the wins in every version, goalies are mostly noise season to season. Next: finish the trade
pull, value both sides of every trade, attribute to general managers, then contracts (no source yet).
To rebuild the NHL data from nothing, in `engine/nhl/`: `fetch.py`, `assemble.py`, `value.py`,
`pbp_fetch.py 2010 2025`, `shots.py`, `xg.py`, `stints.py`, `rapm.py 50`, `write_v1.py`, `draft.py`,
`trades_wiki.py` (the draft and general-manager files come from `records.nhl.com/site/api/draft` and
`/general-manager-franchise-records`, saved under `draft/`).

## 11. Things that only existed in the chat
- The page helper used to commit an upload once the files are listed:
  `document.querySelector('button.js-blob-submit')`, pressed only when the count of
  `.js-manifest-file-entry` rows with a name equals the number of files sent.
- A big upload can lose its reply over the Chrome link and still land. Check `git fetch` before repeating.
- A full rebuild of `desk_data.json` drifts from the live page in three side tables; change the page's
  data surgically (`engine/apply_y1.mjs` is the pattern) until the chain is reconciled.
- `desk_data.py` charges a qualifying-offer signing by club type; report cards use a flat 1.0 win.
- The ideas list ("Shipped Nov 10 2026" and what is still unbuilt) is a Claude Doc in Sean's account.
- Kirk is Sean's other assistant; he drafts X posts and ran the launch QA. Share pages and drafted posts
  from this project feed his posting.

## 12. Scheduled tasks and chats that belong to this project
Recurring, all needed while the winter is live:
1. Ledger: trade reports
2. Ledger: contract terms and QO decisions
3. Ledger: share pages for new moves
4. Ledger: drafted posts for big moves
5. Front Office Ledger weekly winter check

None of them depends on the build chat: each run starts on its own. So:
- **The chats those runs open** ("Ledger: ..." with a date) can be closed once read. They hold nothing
  that is not in the repo or the phone note.
- **Candidates to switch off, Sean's call**: number 5, whose job is now covered by the daily tasks and
  the live feed; number 4, if Kirk is drafting the posts himself.
- One-off reminders created during the build ("Continue ...") end by themselves after firing.
- The build chat itself can be closed after this file is in the repo; start the next one by pointing it
  at this file.

## 13. Decisions waiting on Sean
1. NHL trade and contract source: Wikipedia's pages are the working source for trades; contracts have none.
2. Where the NHL edition lives (a section of this site or its own address) and how far back it goes.
3. Re-list of the earlier formatting notes.
4. Whether to switch off tasks 4 and 5 above.
5. Whether the laptop stays awake at the task times, or misses are acceptable.
