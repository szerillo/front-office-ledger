# The Front Office Ledger
## Design Document — A Public Site That Grades Real Front Offices the Way OOTP Grades You

*Prepared for Sean Zerillo · July 2026 · v1.0*

---

## 1. The Idea in One Paragraph

Out of the Park Baseball shows every manager a "Decision History" screen: every trade, draft pick, signing, and waiver claim they ever made, with the realized WAR gained or lost attached to each one. Nothing like that exists for real front offices. Fans argue about whether Jerry Dipoto is good at his job with anecdotes; beat writers score trades the day they happen and never revisit them. The Front Office Ledger is a public website that maintains a complete, continuously-updated ledger of every MLB roster decision, attributes the realized value of each decision to the executive regime that made it, and rolls those decisions up into transparent report cards and leaderboards for every front office in baseball. It is Baseball-Reference for the people who build the rosters instead of the people on them.

The core insight that makes this buildable: a front office's output is almost entirely observable. Every acquisition and departure is a public transaction with a date. Every player's subsequent production is public. The hard part is not the data on players — it's the *attribution layer* (which regime gets credit, measured against what baseline) and the *personnel layer* (who actually ran baseball ops on each date). Those two layers are the product's moat, because nobody maintains them publicly.

---

## 2. Product Vision & Positioning

**Audience.** Three overlapping groups: (1) analytically-minded fans who already read FanGraphs — the people who argue about trades on the internet and want receipts; (2) media and content creators who need a citable, neutral reference ("per Front Office Ledger, the Braves have added +41 WAR via trade under Alex Anthopoulos, 2nd in MLB"); (3) bettors and futures traders, for whom front-office quality is a real but unquantified input into long-horizon team projections.

**The headline artifact** is the **Front Office Leaderboard**: all 30 current regimes ranked by a composite rating, decomposable into the four acquisition channels — Draft, Trades, Free Agency, and Waivers/Minor Moves. Beneath it sit four core page types:

**Regime Report Card** — one page per executive tenure (e.g., "Mike Elias, Baltimore, Nov 2018–present"). Mirrors the OOTP screen: best and worst trades by WAR, best acquisitions, greatest losses, draft class grades, FA signing ROI, with every line item linking to a decision page. A regime, not a team-season, is the unit — this is what lets an executive carry a career record across jobs (Dombrowski's ledger spans Montreal, Florida, Detroit, Boston, Philadelphia).

**Decision Page** — the atomic unit. One page per transaction: the full package both ways, what each side gave up and received, value realized to date, value projected remaining, contract dollars exchanged, and a "how it looked at the time" snapshot (consensus prospect ranks, projection-system forecasts as of the transaction date). The at-the-time snapshot is what separates this from cheap hindsight rankings — it lets you distinguish *bad process* from *bad luck*.

**Player Provenance Page** — the inverse view: for any player, the chain of decisions that moved him. Who drafted him, who traded for him, who let him walk, and how much value each front office captured from his career. This is the foundation for the later scout/player-dev layer.

**Transaction Tree View** — assets compound across decisions (a fourth-round pick becomes a rental ace becomes a comp pick becomes a new draftee), and the tree view follows each chain generation by generation. Every branch carries an OPEN/CLOSED status — closed means the window is finished and the number is final; open means value is still accruing and the verdict can move — with captured value and outflows visually distinct. Trees are also the honest display for sell-offs, which are a dozen open branches rather than a gradeable verdict, and they pair with the **lens stack** on every decision page: windows-only, option-inclusive, and counterfactual readings (raw and leverage-adjusted where they differ) shown side by side with per-lens status, never averaged into a single number — the disagreement between lenses is the analysis.

**Executive Career Page** — cross-regime career totals for every GM/POBO, plus (in later phases) assistant GMs, scouting directors, and farm directors, enabling "coaching tree"-style lineage: which front offices train executives who go on to succeed elsewhere.

**Positioning.** Free, public, methodology fully documented — that's what makes it citable and defensible. Monetization (later): premium tier with alerting/exports/API, sponsorship, and eventually the same framework applied B2B. Comparable trajectory: Spotrac and FanGraphs' RosterResource both started as one obsessive person maintaining a structured dataset nobody else would.

---

## 3. Methodology: Turning Transactions into Grades

This is the intellectual core. The guiding principles: (a) every number must be reproducible from the methodology page; (b) separate *realized outcome* from *at-the-time process* and show both; (c) never hide judgment calls — publish the attribution rules.

### 3.1 The unit of account: the Decision

A **Decision** is a dated transaction event attributed to a **Regime** (an executive-team-tenure triple). Each decision has one of the channel types — draft selection, trade, FA signing (major/minor league), waiver claim, Rule 5 pick, international amateur signing, contract extension, non-tender/release, and the *passive* decisions: letting a free agent walk, losing a player on waivers. Passive losses matter — the OOTP "Greatest Losses" panel is half the story, and it's the half fans forget.

### 3.2 The value currency: WAR captured, and surplus dollars

For each player-side of each decision, the system computes:

**WAR captured** — WAR the player produced *for the acquiring team during the club-control window acquired in that decision*. A player acquired at the deadline as a rental is measured over two months plus playoffs; a drafted player over his entire pre-free-agency run. Departures are symmetric: WAR the departed player produced elsewhere during the control window given up.

**Surplus value ($)** — WAR captured × market $/WAR (year-specific), minus actual salary paid. This is what lets FA signings and extensions be graded fairly: a 3-WAR season on a $30M salary is roughly break-even, not a win. For trades and drafts, surplus value is the more honest currency than raw WAR; the site shows both.

**Net decision value** — acquired-side value minus departed-side value, minus cash considerations. Every decision nets to a single number, exactly like OOTP's "gained 10.9 WAR in the deal."

### 3.3 Baselines: grading against expectation, not against zero

Raw realized WAR overrates teams that pick at the top of the draft and underrates good decisions that were merely expensive. Every channel gets an expectation baseline:

**Draft:** historical expected career-WAR-in-control-years by pick number (a smooth curve fit on ~40 years of draft outcomes — pick 1 overall carries a very different expectation than pick 38). A team's draft grade is realized WAR minus slot expectation, summed over picks. This also handles the tanking objection: Baltimore drafting well at 1-1 clears a high bar, not a low one.

**Trades (prospect side):** prospects exchanged are valued at acquisition using published prospect-value curves (surplus value by prospect tier — the FanGraphs/Point of Pittsburgh research lineage: an FV60 prospect carries ~$40–55M expected surplus). The *ex-ante* ledger scores the deal on values at the time; the *ex-post* ledger scores realized outcomes. Both are shown; the gap between them is the "luck vs. skill" diagnostic.

**Free agency:** expected WAR from the contract's market price (dollars ÷ market $/WAR) versus realized. FA grading is therefore ROI, not raw production — signing Aaron Judge and getting Aaron Judge is a pass, not an A+. This is also the universal *display* rule: anywhere a contract exists (FA signings, extensions), the number shown is value net of cost, never raw WAR accumulation; only the zero-baseline channels (waivers, minor-league deals, Rule 5) display raw captured value, because there the cost genuinely rounds to nothing.

**Waivers/minor-league deals/Rule 5:** baseline ≈ 0, so this channel is pure found money and a clean read on pro scouting. (In the OOTP screenshot this is where "Scout Discovery" lives.)

### 3.4 Attribution rules (the judgment calls, published)

**Regime windows.** A decision belongs to the regime in office on the transaction date. Interim GMs get flagged tenures. Where a POBO/GM pair coexists (Friedman/Gomes, Dombrowski/Fuld), credit attaches to the *front office regime* — the named top decision-maker — with co-executives listed; trying to split credit between a POBO and his GM from public data is false precision.

**Inherited value is excluded.** A regime is graded only on its own decisions. The 2020 Dodgers' championship core doesn't credit Friedman for Kershaw (inherited) but does for Betts (trade) and Muncy (minor-league signing).

**Extensions are decisions.** Extending a pre-arb player is a new decision graded on surplus vs. the market alternative; so is a non-tender or a decision to trade a player one year before free agency vs. letting him walk.

**Time decay and open positions.** Recent decisions are largely unrealized. Every decision carries realized-to-date plus a projected-remaining component (from public projection systems) that decays to zero as the control window closes. Leaderboards default to *realized only*, with a toggle for realized+projected; regimes under ~3 years get an explicit "small sample" badge rather than silent inclusion.

**Playoff value.** Postseason WAR is scarce and championship-leveraged. V1: include postseason performance at a fixed multiplier and show championships won on the regime card without mixing them into the rating. Fancier championship-probability-added accounting is a documented future upgrade.

**Retention rights and opportunity cost.** A trade transfers a third asset beyond the control windows: the exclusive right to extend the player. Pricing it at zero produces indefensible verdicts (the windows-only ledger says Boston "won" the Betts trade). Every trade therefore carries three ledgers: (A) windows-only; (B) option-inclusive — realized extension surplus flows to the acquirer's side once the option is exercised; (C) the seller's counterfactual — charged p(retain) × haircut × forfeited extension surplus, where p is a per-case, documented, versioned judgment drawn from negotiation reporting, exposed as a slider so readers can test the verdict against their own prior. The same machinery scores passive retention failures (letting a star walk = p-weighted forfeited surplus, comp pick credited), making "traded him with 2.5 years left" and "let him leave for nothing" directly comparable decisions. Deals stop being zero-sum under this accounting — both sides can beat their alternatives — which is the honest and more interesting answer.

### 3.4b The v0.3 target: market-price baselines unify the channels

The methodology's layers (leverage curves, discounting, retention options, the lens stack) exist because trades currently grade against "value in = value out," which is not a market baseline. The endgame is one principle everywhere: every decision graded against the market price of that transaction type at that moment. Draft picks already have it (slot curves), FA already has it (contract price), waivers trivially (zero). The missing piece is an **empirical trade-return baseline**: regress prospect value surrendered against quality and control-window acquired across every trade since ~2005 (the pipeline can enumerate the corpus automatically), segmented by asset type: pure rental, one-plus-one, multi-year control, salary dump. That yields the going rate per projected rental WAR by era. Once it exists, the leverage curve and discount rate stop being grading inputs (the market's observed prices already contain the win-now premium) and become diagnostics, retention rights fold into the asset definition, and the lens stack collapses to two defaults: **paid vs. market at the time** (process, closable on day one) and **realized vs. paid** (outcome, open until windows close), with the full stack available behind a click. Prerequisite: the historical prospect-valuation archive (at-the-time top-100s and FV-tier surplus curves), which is also moat #2, so the work compounds.

### 3.5 The composite: Front Office Rating (FOR)

Per regime, per channel: **value added vs. expectation, per season of tenure**, expressed as both dollars and a 20–80 scouting-scale grade (on-brand for baseball and instantly legible). The composite FOR is the tenure-length-weighted sum across channels, deliberately *not* reweighted by opportunity — a team that never spends in FA simply has few FA decisions, and per-season normalization handles volume. Every rating is clickable down to the individual decisions that produced it. No black boxes: the entire pipeline from transaction to grade is documented on a public methodology page.

### 3.5b Prospect development credit and farm system rankings

Prospects are assets with observable market prices before they ever play an MLB game: top-100 ranks and FV grades map to published surplus-value curves. That makes development creditable independently of MLB outcomes, which fixes a real unfairness in window-based accounting: a GM who turns a 4th-rounder into a consensus top-100 prospect has manufactured tens of millions in asset value even if he trades the player before debut. The accounting is a **mark-to-market value chain per asset**: acquisition (credited at cost vs. the acquisition channel's baseline: slot price, int'l bonus, trade valuation), **development (the appreciation: asset value at exit minus asset value at entry, credited to the org that held the player while the marks moved)**, and deployment (MLB windows and trade returns, graded vs. the asset's value at graduation or exit, not vs. zero). Each stage credits the regime that held the asset during that stage, so Elias gets the Stowers-and-Norby manufacture even though Miami got the Stowers outcome, and no value is double-counted: what you spend in a trade is the marked value you built. Marks come from the historical prospect-rank archive (BA/BP/FanGraphs/Pipeline top-100s and FV grades, quarterly-to-annual granularity), which is the same dataset the v0.3 market baselines need; one curation effort feeds both.

The org-level rollup is a product surface of its own: **farm system rankings as a time series with flows**. A system's value at time T is the sum of its prospects' marked values; the time series decomposes into draft-in, international-in, trade-in, development appreciation (the skill number), graduation-out, and trade-out. Existing farm rankings publish the level; the Ledger publishes the *flows*, which is where front-office skill actually lives: two systems ranked 10th are very different if one got there by drafting and developing and the other by hoarding trade returns. Transaction tree nodes carry the marks too, so a tree shows not just who was traded but how much value the holding org added before spending it.

### 3.6 The later layer: scouts, player development, coaches

Designed-for but deferred (Phase 4). The data model already stores the *provenance chain* per player (drafted-by, signed-by, developed-at levels X–Y under farm director Z, breakout under hitting coach W). Two tractable public-data approaches when we get there: (1) **org-level player-dev deltas** — realized outcomes vs. prospect-tier expectations, aggregated by organization and era: which orgs systematically beat their prospects' expected outcomes (the "pitching factory" effect, quantified); (2) **personnel-linked attribution** where public reporting names the responsible person (scouting directors for draft classes are always public; area scouts sometimes; coaches increasingly, via reporting on swing changes and pitch-design work). Individual-scout attribution below the scouting-director level will always be partly journalistic — that's a content opportunity, not a blocker.

---

## 4. The Dataset: What "World of Baseball" Actually Requires

Seven entity groups. The good news: five are solved public problems. The two that aren't (bold below) are the moat.

| # | Dataset | Best source(s) | Status |
|---|---------|----------------|--------|
| 1 | Player identity spine | Chadwick Bureau Register (open, cross-references MLBAM/BRef/FG/Retrosheet IDs) | Solved, free |
| 2 | Transactions | MLB Stats API `transactions` endpoint (current + deep history); Retrosheet transaction DB (1870s–2020, no longer maintained); ProSportsTransactions archive; FanGraphs RosterResource for verification | Solved-ish; needs merging + entity resolution |
| 3 | Performance / WAR | BRef WAR & FanGraphs WAR (⚠ licensing — see below); fallback: compute an open WAR in-house from Retrosheet/Statcast (openWAR lineage) | Available; licensing is the key strategic decision |
| 4 | Draft history | MLB Stats API draft endpoints (picks, slot, signing status, bonus) + BRef draft pages for older years | Solved, free |
| 5 | Contracts & salaries | Cot's Contracts (Baseball Prospectus), Spotrac (⚠ both proprietary); arb/pre-arb salaries partially in news archives; Lahman salary tables for history | Hardest licensing problem after WAR |
| 6 | **Front office personnel & regime dates** | No dataset exists. Wikipedia GM lists + team press releases + transaction-log announcements. Must be hand-curated (~30 teams × ~3–5 regimes over 25 years ≈ a few hundred rows — tractable) | **Build it — moat #1** |
| 7 | **At-the-time context** (prospect ranks, projections, market $/WAR by year) | Historical BA/BP/FG/Pipeline top-100s; published $/WAR research; archived projections | **Assemble it — moat #2** |

### 4.1 Sourcing notes and the licensing reality

**Transactions.** The MLB Stats API (statsapi.mlb.com) is free and includes a transactions endpoint with team/date filtering, plus draft and prospect endpoints — this is the primary live feed. It's technically unofficial/undocumented (community wrappers like toddrob99's MLB-StatsAPI and pybaseball cover it well) and MLBAM's copyright notice governs it; interpretation-of-facts sites built on it have operated for years, but this deserves a real ToS review before commercialization. Retrosheet's transaction database (open license, requires attribution) is the historical backbone but was last updated 2021 — the gap from ~2020 to present gets filled from the Stats API and ProSportsTransactions.

**WAR licensing is the single biggest strategic decision.** Sports Reference and FanGraphs both prohibit bulk scraping for a commercial product; both sell/negotiate data licenses. Three viable paths, in order of preference: (1) *license FanGraphs data* — they have a data-feed business and a media-friendly posture; a citable partnership also lends credibility; (2) *compute our own* — an open, documented WAR built from Retrosheet event data + Statcast (both free); openWAR (Baumer/Jensen/Matthews) is a published, reproducible starting point; more work, but it makes the whole stack self-owned and is itself a marketing asset ("Ledger WAR"); (3) *hybrid* — own WAR as the spine, licensed WAR shown as a cross-check. Recommendation: start development against freely-computable value metrics so nothing blocks, and pursue the FanGraphs conversation in parallel.

**Contracts.** Needed for surplus value. Cot's is the community standard and BP has historically been permissive about derived use with attribution — worth a direct conversation. V1 can ship with a coarser model (league-minimum during pre-arb, modeled arb awards, publicly-reported FA terms from news archives) that captures 90% of surplus-value signal, because the biggest dollar figures (FA contracts, extensions) are always publicly reported.

**Front-office regimes.** The genuinely new dataset. Schema: person, team, title, start date, end date, reporting line, source citation. Seed from Wikipedia's list of MLB GMs and team-by-team executive histories, then verify against press releases. A weekend of focused curation gets the 2000–present era; maintaining it takes minutes per month. This table is small, but everything hangs off it, and *nobody else has it clean*.

### 4.2 Entity resolution — the unglamorous 30%

Transactions name players inconsistently across sources and eras; trades involve PTBNLs and cash that resolve weeks later; draft picks don't sign; international signees lack IDs until affiliation. The pipeline needs a resolution layer that joins everything to Chadwick IDs, links PTBNL resolutions back to the parent deal, and flags unresolvable rows for human review. Budget real engineering time here — this is where naive versions of this product die.

---

## 5. System Architecture

Deliberately boring stack — the value is in the data model, not the infrastructure.

**Ingestion (Python).** Scheduled jobs: daily transaction pull (Stats API), daily stat lines during season, annual draft/prospect/contract updates, one-time historical backfills (Retrosheet, PST, Lahman). Raw payloads land immutably in object storage; loaders normalize into Postgres.

**Core store (Postgres).** The schema centers on five tables: `people` (Chadwick spine), `regimes` (the curated FO table), `transactions` → `decisions` (a transaction is raw fact; a decision is the attributed, regime-linked interpretation, with acquired/departed asset lists), `asset_windows` (per player per decision: the control window acquired/surrendered), and `valuations` (per asset window per season: WAR captured, salary, surplus, realized vs. projected). Baselines (`draft pick expectation`, `prospect tier values`, `$/WAR by year`) are versioned reference tables so the whole site can be recomputed under a new methodology version — grades will change as methodology improves, and versioning is what keeps that honest.

**Attribution engine (dbt or plain SQL + Python).** Pure, deterministic transforms from decisions + valuations + baselines → channel grades → regime FOR. Everything recomputable from scratch; nightly rebuild is fine at this scale (the entire dataset is a few million rows — this is a small-data problem with a big-brain schema).

**Serving.** Next.js (or similar) on top of a read API; static-generate the heavy pages nightly, live-update only in-season stat lines. Public JSON API from day one — it seeds the citation flywheel.

**Multi-sport readiness.** Nothing above is baseball-specific except the valuation tables. The schema abstracts to: identity spine, transaction feed, value metric, contract data, regime table, channel baselines. NBA is the natural second sport (clean transaction data, public EPM/RAPTOR-style metrics, Spotrac/cap data, high fan interest in FO quality); NFL after (draft-dominated, harder value metric); NHL similar. Sport is a column, not a rewrite.

---

## 6. Roadmap

**Phase 0 — Spine (4–6 weeks).** Chadwick + Stats API transactions + regime table for 2015–present. Ship nothing; validate entity resolution on 10 famous trades end-to-end.

**Phase 1 — MVP (2–3 months).** All 30 current regimes, 2012–present decisions, realized WAR only (open-source value metric), trades + drafts + major-league FA. Ship: leaderboard, regime report cards, decision pages, methodology page. The launch content writes itself ("The most valuable trade of the decade", "Every current GM, ranked by receipts").

**Phase 2 — Full accounting.** Surplus dollars, contracts, extensions, non-tenders, passive losses, projected-remaining values, at-the-time snapshots, 2000–present backfill. This is where the ex-ante vs. ex-post split lands — the analytically distinctive feature.

**Phase 3 — History + API + premium.** Backfill toward 1990s/earlier (Retrosheet supports it), executive career pages and lineage trees, public API, premium alerts/exports.

**Phase 4 — Attribution layer + second sport.** Org-level player-dev deltas, scouting-director draft attribution, coach/dev storylines; NBA build on the same schema.

---

## 7. Risks & Open Questions

**Licensing** is the top risk (WAR, contracts) — mitigated by the own-metric path and by the fact that transactions, drafts, and biographical facts are uncopyrightable facts. **Methodology contestability**: every ranking will be argued with — that's a feature (engagement) if and only if the methodology page is airtight and versioned. **Attribution fairness**: ownership meddling, budget constraints, and inherited farm systems all confound "GM skill"; the site's stance is to measure *decisions vs. expectation given the choices actually available* and be explicit that FOR measures the regime's output, not the executive's soul. **Small samples**: badge, don't hide. **Maintenance load**: the regime table and PTBNL resolution need a human in the loop — small but nonzero forever.

Open questions worth deciding early: whether to pursue the FanGraphs license before or after MVP; whether "Ledger WAR" is worth the build cost as a brand asset; how aggressively to editorialize (neutral reference vs. opinionated grades — recommendation: neutral numbers, opinionated *writing* around them).

---

## Appendix A — Key public resources

Chadwick Bureau Register (github.com/chadwickbureau/register) · MLB Stats API (statsapi.mlb.com; wrappers: toddrob99/MLB-StatsAPI, pybaseball) · Retrosheet transactions & event files (retrosheet.org/transactions) · ProSportsTransactions archive (prosportstransactions.com/baseball) · Lahman Database (salaries, biographical) · openWAR paper (Baumer, Jensen & Matthews, JQAS 2015) · FanGraphs RosterResource transaction tracker · Wikipedia: List of MLB general managers · Sports Reference data-use policy (sports-reference.com/data_use.html) · Prospect-valuation research lineage (FanGraphs prospect surplus-value studies).
