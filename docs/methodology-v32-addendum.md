# Methodology addendum v3.2: the Retrosheet backfill, championship provenance, and trade market comps

October 14, 2026.

## 1. The feed gap, found and fixed (Retrosheet backfill 1998-2008)

While tracing the 2009 Yankees' championship roster, CC Sabathia's signing
could not be found. The reason turned out to be structural: **the MLB Stats
API transaction feed is effectively empty before 2009** (zero trade rows
2005-2008; ~170 rows in all of 2008 against ~1,000/year once coverage
starts). Every number built on "transactions from 2005" was actually built
on transactions from 2009, with 2005-2008 windows scored on drafts and
standings alone. The Beckett-for-Hanley trade was not in the book.

The fix was already sitting in the repo: the Retrosheet transaction archive
(1873-2022), ingested months ago for exactly this backfill.
`ingest/retro_backfill.py` maps Retrosheet rows 1998-2008 into the
transaction table: T/Tp to trades, F/Fo to FA signings, Fg to FA
declarations, W to waiver claims, D to Rule 5, R to releases. Players map
retro id to MLBAM via the full Chadwick Bureau register
(`data/retro2mlbam.json`, 24,622 mappings, built from
github.com/chadwickbureau/register; 94% of backfilled rows carry an MLBAM
id). Team codes map to era-correct API names (Devil Rays, Florida Marlins,
Anaheim Angels) so control-window value lookups match the value cache's
season strings. Each trade emits rows under both clubs with one shared
description, the scorer's deal-grouping key. 22,697 rows inserted; ~600
trades/year 1998-2008, consistent with the feed's own 2009+ volumes. The
feed remains the sole source from 2009.

The information used here was obtained free of charge from and is
copyrighted by Retrosheet. Interested parties may contact Retrosheet at
www.retrosheet.org.

Effects of the rescore (all disclosed on the site):

- Epstein's Boston trades fall from +23.1 to -26.5 (the Beckett deal's
  windows now count Hanley Ramirez's Florida prime; the 2007 ring is why
  the leverage lens and the Success column exist).
- Dombrowski's Detroit trades rise from +61.8 to +94.9 (the Cabrera heist
  enters the book).
- Late-era Beane's trades fall to -77.7; Sabean reaches +203.5 total.
- Cashman's active-window trades rise to +78.8 (2005-2008 now counted).
- Validation is stable (accounting r = 0.861 unchanged; predictive partial
  r 0.338 to 0.342): the backfill adds decisions, not value rows.

Windows and claims are unchanged: regime grading still floors at
2005-01-01. What changed is that 2005-2008 inside those windows is now
actually populated, and 1998-2004 rows exist for provenance tracing.

## 2. Championship provenance, computed (all 21 titles, 2005-2025)

`engine/champions_build.py`: for every World Series winner, the core
(players with >= 1.0 Ledger WAR in the title season) is traced to the
club's last acquisition event (feed + backfill) or draft pick. Channels:
FA, trade, draft, int'l/minor-league find; inherited means acquired before
the sitting regime's TRUE seat date (Cashman 1998, not his 2005 scoring
floor). The Champions tab renders every title's roster ledger plus a
21-title through-lines panel.

The through lines the data actually supports:

- The median champion was **88% built by its sitting regime** and won in
  **year 7** of the tenure. Nine of 21 titles came in year 10 or later;
  only three in the first three years. The quick-flip title is rare.
- **Free agency has been a majority channel exactly once** (2009 Yankees,
  56%), averaging 27% of core WAR across all titles.
- Only the three San Francisco titles were majority homegrown.
- Most trade-built: 2016 Cubs (44%). Most inherited: 2023 Rangers (85%,
  Chris Young winning with Jon Daniels' core two seasons after the
  handoff, the sharpest attribution case in the book).

## 3. Trade market comps

Every graded trade on an active or archive card now carries up to three
market comps (`engine/trade_comps.py`): the nearest deals by eventual value
received, same season phase (deadline / offseason / in-season), drawn from
the league-wide archive of **5,764 buyer-seat deals 1998-2023**
(`data/deal_archive.json`), with a 0.15 wins/year era-distance penalty and
one comp per counterparty-date. Each comp shows what the buyer eventually
received against what the surrendered players became for the seller, so a
verdict reads against the market for deals of that shape instead of in a
vacuum. Control buckets (rental / +1 / +2 / 3+ years) are measured from the
feed as seasons to the player's next free-agency declaration.

# v3.3 addendum: the 1998 floor, 28 championships, validation v2

October 14, 2026, same build day as v3.2. Four extensions.

## 1. The archive floor moves to 1998

Retrosheet backfill extended to 1985-2008 (provenance) with scoring windows
floored at 1998-01-01; drafts 1998-2004 backfilled from the Stats API draft
endpoint (verified: Pat Burrell #1 in 1998, Bullington #1 in 2002); park
factors extended to 1996 (pre-humidor Coors reads 1.26-1.31); the full value
cache rebuilt over 28,149 players; Montreal Expos alias joined so Expos-era
value rows land. The regime table (`data/regimes_hist.json`) now holds 110
archive regimes, including ~40 new or unclamped 1998-2004 windows (dates are
month-precise from documented GM history; 'approx' flags uncertainty, and
regimes seated before 1998 stay truncated with true start shown). Cashman's
ACTIVE window now runs from his real 1998-02-03 seat. Headline corrections
the fuller windows produce: the complete Billy Beane record is -28 net over
17.8 seasons (trades -54, waivers +14, drafts +12), Sabean's full window
reaches +226, and Cashman's draft channel drops to +17 once his barren
1999-2004 classes enter the book.

## 2. 28 championship ledgers, and the era through-line

All World Series winners 1998-2025. The strongest finding in the project:
the median title core was 48% self-built in 1998-2009 and 90% self-built in
2010-2025. The handed-down championship (1998 NYY 93% inherited, year one of
Cashman's seat; 2023 TEX 85%) is going extinct.

## 3. Validation v2: pooled design, honest intervals

The predictive study now pools 574 regime-years from 112 active and archive
regimes (futures bounded inside each regime's own window). Partial r of
decision value on future W%, controlling for record to date: 0.276, with a
cluster-bootstrap 95% interval of [0.164, 0.371] (B = 2000, resampling whole
regimes, the honest interval given overlapping regime-years). Grouped 5-fold
cross-validation (folds by regime) lifts out-of-sample R2 from 0.184 to
0.245. The effect survives on held-out regimes. Accounting check on the
full-coverage era (2015-2025): r = 0.853, MAE 5.3 wins.

## 4. Comps v2 and shareability

Trade comps now match on control bucket AND buyer posture (contender >= 85
wins pace / mid / rebuilder < 75) in addition to size, phase, and era.
The page itself gained Open Graph and Twitter cards with a generated
preview image, a favicon, a first-visit intro, and a mobile pass.

# v3.4 addendum: Ledger Projection v1 (the forward view)

October 14, 2026. Open deals now carry a projected rest-of-window and a
projected final verdict beside the realized grade. The projection is
self-built end to end; no licensed projection system is consulted.

Components (`engine/proj_v1.py`, curves in `data/proj_curves.json`):

- AGING CURVES by the delta method over the 28,149-player cache, hitters
  and pitchers separately, 3-age smoothing, n >= 30 per point. The textbook
  curve falls out: hitters peak at 27-28 and decline ~0.3 wins/yr through
  the 30s; pitchers decline flatter. Survivorship bias is the delta
  method's known weakness; the backtest is the arbiter.
- BASE SKILL: Marcel-style 5/4/3 weighting of the last three seasons,
  regressed 20% toward the population mean.
- FORECAST: base walked forward on the aging curve, zero floor, 10%/yr
  roster-uncertainty haircut beyond the first projected season. Control
  windows from the feed (free-agency declarations) bound every projection.
- PROSPECTS with no MLB track record: Pipeline-rank expectation (the same
  rank-to-surplus curve the deal marks use). Unranked traded prospects:
  the empirical mean outcome of 1,327 unranked traded pieces, 0.41 wins.
- BACKTEST: projecting each season from only prior data gives r = 0.619
  (2023, n = 1,093) and r = 0.667 (2025, n = 1,067) against actual
  next-season WAR, MAE ~0.8 wins: competitive with public systems.

Quarantine rule: the overlay is disclosed and the grades never move on a
forecast. Realized value is the ledger; the projection is the heading.
Worked example (the deal that prompted this): Cubs-Mets, Aug 3 2026,
Jefferson Rojas for Clay Holmes and Tyrone Taylor. The Mets' seat reads
-2.3 realized (Holmes and Taylor produced for Chicago immediately) with
projected final -6.4 (Rojas' rank expectation +4.3 against the veterans'
remaining windows); the Cubs' seat projects +3.2 final.

# v3.5 addendum: the Deal Desk

October 14, 2026. The forward-looking half of the system: a Deal Desk tab
where a hypothetical trade, free-agent signing, or extension gets a verdict
assembled from the ledger's own machinery. Trade pieces can be MLB players
(Ledger Projection v1 over adjustable control years), top-100 prospects by
rank (the rank-to-surplus curve), or draft picks (the slot curve). The
verdict: projected value each way, leverage-weighted at the club's current
standing; a market-rate check against the control-bucket price curves from
the 5,804-deal archive (with bust rates), flagged BELOW MARKET / MARKET
RATE / ABOVE MARKET; the three nearest real comps and how they ended; and a
counterparty card (trade grade, DNA tendencies, head-to-head record).
Signings and extensions grade with the exact accounting of the FA and
extension channels (market $/win forward table, QO charge, class discounts).
Sandbox rules: proposals are evaluated client-side and never recorded, and
real card grades never move on a forecast. Inside a club, the same
architecture pointed at internal projections and pref lists is a deadline
war-room tool. `engine/desk_data.py` builds the data pack
(`data/desk_data.json`: 2,035 players with recent form, ages, and control
defaults; curves; market constants; the compact deal archive).

# v3.6 addendum: calibrated contract terms, the payroll layer, the Horizon tab

October 14, 2026.

## 1. Suggested terms, backtested the only honest way

The Deal Desk now proposes contract terms instead of making the user guess.
Two components, both shown: the market-comp offer (median years and
inflation-adjusted median AAV of the eight nearest real contracts by blended
recent form, age, and position type, from the 1,616-contract book) and the
model-fair offer (years until projected season value thins below ~0.75 wins;
dollars = projected WAR x market $/win, class-discounted on extensions).

`engine/calib_suggest.py` backtests the suggester winter by winter: for all
1,224 book contracts signed 2010-2025, the suggestion is reconstructed using
only information available at the time (comps strictly earlier, that era's
$/win from the dpwHist table). Results: the market-comp offer is nearly
unbiased on ordinary deals (MAE 0.73 years, $3.6M AAV, total bias -$8.5M
driven entirely by stars) but reads the $100M+ class $92M light on average;
the model-fair offer prices stars better and overshoots small deals. The
headline Ledger offer is therefore a blend whose model weight ramps in only
above star-level projection value (w = clamp((undiscounted projected value -
$60M) / $120M, 0, 1)): mega-deal total MAE falls 97 -> 71, overall bias
-8.5 -> -1.9, and the 936 ordinary contracts keep the unbiased market read.
The residual star shortfall is disclosed, not tuned away: the market pays
elite free agents above both the comp median and model $/win.

## 2. The payroll layer

Committed payroll per club per season 2027-2031 is computed from the book:
guaranteed FA and extension dollars, AAV-spread. Signing and extension
verdicts show the club's committed payroll before and after the proposed
deal and distance to the $244M CBT reference line (2026 threshold; 2027+
awaits the next CBA). Disclosed limits: arb, pre-arb, options, and
mid-contract trades sit outside the book, so true payrolls run higher.

## 3. The Horizon tab

Every club's roster walked forward on the aging curves through 2031, bounded
by control: feed-derived service defaults extended by guaranteed contract
years from the book (the later of the two wins). Per season: projected WAR
total, controlled-player count, committed dollars, top contributors, and
whose last controlled season it is. Ranked prospects with no MLB track sit
on a farm line at rank expectation. Trade verdicts at the Desk append the
proposed deal's season-by-season effect on the club's horizon.

## 4. Deal memos

Every Desk verdict exports as a print-styled one-page memo (browser print /
save as PDF): proposed terms or pieces, suggested terms, the full verdict
tiles, market check, comps, counterparty card, payroll line, and the
sandbox disclosure. Client-side only; nothing is recorded.

# v3.7 addendum: durability, arb estimates, the draft room

October 14, 2026, same build day as v3.6.

## 1. Durability factor on Desk projections

`engine/pt_fetch.py` pulls 2024-2026 playing time for the 2,035-player Desk
pool (PA for hitters; IP and games for pitchers, starter vs reliever by
IP/G). Each player carries an availability factor 0.7 + 0.3 x weighted
recent availability (5/4/3 across observed seasons; PA/640 hitters, IP/165
starters, IP/65 relievers, capped at 1), multiplied into every projected
season at the Desk. Validation: projecting 2026 from 2024-25 with and
without the factor across 1,081 players gives MAE 0.859 -> 0.848 and bias
+0.06 -> -0.01, with rank correlation slightly down (0.584 -> 0.563). It is
a calibration fix for totals and dollars, published with both numbers.

## 2. Arb and pre-arb estimates; extensions join the book

The payroll layer adds estimated salaries for controlled players outside
the contract book: league minimum pre-arb, arb years at 25/40/60% of
projected market value (projected WAR x that season's $/win), free agency
at six years of service. True MLB seasons ride along in the Desk data pack
(the clamped control default is not a service record). The 61 major
extensions from the extension channel's own list are merged into the
contract book at CBT value where deferrals diverge, with a type flag so
contract comps keep drawing from free-agent deals only. Club payrolls now
read realistically (checked against five clubs across the spending range).

## 3. The draft room

A fourth Deal Desk mode prices pick packages on the maturity-adjusted slot
curve the draft channel grades with (future drafts discounted 10%/yr):
multi-pick packages both ways, pick-for-player via Ledger Projection v1,
each side translated to its nearest single-pick equivalent, the slot-curve
anchors printed on the verdict, and the variance warning stated plainly.
Disclosed framing: MLB only permits trading Competitive Balance round
picks, so this is the valuation chart a draft room argues from.

# v3.8 addendum: the completeness audit, and the Scenario Room

October 19, 2026.

## 1. The second self-audit: 133 invisible players

Found while building the Scenario Room: a scenario about Cleveland's 2017
Jose Ramirez extension read zero, because Jose Ramirez was not in the value
cache. The universe had been built from transaction-touched players, so
career-one-club stars who never hit free agency (intl signees above all)
never entered it. engine/cache_audit.py now checks every player with 150+
PA or 40+ IP in any season 1998-2026 against the cache: 133 significant
players were missing (Altuve, J. Ramirez, Salvador Perez, Acuna, Albies,
Chipper Jones, Helton, Duran, Pasquantino, ...). All rebuilt at Ledger WAR
v1.5 (park factors + defense join) and the chain rerun. Accounting
validation improved r = 0.853 -> 0.864 (MAE 5.3); predictive unchanged;
channel grades moved under a win (these players were rarely transacted,
which is exactly why they were missing); the 2015 KC and 2017 HOU
championship cores got their stars back; the Desk pool grew to 2,102.
cache_audit.py joins the refresh runbook so the hole cannot silently
reopen.

## 2. The Scenario Room

engine/scenario_build.py generates decision scenarios from the ledger
itself: 10 famous trades (both buyer and seller seats), 4 free-agent
signings, 1 extension, 1 live unsettled 2026 deal, plus 1 fictional
scenario synthesized client-side from the current data pack. Each carries
at-the-time context only: dated standings, win-curve leverage, computed
roster-need groups (weakest of C/IF/OF/P by that season's roster WAR,
an approximation from current primary positions), era $/win, and piece
info with contemporaneous Pipeline ranks. Pre-2011 prospect pieces carry
curated consensus tiers (flagged; the rank archive starts 2011). The
ex-ante expectation is deliberately crude and stated: last full season's
rate times typical control for the bucket, prospects at rank expectation,
unranked minors at the 0.41 empirical mean. Counters resolve by
deterministic rules from the control-bucket price curves (a counterparty
with an above-market deal in hand caves to a sweetener demand; a
below-market buyer walks), so every adjudication is explainable. Scoring
separates process (against the ex-ante market read) from outcome (the
archive's realized windows; the live scenario scores on projected final,
labeled UNSETTLED). Setup lines are curated color; every number is
computed.

# v3.9 addendum: the championship refresh, GM Mode, and two data hardenings

October 30, 2026.

## 1. The 29th ledger

Milwaukee won the Series. The full chain reran with the postseason final:
Success grades moved, and the champions machinery now carries 29 titles.
The 2026 Brewers enter as the modern era's great exception: 43% self-built
(2010-25 median: 84%), the most inherited championship core since the 2023
Rangers. The Arnold/Stearns attribution was re-verified against the public
record: Stearns stepped down October 27, 2022; the stored windows are
Stearns 2015-09-21 to 2022-10-26 and Arnold from 2022-10-27, so the July
2022 draft class (Misiorowski) is Stearns' and the December 2022 Contreras
trade is Arnold's. Convention, stated: the ledger credits final baseball
authority, so 2020-22 (Arnold as GM under Stearns' presidency) is Stearns'.

## 2. GM Mode

The offseason, playable. Your winter inbox is real (your club's actual
free agents; the arb class at estimated awards). The FA market is the real
2026-27 class, computed from service and contract coverage, each name
carrying the calibrated Ledger offer. The trade board lists short-control
talent on sub-79-win clubs (availability heuristic, disclosed) priced by
the control-bucket market rates; any other player can be priced on demand,
with a contender premium; counterparties answer deterministically by the
market band. Extensions grade against the class market. Every move is
graded at signing; payroll and the CBT line run live. Closing the winter
produces: a grade (total projected surplus), a projected 2027 record
(league calibrated to .500, the accounting metric's ~5-win MAE carried as
the error bar), and the five real club-winters 2009-2024 nearest in shape
(prior wins, FA dollars, signings, trades), with what happened to those
teams the next season as history's base rate.

## 3. Contract comps hardened

Comps now hard-filter to the same player type (a pitcher never comps to a
hitter contract), carry a position-group penalty (C/IF/OF; SP/RP) from the
new group field on book and player rows, and display each comp's AAV
restated in 2027 dollars via the $/win history, so an old contract reads at
today's prices. The suggester re-backtested under the hard filter: MAE 0.74
years / $3.6M AAV, unchanged; accuracy cost nothing.

## 4. The extension-book coverage audit

Building the FA class exposed stars with live contracts reading as free
agents. Ten long-term deals were missing from the extension list (Lindor's
10/$341M above all, plus Devers, Trout, Wheeler, Chapman, Alvarez, Webb,
Perdomo, Arenado's exercised 2027, and Willson Contreras' FA deal absent
from the source csv). All verified and restored: the FA class now leads
with the players who are actually free, and club payrolls picked up the
missing money (the Mets' 2027 book went from $234M to $268M). Residual
known limits: service time is proxied by seasons with MLB value, so a few
late-debut players sit one year early in the class; traded contracts stay
with the signing club in payroll.

# v4.0 addendum: the continuity lens, and GM Mode v2

October 30, 2026.

## 1. Reconciling the underboss problem

Regime attribution credits final baseball authority, because that is the
only rule that applies consistently across 139 regimes. But an internal
promotion blurs it: the new boss was in the room for the predecessor's
decisions. The answer is a second, disclosed lens rather than a changed
rule. Championship cards where the winning executive held the chair
immediately below before promotion now carry a CONTINUITY VIEW: the share
of the title core acquired while he already sat in that chair. Verified
dates: Arnold named Brewers GM 2020-11-19 (Stearns stayed as president);
Young named Rangers GM 2020-12-04 (Daniels stayed); Cashman assistant GM
from 1992 (month approximate, flagged). The lens recasts the three most
inherited champions: 1998 NYY reads 7% Cashman-built by final authority
and 87% with-him-in-the-room; 2023 TEX 15% and 76%; 2026 MIL 43% and 69%.
Both numbers are true; they answer different questions; the cards now
carry both.

## 2. GM Mode v2

The winter now flows like the calendar: (1) contract decisions, with
qualifying offers (1/$22M; acceptance deterministic from the player's
calibrated market) and arb tenders; (2) the exclusive re-sign window;
(3) the open market with trades and extensions; (4) the depth chart;
(5) the report card. Advancing out of the exclusive window resolves
unsigned free agents to other clubs, and a declined QO banks the comp
pick when the player walks. Negotiations are offer/counter against a
deterministic camp: each player carries a stable personal ask (his
calibrated Ledger offer times a hashed 0.95-1.17 greed factor, a 5%
hometown discount in the exclusive window); serious offers draw midpoint
counters with eroding patience, two lowballs end the talks. The depth
chart auto-fills C through RF, DH, five starters, seven relievers, and a
bench from the org by projection, using season-workload SP/RP resolution
and true positions (new field in the data pack); holes are flagged
against an everyday bar and matched to available market names. A winter
memo prints the whole thing. Projections, grading, payroll, the CBT line,
and the historical comp winters are unchanged from v3.9.

# v4.1 note: the paper ledger

October 30, 2026. A visual identity, not a methodology change: the site now
dresses like what it is, an accounting ledger that happens to be about
baseball. Cream paper, iron-gall ink, a serif masthead, feint rules with
the oxblood margin line on every table's first column, grade chips as
scorebook stamps, and a Night desk toggle for the dark room. The mark is a
baseball ruled like ledger paper: blue feint lines, red stitching, drawn in
SVG by hand. No number moved.

# v4.2 note: the trade desk

October 30, 2026. GM Mode's open market rebuilt on the pattern the great
sim franchises settled on: everything on screen, nothing in a pop-up. The
trade desk shows the counterparty's controlled roster and farm on the
left, your assets (including your actual ranked prospects, by name) on the
right, and the deal on the table in the middle with the ask priced live by
the control-bucket market, a fill meter, and a deterministic response that
names the gap and suggests the piece that closes it. Trading real players
moves them on and off your roster, depth chart, and projection. The
free-agent market gained position and name filters, with every negotiation
already inline. And the winter journal now records everything: every
offer, counter, rejection, QO, tender, trade conversation, and stage
advance, newest first, printed in full on the winter memo.

# v4.3 addendum: surplus-value trade logic, and the FA pricing re-fit

October 30, 2026. Both fixes came from the same user test: GM Mode accepted
Bobby Witt Jr. for Juan Soto instantly, and priced mid-tier free agents
near $200M.

## 1. Trades price surplus, not gross projection

The desk was valuing pieces at projected WAR over control. The currency of
real trades is SURPLUS: discounted projection minus salary at $/win. Under
surplus accounting Witt (elite production, ~$26M AAV, long control) prices
at +17.5 while Soto (the same class of production, paid retail) prices at
-8.9 and Lindor at -3.2: a big salary is not a trade chip. On top of the
currency: franchise cornerstones (surplus >= 5, control >= 4) are
unavailable from clubs that are not selling and cost 1.75x from clubs that
are; contenders charge 1.5x; negative-surplus contracts trade as salary
dumps (the seller eats half the negative in ask relief); and acquired
salary lands on your payroll against an ownership capacity ceiling
(~1.3x your entering commitment), which blocks deals your market could
never absorb. The refusal message shows the arithmetic.

## 2. FA pricing: sliding scales for forward years

The old model-fair rule ran years until projected value thinned, which
gave steady 29-year-olds eight-plus years, and the star gate keyed on that
inflated total, flipping mid-tier players to full model weight ($200M
Hoerners). v4.3: the star gate reads FIRST-YEAR projection ((proj1 - 3.2)
/ 2.5); years are capped by age at signing (hitters 11 - (age - 26),
pitchers one fewer, stars earn back up to two); out-year dollars decay at
0.93/yr, fading to a 1.05 premium at full star weight. Re-backtested
winter by winter on the same 1,224 signings: the Ledger offer's miss
improves from 0.74 to 0.72 years, $3.6M to $3.5M of AAV, and $15.7M to
$14.8M of total value, with the mid-tier ($25-100M) error falling from
~$28-32M to ~$28M and bias cut in half. Checked against the public
2026-27 projections (B/R, Yahoo, ESPN insiders): mid-tier names now land
in the consensus band; the model still reads the very top of the market
light, the same disclosed star premium the market itself produces.

# v4.4 addendum: the contract model re-fit and the assistant GM (Oct 2026)

## 0. A data audit first

The re-fit began with a position refetch for all 28,282 players in the
value cache (live feed primaryPosition). The old positions file was
missing or wrong for roughly 440 of the backtest's contracts: Jon Lester,
Stephen Strasburg, and Jordan Zimmermann priced as hitters, Trea Turner as
a pitcher. Since the suggester hard-filters comps by player type, each
error poisoned comp pools in both directions. Fixing the data (and
excluding internationals with no MLB track record, who are unknowable
in-model: Yamamoto, Tanaka, Jung Hoo Lee are flagged, not priced) improved
every tier before a single rule changed. Signings evaluated: 1,196.

## 1. v4.4 pricing rules

Mega deals were systematically light (bias -$82M on the $200M+ class)
because the star gate keyed only on first-year projection, so a star off a
down platform year (Harper '18, Seager '21) priced as his worst season,
and ace pitchers never cleared the hitter-calibrated gate. The v4.4 rules,
each a market structure, not a curve fit:

- Pedigree gate: stardom is the best of the last FIVE seasons, decayed
  0.88/yr and discounted by age at signing. Harper '18 moves from a
  2 yr / $18M suggestion (platform year 3.0) to 11 / $255M vs the real
  13 / $330M.
- Pitcher market: gate 2.8 (vs 3.2) and pitcher wins paid 1.28x flat
  $/win. Scherzer '14 moves from 5/$97M to 7/$176M vs the real 7/$210M.
- Convex elite premium, shrunk inputs: +15% per win above 3.5 (capped),
  computed on projections shrunk 0.7x above 4.5 wins. The market pays for
  scarcity and prices elite regression risk at the same time.
- Years gates split: dollars blend toward the model at the star gate, but
  YEARS blend at a softer gate (eff 2.1, span 2.7), because mid-tier
  regulars get model-length deals at comp-driven AAVs.
- Spread years: at star weight >= 0.5, extra years at the same total
  (the AAV-flattening structure of real megadeals; Soto suggests 14/$776M
  vs the real 15/$765M).
- Comp plausibility filter: when the subject is an everyday player
  (blended platform >= 2), comps whose own contract repudiated their
  platform value (AAV under 25% of platform x era $/win: non-tenders,
  injury collapses) are dropped from the pricing median. They carry
  information about risk, not price. Depth signings keep them, because at
  that end of the market those outcomes ARE the price.

Walk-forward backtest, same protocol (comps strictly earlier, era $/win):

- ALL (n=1,196): 0.69 yrs / $3.2M AAV / $14.0M total (v4.3: 0.72/3.5/14.8)
- Mega $200M+ (n=22): total MAE $91M, bias -$2M (v4.3 rules on the same
  corrected data: $119M, bias -$21M; on the old data: bias -$84M)
- Big $100-200M: $62M (from $71M); mid $25-100M: $26M; small: $6.7M
- The $100-200M class remains modestly light, disclosed: auctions for
  scarce players end above any median.

One in-page fidelity fix: the page's median took the upper element on
even-sized comp pools where the backtest averaged the middle two; with the
plausibility filter producing even pools often, that skew mattered
(Chisholm 7/$191M wrong vs 5/$106M right). The page now computes the true
median, matching the backtest exactly.

## 2. The assistant GM

GM Mode now seats a second voice at the desk, rendered as a standing
counsel card beside the winter log. Everything it says is computed from
the same engines the mode already runs on, so the advice is deterministic
and auditable:

- Stage counsel: QO recommendations (projection x $/win against the $22M
  offer), non-tender flags (estimated award vs projected value), re-sign
  vs let-walk advice in the exclusive window (with the hometown discount
  and whether he covers a depth-chart hole), market targets matched to
  your actual holes, depth-chart triage, and a closing review naming your
  best piece of business and the one to take back.
- Negotiation reads: during any live negotiation, the counsel compares the
  camp's current ask to the calibrated Ledger offer and says whether to
  meet it, counter under the midpoint, or walk, and warns when one more
  lowball ends the talks (the camp's patience rules are real and the
  advice knows them).
- Contract comps with outcomes: for players on the table, the two or three
  nearest real contracts from the 1,689-contract book, era-adjusted, each
  tagged with how it aged (aged well / broke even / aged poorly / a
  burden) from realized ledger value against implied cost.
- Posture and payroll: counsel adapts to your club's standing (contender /
  bubble / fringe / rebuilding) and warns on CBT proximity.
