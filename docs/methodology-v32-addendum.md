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

# v4.5 addendum: position truth, the diamond, and the public pass (Oct 2026)

- Position-fit map. Depth-chart filling and every assistant-GM recommendation
  now run on explicit position fits (a shortstop slides to second or third; a
  second baseman is not an answer at first base; corner bats cover first and
  DH; only catchers catch). Scarce positions fill first so a star shortstop is
  not burned at third. Audited across clubs: zero non-fitting assignments.
- The diamond. The GM depth chart renders as a scorebook field diagram with
  players at their positions, rotation/bullpen/bench rows below, weak slots
  flagged in red, and market fixes listed under the chart.
- Trade bridges. When an offer is short, the assistant GM names the cheapest
  pieces from your own system that close the gap, valued on the same prospect
  EV curve the ask uses.
- Payroll integrity fix. Book money now leaves with a traded player; verified
  on the Soto case ($51M off the 2027 estimate on execution).
- Counsel fix: an empty block-list no longer reads as a cornerstone refusal.
- Charts, all inline and theme-aware: the full 1,196-signing calibration
  backtest as a log-log scatter (one dot per contract, hover for the terms) in
  Methodology; in the GM report, a strip of your projected wins against
  standing pat and the five most similar real winters, and a committed-payroll
  bar chart 2027-2031 with the CBT reference line and your winter's estimate.
- The footer changelog is consolidated into grouped release notes; the in-page
  methodology is reorganized into a single coherent document (value engine,
  grading engine, markets, projections, pricing, rooms, validation) instead of
  version-ordered patches.

# v4.6 addendum: negotiation structure, the salary book, and the live diamond (Oct 2026)

- Negotiation economics. The camp now values an offer at ITS preferred
  structure: dollars in years beyond the ask are worth 45 cents each, so
  2 yr / $30M no longer beats a 1 yr / $29M ask (the agent will say so), and
  shorter-at-higher-AAV offers price correctly. Counters are restated in the
  camp's own years, and a counter that would barely beat your number is an
  acceptance, not an echo you have to re-click.
- The assistant GM's call sits inline on every QO and arbitration row
  (offer it / let him walk, tender / non-tender candidate), same math as the
  counsel card.
- Team salary book: an OOTP-style forward-obligation table for any club,
  player by season 2027-2031, bold for guaranteed book money at CBT values,
  (A) for arbitration estimates on the 25/40/60 ladder, (^) for pre-arb,
  with season totals against the CBT reference. Lives on the open-market
  stage so you can scout a counterparty's books before a trade.
- The depth diamond is live on every stage as a compact card in the rail,
  with holes named; stage 4 keeps the full chart.
- Every long player list scrolls inside its card instead of cutting off.
- Trade counsel knows the counterparty's historical tendencies (their
  regime's ledger DNA: drafts arms, trades for bats, and so on) and says
  what to shop them.
- Extension-book coverage: Yelich (9/$215M) and Keibert Ruiz (8/$50M)
  restored; a duplicated Wheeler extension row that double-counted $42M/yr
  on Philadelphia's book removed.

## v4.6 follow-up: the winter reality pass (same day)

The computed FA class is now reconciled against the actual 2026-27 winter
(the league's option tracker and the published class rankings, Nov 2026):

- Exercised and plainly in-the-money 2027 club options are encoded as
  one-year book coverage at the option price (William Contreras $15.5M,
  Paredes, Alcantara, Clase, Whitlock, Yandy Diaz, Albies, Munoz, Gonsolin),
  so those players price as controlled salary, not free agents.
- Opt-outs and declined options void remaining coverage (King, Holmes,
  Imanaga are in the class; their historical contract rows keep original
  terms so comps stay honest, with a fa27 exclusion list doing the work).
- The service-time proxy (seasons with recorded value) overcounted
  cup-of-coffee years and wrongly promoted Joe Ryan, Oneil Cruz, Jarren
  Duran, Detmers, Gilbert, Jax, and Stephenson into the class; curated true
  service keeps them home and prices their arb years correctly. NPB-origin
  players free by contract expiry (Suzuki, Imanaga) are encoded FA-eligible.
- Missing guarantees added: Pablo Lopez 4/$73.5M, Glasnow 4/$110M.
- Incoming NPB postings in the real class (Sato, Taira, Itoh) have no MLB
  track record and are outside the engine's universe, disclosed as before.

# v4.7 addendum: the attribution audit and the public-polish pass (Oct 2026)

- ATTRIBUTION FIX (the big one). The international-signings channel never
  window-filtered: every club signing since 2005 was credited to the
  CURRENT regime (a 2025 hire inherited two decades of IFA classes). Now a
  signing belongs to a regime only if its class year falls on that regime's
  watch, and the class baseline is league value over 30 clubs (every club
  shops every near-equal pool). All other channels were audited and already
  window-filter correctly. Channel nets re-merged idempotently.
- Internal model-version labels (engine names, sweep numbers, pass numbers)
  removed from every public-facing string, including generated tree notes
  and archive badges; versions live in source control, not on the page.
  The sharpest recipe constants were also removed from public prose; the
  methodology explains mechanisms and shows backtest results instead.
- Styles replace archetypes: two distinctive traits per front office,
  scored as the regime's largest league-relative deviations across
  development, acquisition taste, market skill, and temperament, drawn
  from a wider vocabulary.
- Head to Head adds the busiest phone lines: most-frequent trading
  partnerships, with every deal between the pair expandable in place and
  linked into the transaction trees; per-regime matchup rows expand the
  same way.
- Open-ended chains are backfilled from the value cache: a chain now ends
  with what actually happened (still with the club through 2026; no MLB
  appearances after a given year, settled; or left without a graded move,
  last seen with a named club), instead of a shrug.
- The assistant GM now sits at the Deal Desk (trade and signing verdicts
  get counsel: do/do-not with the leverage math, roster-fit against the
  club's computed holes, counterparty style) and in the Scenario Room
  (a stated lean with reasons on every decision point, from the same
  knowable numbers the process grade uses).
- Champions tab adds the side-by-side: all 29 title cores sortable by core
  WAR, share built by the sitting regime, continuity share, and channel
  mix, with a bar per row.
- Fixes: the leaderboard header was missing its Retention column (every
  header to its right was one column off); club nicknames render Red Sox,
  White Sox, and Blue Jays in full; GM Mode states that every number on
  the screen is Ledger WAR.

# v4.8 addendum: arbitration realism and the fit-and-finish pass (Oct 2026)

- ARBITRATION FIX (circularity). Awards were priced off the same projection
  used to value the player, so the model could never recommend a non-tender:
  salary was 25/40/60% of value by construction. Arbitration is
  backward-looking, so the 2027 award now prices the season the player just
  PLAYED (platform value, with a one-year blend), while the tender decision
  weighs that award against the forward projection. The league now shows 77
  non-tender candidates across 28 clubs, which is what a real winter looks
  like; the gap between what arb pays for and what you receive IS the
  non-tender decision, and the assistant GM now names the worst cases.
- A methodology-reorder bug had moved the Validation, inside-a-front-office,
  and About sections out of Methodology and into every report-card ledger
  table header; both sides fixed.
- The rail depth card now stacks compact rotation and bullpen rows under
  the diamond.
- Pop-out trees: any player's full chain opens in an overlay from wherever
  his name appears (Deal Desk pieces, GM trade desk, the salary book), with
  endings from the value cache.
- Champions page: the side-by-side is the landing, selecting a club scrolls
  to its card, channel percentages are computed from the full core
  regardless of who inherited it (the 1998 Yankees now read 33% trade / 45%
  international / 22% FA with 7% built by regime and 87% with continuity),
  and the continuity column fills with the regime share where no deputy
  window applies.
- The season-by-season salary book now also lives on the Horizon tab for
  every club, outside GM Mode.

## v4.8.1: the combing pass (same day)

- Full-tab click-through at desktop and phone widths, zero console errors
  on every view in both themes; phone-width horizontal overflow eliminated
  (wide tables and the championship strip scroll inside their cards, team
  selectors capped).
- Boundary audit: every dated decision on every active regime card checked
  against its regime window. One class of display error found and fixed:
  international-signing entries carried a fabricated January class date
  instead of the true signing date, which made correct attributions look
  wrong (Perdomo, Nov 2016, reads under Hazen with the real date now);
  window filtering now uses the true signing date as well. Re-audit: zero
  violations across all cards, and zero championship-roster acquisition
  dates after the title year.
- Seat check against the record: the recently changed chairs (Mozeliak as
  Angels interim from June 2026, Zoll running Twins baseball operations
  from January 2026, DePodesta in Colorado, Toboni in Washington, Bloom in
  St. Louis) all match the reporting, with interim status flagged.

# v4.9 addendum: the shopping fingerprint and launch hardening (Oct 2026)

- THE SHOPPING FINGERPRINT. Every sitting regime's acquisitions since 2016
  (trades in + major league FA signings) joined to the player's public
  Statcast profile in the season the front office evaluated, z-scored
  within season: contact quality, chase, whiff, sprint, walks for hitters;
  velocity, bat-missing, ground-ball rate, chase induced, walks for
  pitchers. Persistent deviations read out as revealed preferences on the
  Org DNA tab (new Shops for column), the Deal Desk counterparty card, and
  the assistant GM's trade counsel. Under eight joined acquisitions on a
  side reads thin sample, never a forced label. New engine script:
  savant_fingerprint.py; new data artifact: fingerprints.json.
- Found and fixed while wiring it: the Deal Desk counterparty card and the
  counsel tendency line matched regimes on a field the auto cards never
  had, so counterparty intel silently never rendered for 27 of 30 clubs.
- Counterparty fit pricing: in GM trades, a piece that fills one of the
  counterparty's computed roster holes is worth 10% more in their eyes.
- Methodology adds the durability-divergence disclosure on the terms
  backtest and the trade archive through-2023 fit boundary.
- Launch hardening: acceptance tests committed under tests/ (three
  harnesses; every check encodes a previously shipped bug); the refresh
  runbook rewritten to the current pipeline including winter-reality
  maintenance; all current data artifacts committed; the Nov 3 scheduled
  task repurposed to the option-deadline reconciliation; the social
  preview image re-rendered in the paper-ledger design; a cookieless
  analytics snippet staged behind a comment; the application packet
  rebuilt with current numbers, GM Mode, and the fingerprint.

# v5.0: the public layout (Nov 2026)

- The name stays Front Office Ledger.
- Navigation reorganized into labeled sections, newspaper-style: THE GRADES
  (Leaderboard, Report Cards, Champions), THE TREES (Transaction Trees,
  now the home of all chain exploration), THE INTEL (Org DNA, Head to
  Head, Horizon), THE ROOMS (Deal Desk, Offseason Simulator, Scenario
  Room), THE METHOD (Methodology).
- GM Mode is renamed the Offseason Simulator everywhere.
- The Trees tab gains "Follow any player": type any of 2,800+ names on the
  graded ledger and get his full chain inline, every onward move with how
  it ended, alongside the existing per-regime trees and curated showcases.

## v5.0.1 (November 1, 2026): Results-grade window and the championship trend

- Results (Success) grades now include the completed 2026 postseason. The
  October blend had stopped at 2025, so the 2026 champion's regime card read
  zero titles. Milwaukee's Matt Arnold now carries the 2026 ring.
- Postseason refetches are rebuilt from scratch each run. Series wins had
  been accumulating across refetches of the current year and in-progress
  series could latch a pennant; 2026 is now clean (one pennant per league,
  one title).
- W%, division titles, and October credit now share one window: a regime
  hired after a season ends gets none of that season. Previously W% and
  division titles counted the hire year itself (an October 2014 hire was
  credited with the 2014 division title). Largest moves: Baltimore .448 to
  .469 (D to D+), Colorado .312 to .358, Dodgers division titles 12 to 11,
  Cubs 1 to 0.
- Regular-season tiebreaker games (Game 163, gameType R in the postseason
  feed) no longer count as October. They had been credited as playoff
  berths and series wins: six berths for clubs that lost a Game 163 and
  missed the postseason (the 2007 Padres, 2009 Tigers, and 2013 Rangers
  among them) and an extra series win for each tiebreaker winner (the 2018
  Dodgers: 19 series wins over the Friedman window, not 20). The full
  1998-2026 postseason set was refetched.
- The three curated cards (Dodgers, Orioles, Brewers) keep hand-verified
  decision pages, but their Results block is objective standings data and
  now syncs from the computed sweep on every regen. It had been typed in by
  hand and drifted, which is how the 2026 champion's card read zero titles.
- Championship through-line corrected. With 29 titles and the v4.8 roster
  accounting, the median title core was 48% self-built in 1998-2009 and 74%
  in 2010-2026, not 90%, and seven of seventeen titles since 2010 came on
  majority-inherited cores (2021 Atlanta, 2022 Houston, 2023 Texas in a row).
  The earlier "inherited title is going extinct" reading is withdrawn; the
  Champions landing now computes this sentence from the data instead of
  carrying it as fixed text.

## v5.1 (November 1, 2026): full-site math audit

Every computed number on the site was re-derived by independent checks (three
parallel audits of the grades, the rooms, and the trees and prose, then a
regression suite that encodes each finding: `tests/t_math.mjs`). What changed:

Arbitration and service time
- Service time is now real MLB service rebuilt from each player's transaction
  history (`engine/svc_fetch.py`: selections, recalls, options, outrights,
  MLB injured list, rehab assignments; All-Star, Futures, WBC, and Fall League
  "activations" ignored; seasons scaled to a 186-day calendar and capped at
  172 days). The old proxy counted any season with an appearance as a full
  year, which put 2022 September call-ups at five years of service. Checked
  against hand counts and known cases: Witt and Rodriguez 5.000, Henderson
  4.037, Carroll 4.039, Skenes 2.136 (Super Two), Baty 3.094. It also showed
  Tyler Stephenson IS a 2026-27 free agent (6.050), which the old manual fix
  had wrongly blocked.
- The arbitration award is recalibrated against 48 real 2026 arbitration
  salaries (agreed figures, or filing midpoints where a hearing was pending):
  award = (0.6 + 1.0 x platform WAR) x class step (1.0 first award, 1.5
  second, 3.1 later) x $/WAR drift. Leave-one-out miss about $1.6M per player
  (median $1.3M), no bias. The old 25/40/60-of-market rule missed by $3.3M
  and ran $3.0M hot. Brett Baty: $12.0M became $2.7M (first award);
  Francisco Alvarez: $14.4M became $4.6M (second award). One model now
  serves every page (the Desk's payroll line used a second, older one).
- Non-tender calls compare the award's cost over a minimum-salary
  replacement with the player's projected value (85 calls across 29 clubs).
- The qualifying offer is the real 2026-27 figure, $23.15M (it was $22M).

Engine corrections (full scoring chain re-run)
- Duplicate feed rows (the same waiver claim filed up to four times) are
  removed before scoring.
- Trades are grouped by deal, not by description text: the feed sometimes
  files one trade in fragments (Toronto "got nothing" for Halladay) or adds a
  garbled second copy of an incoming player (the Cronenworth row that put
  +17.1 on San Diego's card twice). San Diego's trade ledger moved from -18.6
  to -64.9; most cards moved by under two wins.
- The Lindor/Carrasco trade exists in the league feed only as one garbled
  row with no origin club and none of Cleveland's return; it is now repaired
  from the public record (Mets +7.7, Cleveland -7.7 on that deal).
- A departed piece's value now follows every name his new club has used, so
  the two seats of a trade mirror each other through the Indians/Guardians
  and Oakland/Athletics renames (Head to Head is now symmetric everywhere).
- Retention excluded re-signings: a free-agency filing followed by a season
  back with the same club counted as a departure that "did nothing
  elsewhere," which credited the club with the whole expectation (the
  Yankees' card carried +133 wins of it). Re-signings are excluded and the
  curve is centered (mean gap per departure 0.0). Cashman's total moved from
  +137 to +28.
- The composite grade is recomputed after every channel lands (22 stored
  grades were stale), and the three hand-verified cards obey the same grade
  thresholds, the same retention channel, and the same total as every other
  card. The report-card net now matches the leaderboard's.
- Head-to-head deal lists show up to 60 deals and say when a list is partial.
- Org DNA's injured-list rate was divided by seasons twice; fixed, and
  counted over the seasons the feed covers.
- Championship tenure counts seasons the leaderboard's way (a fall hire's
  first season is the next one): median title in year 5, 11 of 29 titles in
  a regime's first three seasons. The computed ledger is canonical for every
  title; the two hand-written cards keep their stories on top of it.
- Validation after the re-run (575 regime-years once the archive windows
  were corrected): partial r 0.27, cluster-bootstrap 95% CI [0.15, 0.36],
  out-of-sample R-squared 0.181 to 0.235 (was 0.276, [0.16, 0.37], 0.184 to
  0.245). Accounting check unchanged at r = 0.864.

Payroll, control, and the Offseason Simulator
- Book money follows the player to his current club, and a newer contract
  supersedes the one it replaced (Devers is on San Francisco's payroll, not
  Boston's; Bregman's Boston deal no longer stacks on his Cubs deal). The
  salary book closes exactly to every payroll widget, including a line for
  guaranteed money with no active player behind it.
- A club's own free agents are no longer under control in 2027 (Horizon), and
  six-year veterans with no deal are free agents, never controlled.
- Extensions replace the salary they supersede instead of stacking, and a
  player can be extended once.
- A declined QO earns the comp pick only when the market closes without you
  re-signing him; players whose exclusive window closes hit the open market
  instead of "signing elsewhere" while staying signable.
- The camp's ask for an extra year adds money (about 60% of the AAV) instead
  of stretching the same total.

Trees
- Every trade 1998-2026 is graded from every seat (`engine/trade_book.py`,
  4,372 deals, cross-checked against 1,701 card decisions: all but one match
  within 0.15). The player finder shows a full career: origin, every trade
  with both clubs' grades and every other piece's onward chain, signings with
  terms and realized value, extensions, and where it stands.
- Regime trees match the right deal on busy deadline days, label the
  executive actually in the seat on the trade date, and the three
  hand-verified cards now get trees from the trade book.
- The Orioles card's Hays trade is corrected (Dominguez and Pache, +1.1;
  Laureano arrived separately as a free agent).

Prose
- Restated from the data: the contract book (1,701: 1,618 free-agent deals
  and 83 extensions, 2006-2026), the trade archive (5,804 deals), the rental
  study (224 rentals; 0.8 is the all-rental rate, the nine star rentals ran
  nearer 1.2), the leverage curve (about 2.5x at 70 wins, 2x at 105), and the
  contract-backtest megadeal figures ($91M miss vs $140M for the comp median,
  no bias). Claims that could not be reproduced from current data were
  replaced with ones that can.

Second pass (same day, after an independent re-audit of the fixes)
- Trade returns filed under minor-league affiliates are recovered from the
  daily feed (`engine/trade_repair.py`, 450 rows, affiliates mapped to their
  parent club per season): Toronto now receives Drabek, Taylor, and d'Arnaud
  for Halladay. About 850 trade seats still show value on one side only; they
  are cash, bonus-pool money, players to be named (whose completion is filed
  as its own dated entry), or returns the feed never filed.
- Multi-team deals: legs that share a player are merged into one deal, and a
  player who only passes through a seat (Gregorius in the Choo/Bauer
  three-way) is neither received nor surrendered there.
- Waiver claims de-duplicate even when one copy of the row lacks the losing
  club (29 claims had still counted twice).
- Archive windows corrected where they overlapped or left gaps: Dick Williams
  (Cincinnati) ends October 2020, Al Avila (Detroit) August 2022, Jon Daniels
  (Texas) August 2022 (Chris Young was GM under Daniels's presidency from
  December 2020; final authority carries the grade). 39 Texas and Detroit
  trades that sat on no card are now graded; Cincinnati deals are no longer
  graded on two cards.
- The three hand-verified cards (Dodgers, Orioles, Brewers) are now graded by
  the engine like every other card, with their hand-written decision pages
  kept below the computed ledger as a showcase. Their totals moved: Friedman
  +58 (was +113 on the hand card), Elias +42 (was +56), Arnold +64 (was +32).
  Two showcase dates were wrong and are fixed (Kimbrel, April 2022; Rogers,
  July 30, 2024).
- Offseason Simulator: a player extended and then traded takes the extension
  with him (no ghost payroll, no lingering surplus); salary-shedding trades
  are never blocked by the ownership capacity check, and free-agent signings
  now face the same check trades do; the Team salary tab shows your club after
  this winter's moves, so it agrees with the payroll rail.
- Horizon no longer marks players controlled past 2031 as ending in 2031.
- Org DNA's injured-list rate counts placements only and includes the
  pre-2019 "disabled list" wording, over the seasons the feed covers.
- Champions: core pieces born in draft territory with no draft record (Jeter,
  Posada, Rollins, Glaus) are amateur draftees from before the draft table's
  coverage, not international finds; the side-by-side table now says that its
  channel columns count original arrival, not the sitting regime's share.
- The report card's surplus tile prices net WAR at the tenure's own average
  market rate instead of 2026 dollars.

## v5.2 (November 2, 2026): the real winter, the posted class, org prospects

The Offseason Simulator now runs the 2026-27 winter as it actually stands,
not as service time alone implies.

Real decisions (`engine/winter_2026.py`, applied in `desk_data.py`)
- Free agents are taken from the league feed's own filings (every "elected
  free agency" row since October 1), plus declined options, opt-outs, and
  released players from the MLB.com 2027 options tracker and per-player
  reporting (each veteran row in `data/vet_status.json` carries its source).
- 29 deals the base contract book lacked are now on file for 2027 (Sale's
  $27M extension, Hoerner's 6 yr / $141M, Rasmussen's $20M option,
  Acuña's $17M option, Castillo's money in Chicago, and so on). These rows
  carry payroll and control only; they are never used as pricing comps.
- Retired players and Emmanuel Clase (restricted list) are off every board.
- Options still open on November 1 are due November 2. Until they post, the
  Ledger models each side's arithmetic and says so on the player's row: club
  options exercised when projected 2027 value at $10M per win clears the
  option net of its buyout, mutual options declined, player options and
  opt-outs kept. A refresh rewrites these rows once the decisions are filed.
- Imai's guarantee corrected to 3 yr / $54M (the $63M figure included
  incentives).
- Qualifying offers follow the CBA: a player who changed clubs after Opening
  Day (trade, waiver claim, in-season signing) or who has received a QO
  before cannot get one. The simulator lists who is ineligible and why.

The posted class (`engine/posted_build.py`, `data/posted.json`)
- Teruaki Sato, Kaima Taira, Hiromi Itoh (NPB), and Si Hwan Roh (KBO) are in
  the open market with their posting club, 2026 line, and signing deadline.
- No public projection the Ledger trusts translates NPB or KBO statistics,
  so each of their last three seasons is matched to the five nearest imports
  since 2017-18 (role, age, production, with a penalty across leagues;
  returning imports, minor-league deals, and Ohtani's two-way case excluded)
  and the row carries what those players actually produced per season over
  their first two MLB seasons, on the Ledger's WAR scale. The standard
  projection then runs on that row like any other.
- They are priced off the posted market itself (the comps' guarantees,
  inflated to 2027 dollars), with published predictions shown beside the
  Ledger's figure. The posting fee (20% of the first $25M guaranteed, 17.5%
  of the next $25M, 15% beyond) is shown and charged in the simulator's
  surplus; it sits outside payroll, as it does in real life.
- Read the comps before the number: the import record is thin and mostly
  sobering (Yoshida, Tsutsugo, Akiyama, Kikuchi's first year), which is why
  a Triple Crown winner projects nearer two wins than five. That is the
  history, not a scouting opinion.

Org prospects (`engine/prospects_build.py`, `data/pros.json`)
- MLB Pipeline's team Top 30 lists are offline between seasons, so the
  Ledger prices org depth from the minor-league record. Calibration: every
  affiliated Single-A to Triple-A season 2014-2019, each player placed at his
  highest level with a real sample (120 PA / 30 IP), scored by age against
  the level and production against the level-season mean, bucketed level x
  age band x tercile, shrunk to the level mean (n / (n + 40)). Outcome: the
  player's actual Ledger WAR over the next six seasons (the span the Top 100
  rank curve prices) and in the next season alone. Prior MLB players and
  that winter's Top 100 are excluded.
- Each club carries its 25 best by that expectation, about 680 prospects in
  all beyond the Top 100. They trade on the board at that value, move between
  farms when a deal executes (and back on undo), and can be promoted onto the
  2027 depth chart at their rookie-year expectation. Top 100 prospects get the
  same rookie-year treatment by rank band and 2026 level (a top-25 prospect
  who reached Triple-A: +1.1 the next season, counting those who never got
  the call).
- Calibration headline: a young, top-tercile Triple-A hitter is worth about
  2.6 wins over six seasons, roughly a #75-#80 Top 100 prospect; an old-for-
  the-level Double-A arm is worth under 0.1.

Regression suite: `tests/t_winter.mjs`.


## v5.3 (November 2, 2026): prospect peak projections (Phase II)

Every prospect now carries a peak projection from a self-built system that
follows the frameworks the public projection systems describe (ZiPS-style
weighted seasons, Davenport/ZiPS-style minor-league translations, and the
comparables idea behind long-term projections), on MLB Stats API data only.
No outside projection numbers are used or shown. Code: `engine/prospects_peak.py`.

1. Translations. Each minor-league component is expressed relative to its
   level-season average (so run environment and ball changes wash out), then
   carried up the ladder (A, A+, AA, AAA, MLB) by level factors learned from
   every player who played at two adjacent levels in the same season,
   weighted by the smaller sample. Hitters: strikeout rate, walk rate,
   isolated power, BABIP, steals per time on base. Pitchers: strikeout rate,
   walk rate, home runs per batter faced. Same-season pairs carry promotion
   bias (players promoted after a hot stretch), so the factors are used only
   to place players at different levels on one scale for matching; the
   outcome always comes from real careers.
2. Weighting. The current season counts 5, the prior season 3.
3. Comparables. Each prospect is matched to his 100 nearest 2012-2019
   prospect-seasons (one per player) on age, age against level, level,
   the translated rates, position group (catcher, premium defensive spot,
   corner), and pedigree (draft slot and Top 100 rank at the time).
4. What the comps became. PEAK = the average of a comp's two best MLB
   seasons of Ledger WAR within eight years, misses counted as zero, so
   bust risk is inside the number; with it, the odds of a 2-win and a
   4-win peak, an upside figure (80th percentile), next-season WAR (used
   for depth-chart call-ups), and six-season WAR (the trade currency).
5. Backtest, leave one cohort out, 2013-2019 (19,843 prospect-seasons):
   - Prospects outside the Top 100: comps r = 0.249 against
     realized six-season WAR, versus 0.181 for the
     level-and-age buckets. The comps model now prices them.
   - Top 100 prospects (706): rank curve r = 0.328, comps
     r = 0.307. Scouting rank still knows more than the stat line
     for elite prospects, so Top 100 value stays on the rank curve (the same
     curve the development grade uses); the peak projection is shown beside it.
   - Peak: r = 0.482. Of the model's top 5% each cohort,
     28% reached a 2-win peak, against a
     4% base rate.
   Read the r values in context: most prospect-seasons end at zero MLB value,
   which caps any correlation; the hit-rate lift is the clearer signal.

Where it shows: the trade board and Deal Desk farm lists, the depth chart's
call-ups, and every prospect's Deal Desk projection line (peak, odds, upside,
and his four nearest comps with what they became).

### v5.3.1 (same day): the low minors, discounting, and the Top 100 tests

- Rookie ball (complex leagues and the DSL) and pre-2021 short-season A are
  now in the translations and the comparables pool (34,825 prospect-seasons
  in the backtest, up from 19,843). Complex-league clubs not in the
  affiliate table are mapped to their parent by name.
- Six-season value is now discounted 10% a year, the units of every surplus
  figure in the simulator and of the Top 100 rank curve (the curve's average
  for ranked prospects, 3.04, now matches the comps' discounted figure,
  3.04). The v5.2 org tier was undiscounted and ran about 35% rich against
  the rank curve.
- Backtest after the change: outside the Top 100, comps r = 0.258 vs
  0.192 for buckets; of the model's top 5% each cohort,
  22% reached a 2-win peak against a 2.8% base rate.
- Two ideas for the Top 100 were tested and NOT adopted. A level adjustment
  to the rank curve (a ranked prospect already in Triple-A delivers more
  inside six seasons: factors {'low': 0.85, 'mid': 0.94, 'AAA': 1.17}) looked better in
  sample but scored r = 0.334 with each cohort held out, versus
  0.336 for the plain curve. A 30/70 comps/rank blend scored about
  0.34 versus 0.336: inside the noise. Top 100 value stays on the rank curve.
- Each club's list is its 25 best by value plus its 10 highest ceilings not
  already in, so high-upside teenagers in the low minors (who price low on six
  discounted seasons) are on the board to be asked for.

### v5.3.2 (same day): every tree ends where the player stands today

- The last club of a player's final season is now the club he finished
  with. The fate table took the FIRST club listed for that season, so
  anyone traded in-season ended on the wrong club (Clay Holmes read NYM
  after his August trade to the Cubs; Tyrone Taylor "left without a graded
  move").
- Minor-league deals are moves on the ledger, and a contract selection that
  follows one is shown (Morel: released by Miami, minor-league deal with the
  Mets in July, selected in August). Each player keeps his 24 most recent
  moves (it was the 14 oldest).
- Every chain ending and every trade piece now says where he stands this
  winter, from the same data the simulator uses: a free agent (and how:
  filed, declined option, opted out), likely a free agent (an open
  decision), under contract and through when, under club control
  (pre-arbitration or arbitration-eligible), a prospect in a named system
  with his rank or org slot and level, posted, or retired. Holmes now ends
  "Finished 2026 with CHC; now a free agent (declined his $12M player
  option)"; Jefferson Rojas, "now a prospect in the NYM system (#64, AA)".
- Audit: all 1,006 players active in 2026 resolve to the same club on the
  trees as in the simulator; no tree renders empty or broken text.

## v5.4 (November 2, 2026): the public-launch pass

A fresh-eyes review of every tab, then fixes to the data and the copy. Each
item below changed a number or a sentence a reader would see.

**Grades and regime windows**
- Seat time is measured in real seasons (`engine/regime_window.py`): a hire
  or dismissal in mid-season holds the seat for that fraction of the season;
  the W-L record counts games from the hire date (schedule API), and
  division titles and October belong to whoever held the seat when the
  season ended.
- Evidence floor: a channel needs a minimum number of decisions to be graded
  (3 for draft, trade, waiver, free agency, international, retention; 2 for
  extensions); below it the cell reads "·" and the overall rating counts that
  channel at the league-average rate. Per-season rates divide by at least 3
  seasons, so a one-season regime cannot ride one lucky move to an A.
  Regimes in the seat under a quarter season (the A's Taylor Smith, the
  Astros' Randy Flores) show as "new" and are not graded or ranked.
- Regime changes since v5.3: Taylor Smith (ATH, Oct 19), Randy Flores (HOU,
  Oct 30); David Forst and Dana Brown move to the archive (112 regimes).
- Ages use the June 30 season-age convention throughout.

**Contracts**
- Extensions signed in spring that cover the current season now start in
  that season (Acuña, Albies, Merrill, Crawford, Hayes, Reynolds, Greene,
  Griffin, both Ramírez deals); Glasnow's and Altuve's add-on years start the
  following season. Willson Contreras's St. Louis deal moves from the
  extension list to the free-agent book, where it belonged. The book is now
  1,620 free-agent deals and 83 extensions, plus 32 contracts on file for 2027.
- A player whose current contract is a free-agent deal (Senga, the posted
  imports) reaches free agency when it ends; the Horizon salary book no
  longer invents arbitration years after it.
- Qualifying-offer charges added for Nick Pivetta and Luis Severino (2024-25).

**Trades**
- Three-team deals filed as separate one-way legs are joined into one deal
  for every seat when the other two clubs also traded that day (the 2014
  Myers deal, the 2025 Lowe/Burrows deal). A "player to be named later"
  completion joins the deal that promised him (Trea Turner joins the Myers
  deal; graded alone he read as a 25-win giveaway). 159 deals merged.
- The curated Orioles and Brewers cards and the Ortiz chain now carry the
  engine's current numbers. The Burnes trade, read as a fair price through
  2025 (+1.2 for Baltimore on the leverage lens), now reads −7.1 after
  Ortiz's 2026; the methodology says so instead of keeping the old verdict.

**Scenario Room**
- No future data: offseason scenarios no longer show the coming season as
  "this season". The Ramírez extension is set in spring 2017 and priced
  against the extension market (projection × years × $/win × the
  pre-arbitration discount), not free agency. The Greinke deal includes
  Jake Odorizzi; the Betts package text matches the real package. Pre-2006
  scenarios use the first year of the $/win history. The assistant GM's lean
  now follows the same market read the grade uses, from the seller's seat too.

**Simulator, Desk, Horizon**
- Simulator: open negotiations pinned at the top, position/roster/farm
  filters and sorts on every board, a Call-ups step, a shareable depth-chart
  image, and Start over. Desk: pickers list only the two clubs' players and
  farms, send on the left, receive on the right, and an acceptance check.
  Horizon: a league table of projected wins 2027-2031 with prospects'
  season-by-season value included, and payroll figures that close to the
  salary book. Offseason comps count trades from the full trade book through
  the 2025-26 winter.

**Copy**
- Every +/- is explained (leaderboard legend, a one-minute guide atop
  Methodology); "LVM" is gone from the page; plural forms are correct;
  extension dates show the signing month; draft decisions carry the real
  draft date; champion names and abbreviations are era-correct (2003 Florida
  Marlins, 2002 Anaheim Angels); an About note states the site is
  independent and unaffiliated with MLB or any club.

Tests: `tests/t_launch.mjs` (new) covers each item above.

## v5.5 (November 2, 2026): one asset, one entry

**Draft and international signings are graded as assets** (`engine/asset_rules.py`).
A pick is worth what the player produced in his six control seasons (debut
season plus five), wherever he played them. If the club trades him, the trade
channel charges what he produced for his new club and credits what came
back; the two entries net to what the club turned the pick into. Before, the
draft only counted seasons with the drafting club, so a traded draftee read
as a draft miss and a trade loss at once (CJ Abrams and MacKenzie Gore were
charged twice to San Diego), and a homegrown star's extension years were
credited to the draft as well as graded, net of cost, in the extension
channel. Both are gone.

The slot expectation is re-calibrated on the new definition: across every
round 1-5 pick of 1998-2016, control-season value ran 1.309 times the slot
curve, and the share realized N years after the draft is fit on all classes
(0.12 at two years, 0.47 at five, 0.80 at seven, full at ten). Pooled across
classes the league's draft net is about zero (ratio 0.985). Preller's draft
channel moves from a deep negative to −0.1 (C+); his trades still carry the
cost of trading those players away. International signings use the same
six-season definition, and their class baseline is recomputed on it.

**Every trade, every move graded against moves of its size.** Report cards
list every trade in the tenure from the trade book, sortable, beside the five
best and worst, and the channel's grade is stated once per channel rather
than stamped on the "best" lists. Each decision carries its own letter, and
the letter is relative to expectation for that kind and size of move: every
decision the engines graded (all clubs and regimes; trades from both seats of
the full trade book) is split into stake bands, where the stake is what the
move put at risk in wins (contract cost for signings and extensions, slot
expectation for picks, the larger side of a trade). Within its band a move's
letter is its percentile: F bottom 10%, D to 30%, C the middle 40%, B to 90%,
A to 97.5%, A+ above. A $4.5M signing that returns three wins over its cost
(Craig Stammen) is an A+; the same three wins from a $300M deal would be
middling. Waiver moves and international signings, which carry no comparable
price, are ranked within their channel as a whole.

**Contract projections recalibrated.** Grading the Ledger offer by the size of
the offer (not the size of the real contract) showed the problem a reader
would notice: when it offered $50M or more, the real contract came in at a
median 80% of the offer, about a year shorter, and $200M+ offers ran 2.7 years
long. Four rule changes, each tested on all 1,197 signings 2010-2025 with only
the information available that winter: no extra "spread" years for stars; no
convex premium for elite seasons; the model never weighs more than 60%
against the market comps; comps from recent winters count as more similar
(0.05 per winter of distance); and regulars take the 30th-percentile comp term
rather than the median. Result: the median real contract is now 92% of a $50M+
offer (years 0.6 long), and the overall miss is 0.69 years / $3.2M AAV /
$13.9M total (was $14.5M). Against this winter's published predictions the
headline numbers now sit in the same range (Skubal 7 years / $348M); the
players where the Ledger still differs most are the ones Ledger WAR rates
differently from the public (Brandon Lowe's 5.7-WAR 2026, Luis Arraez), and
the Big Board shows each player's last three Ledger WAR seasons so the reason
is visible.

**Trees.** A browsable player finder (scroll the full ledger, alphabetical by
last name), the Soto chain as a showcase (Abrams, Gore, Wood, Hassell and
Susana to Soto; Soto to King and Thorpe; Thorpe to Cease), and a "still
expected" line on open branches: the Ledger Projection over remaining control
for major leaguers, comparables' six-season value for prospects.

**Big Boards (new tab, "Look ahead").** Three rankings from the models the
Simulator and Desk already use, each with its backtest stated on the page:
the 2026-27 free-agent class by projected 2027 WAR with the Ledger offer
(years and dollars, a likely range equal to the backtest's typical miss of
about $3.2M a year, and posting fees for posted players); the top 100
prospects by Ledger value (six-season discounted WAR: rank curve for ranked
prospects, comparables for everyone else) with the comparables' peak and
4-win odds; and farm systems ranked on their ten most valuable prospects,
with the full total, Top 100 count, and Double-A/Triple-A share. Ranks now
come from the current (2026) Pipeline list only; a 2025 rank had outlived
Kristian Campbell's graduation.

**The pitch.** The site now says what it is in the masthead, the intro, and
the share cards: a decision-making model that grades every move since 1998
and prices the moves still to be made.

**Copy.** Every "lev-adj" on the site explains itself on hover or tap; the nav
drops its redundant labels; the beta tag reads "built entirely from public
data"; and the validation section opens with "Evaluating the evaluators."

Validation after the change: partial r 0.265 (95% CI 0.16 to 0.38) across 575
regime-years from 112 regimes; out-of-sample R² 0.177 to 0.230.

## v5.6 (November 2, 2026): the market model, and every international signing

**International volume.** The international channel counted only signees who
had reached the majors, so a club whose recent classes have not debuted (or,
like Atlanta 2018-21, signed under MLB sanctions) showed one or two signings
and no grade. It now counts every international amateur signing in the feed
(13,502 classified, 497 of whom have produced MLB value); the expectation was
always the league's class value over 30 clubs, so only the volume and the
grade's evidence floor change. Anthopoulos now carries a graded channel (199
signings, D+), with the sanctions noted on the card: in November 2017 MLB
released 13 Atlanta signees, capped the club's signings at $10,000 for
2019-20 and halved its 2020-21 pool, for the previous front office's
violations.

**A second, independent read on every contract** (`engine/contract_model.py`,
`engine/stats_fetch.py`). A gradient-boosted model is trained on 1,581 real
free-agent contracts (2006-2025 winters) using the player's last three
seasons as the market saw them, from the public box score (PA, OBP, SLG, HR,
SB, strikeouts for hitters; IP, starts, ERA, K-BB%, HR rate, saves for
pitchers), plus Ledger WAR, age, and position. It predicts AAV in wins and
years. The Ledger offer is now the geometric mean of the two AAVs (rules and
market model) and the average of the two terms, moved to today's market:
contracts in the 2021-25 winters ran 16% above the published $/win curve
(median over 92 deals the model priced at $25M or more, which keeps the
estimate free of the bias that comes from looking only at big real deals).

Walk-forward backtest, every winter 2012-2025 predicted only from earlier
ones (1,029 signings): typical miss 0.66 years / $3.0M AAV / $13.6M total
(rules alone 0.74 / $3.5M / $15.2M); offers of $50M or more land at a median
97% of the real contract (rules alone 91%). Two ideas tested and rejected on
the same backtest: dropping Ledger WAR from the market model (worse: it
carries information the box score lacks), and anchoring to a player's
previous one- or two-year deal (no gain on 175 such cases).

A data fix found on the way: the league's year-by-year feed returns a traded
player's season once per club plus a combined row, and the playing-time
pull (`engine/pt_fetch.py`) summed all of them, doubling traded players'
plate appearances and innings (Luis Arraez's 2024 read 1,344 PA). Both pulls
now use the combined row alone; durability factors were recomputed.

**Where it still disagrees with the public.** Against Baseball America's
published predictions for this winter's top 42 non-posted free agents the
median miss is 0.50 in log terms (v5.4: 0.69) and the median ratio 0.91.
The largest remaining gaps are players Ledger WAR rates far above the public
consensus, Brandon Lowe (5.7 in 2026) and Luis Arraez (4.4, after the market
paid him one year and $12M last winter); the open question there is the
metric's defensive and positional credit, not the pricing.

## v5.7 (November 2, 2026): positional credit, salary in trades, full lists, process-only scenarios

**Positional credit by games played.** Ledger WAR v1.6 weights the positional
adjustment by the games a player actually played at each position each
season (the league's fielding splits; a traded player's combined row),
replacing the single listed position applied to every season. Luis Arraez's
2024 and 2025 move from 3.2 and 3.0 to 1.6 and 1.3 (he played first base and
DH, not second); Jose Altuve's 2025 from 3.2 to 2.2; designated hitters and
late-career first basemen (Mauer, Rodriguez, Ohtani's hitting) drop, and
catchers and center fielders who were listed elsewhere gain. Brandon Lowe's
2026 holds near 5.5: his Statcast fielding swung from -11 runs in 2025 to +11
in 2026, and that is real. Rebuilt for 28,403 players (`engine/lvm_v16_rebuild.py`).
Validation after the rebuild: accounting r 0.865 (R² 0.749, MAE 5.34);
predictive partial r 0.26 (95% CI 0.15 to 0.38), out-of-sample R² 0.177 to
0.227 across 575 regime-years. Prospect peak backtest: all comps r 0.45.

**Trades net of salary.** A traded player's value to the acquiring club is
now his production minus the guaranteed salary that came with him: each
season with the club is charged the contract's AAV above the league minimum,
in wins at that season's $/win (`engine/asset_rules.contract_cost`). The
selling side is relieved of the same amount, so the trade stays zero-sum.
Where a public report gives the cash sent by season, the acquiring club is
charged what it actually paid (`NET_PAID`; first entry: Nolan Arenado to
Arizona, Jan 13 2026, St. Louis sending $22M toward his $27M 2026 salary and
$9M toward 2027). Arbitration salaries and cash without a published
per-season figure are not yet charged. Arenado's deal reads about +6 for
Arizona: 3.9 Ledger WAR in 2026 (30 HR, .331 OBP, .475 SLG) at a $5M cost,
while the return has no MLB value yet. The prospect side is an open branch.

**Every decision listed.** Report cards now carry full, sortable lists for
every channel: every draft pick (expected vs produced, wherever he played),
every major-league free-agent signing (terms, cost in wins, produced here;
signings whose terms are not in the contract book are listed, not priced),
every extension, every international signing that reached value, every
waiver and Rule 5 move in both directions, and every free agent who walked.

**Why so many "partial" badges, and the fix.** A channel letter needs
evidence: 3 priced free-agent deals, 2 extensions. The contract book was deep
for the 2006-21 winters (about 90-110 major-league deals each) but held only
about 30 curated majors per winter for 2022-25, so regimes hired since 2022
often lacked a free-agent or extension letter. The free-agent evidence floor
drops from 8 deals to 3, and the book is now complete for those winters (next
paragraph). Partial badges on the current leaderboard fell from 15 to 11, and
most of the rest are regimes with one or two seasons in the chair.

**The full contract book (same day).** The 2022-25 free-agent book now holds
every guaranteed major-league deal: 560 signings (137, 137, 140 and 146 by
winter), built from MLB Trade Rumors' team-by-team Offseason in Review posts
and cross-checked against NBC, MLB.com, ESPN, Fox, CBS and AP. Guaranteed
totals include buyouts; accepted qualifying offers count as one-year
re-signings; split and minor-league deals are excluded. All 129 previously
curated deals reappear, two differing by a buyout. The extension book adds
203 deals from 2015-2026 (MLB Trade Rumors' extension tracker through July
2022, then deal-by-deal reports), for 286 in all; curated rows win where the
two disagree. A deal signed through March covers that season; April-June
covers it for players within three seasons of debut; otherwise the next.
Milwaukee under Matt Arnold goes from 2 priced signings to 16 (free agency
graded D) and from 2 extensions to 3 (graded C).

The fuller book moves the contract model. Walk-forward backtest on 1,439
signings 2012-2025: typical miss 0.54 years / $2.8M AAV / $10.5M total (rules
alone $12.2M); offers of $50M or more land at a median 97% of the real deal.
Rules alone, 1,607 signings 2010-2025: 0.57 years / $3.0M AAV / $11.4M. The
market drift (median real contract over the ensemble price, 2021-25 deals it
priced at $25M or more) falls from 14% to 8% on 106 deals; the 2024 and 2025
winters alone ran 38% above it, but with a 95% interval of 0.93 to 1.65 on 48
deals, too noisy to adopt yet. Against Baseball America's predictions for
this winter the median miss is now 0.50 in log terms with a median ratio of
0.95 (the lower drift is most of the change).

**Scenario Room: process only.** The archive plays blind (names, club,
executive and date revealed after the decision), and the grade is process
alone: the price against that day's market, adjusted for the seat (a
rebuilding club giving a 31-year-old 4+ years: -20; a club out of the race
buying a rental: -25; a contender paying a fair price at a need: +10).
Outcomes are shown as hindsight and never graded. A Winter 2027 pack is
generated from the live data: the class's top free agents offered to the
clubs whose depth charts need them most, three extension candidates, and
three controllable stars on rebuilding clubs, priced by the market model at
asks above, at and below it.

**Assistant GM fits.** Recommendations must be natural fits for the hole (no
starter for a bullpen hole), are ranked by the gain to the whole depth chart
after re-slotting, and charge a fielder used at DH for the glove and
positional credit he loses (0.4 wins for a first baseman, 0.8-0.9 for a
corner outfielder, 1.2-1.5 for an infielder, 1.3 for a catcher or center
fielder). Rebuilding clubs are shown players 29 or younger; fringe clubs 32
or younger.

Tests: `tests/t_consistency.mjs` (v5.7 block).

**Contract offers (same day).** Every offer, ask and comparable now states
its average annual value. Position still helps pick comparables but no
longer decides them (the penalty for a different position group drops from
1.2 to 0.4 in the match score; the walk-forward backtest that sets the rules
uses no position term at all). The market model underprices regular
catchers: in its walk-forward backtest, catchers signed for $5M or more
landed 0.27 log points further above its price than other players (n=39),
so half of that gap is applied (x1.3) to catchers with a blended platform of
1.5 wins or more. Against Baseball America's predictions for this winter's
top 45 free agents the median miss moved from 0.47 to 0.41 in log terms
before the full-book refit (see above). Ryan Jeffers prices at 2 years / $32M
($16.0M AAV) after the refit; the remaining gap to the public consensus (about four years)
is term: his 2026 was 92 games (fractured hamate), and catchers his age with
his blended platform have historically signed for two years.

**Graded against expectation and investment (same day).** Free agency was
graded against zero: a signing "broke even" only if the player produced every
win his salary bought at market $/win. Across 1,940 priced major-league
signings by every club since the 2005-06 winter, the typical club got back
0.704 wins per win of cost (the winner's curse: the club that wins an auction
is usually the one that rated the player highest). Each signing's expectation
is now its cost times that typical return, so the expectation scales with the
money; extensions get the same treatment against their service-class market
(typical return 0.971 over 269 priced extensions). Draft, trades, waivers,
international signings and retention were already measured against an
expectation (slot value, zero-sum trades, class baselines, conditioned
departures). Effect on the current leaderboard: free-agency letters spread
from mostly D/F to a D-to-A range (Yankees under Cashman: -83.9 to +20.4
wins; Dodgers: -29.5 to +21.3); validation is unchanged (partial r 0.26,
95% CI 0.15 to 0.38; out-of-sample R² 0.177 to 0.227). The Deal Desk and the
Offseason Simulator now letter every proposed move by its percentile among
real moves of the same kind and size, against the same typical returns; the
simulator's winter letter is the money-weighted percentile of its moves.

## v5.8 (November 2, 2026): the pre-public audit

Four independent reviews (facts, engine math, the page, the forward-looking
tools) read the site and the code before wider promotion. What they found and
what changed:

**One contract book, one ownership rule (`engine/contract_book.py`).** Every
guaranteed contract the ledger knows now lives in one table resolved to
player ids: free-agent deals from the 1997-98 winter on (2,766; the 1997-2005
winters from news and ESPN lists, research file `data/research/fa_1997_2005.csv`)
and extensions from 1998 on (806; `data/research/ext_1998_2014.csv` adds 532).
A later contract owns its seasons. That one rule removed three double counts
the math review measured: trade windows running into the acquiring club's own
later extension or re-signing (79 cases, 239.6 WAR; Mookie Betts's 2021-25
counted in the 2020 trade and again in his extension), draft and
international control years running into graded extension seasons (19
players, 113.9 WAR), and free-agent deals overlapping the extension that
replaced them (Manny Machado 2023-26). Four extension start seasons were a
year early (Altuve, Sale, Goldschmidt, Verlander) and are fixed.

**Draft calibration.** With control years capped where a later contract
begins, round 1-5 picks 1998-2016 produced 1.058x the slot curve (1.305x
uncapped), and the maturity shape was refit on the same pool.

**Traded players are assets.** The acquiring club is credited with the
player's control window wherever he plays it (a quick flip is graded in the
flip), ending at a new contract, a free-agent filing or a release; in the
trade season, what he produced after leaving the sending club. Before, a flip
left the original seller charged nothing (Mike Piazza's May 1998 trade read
as a +30 win for the Dodgers). Multi-team deals filed as separate
transactions are linked when the same player moves between the clubs within
three days.

**One money unit.** Salary that moves in a trade is charged at what that money
typically buys in free agency: salary above the minimum, at that season's
$/win, times the typical free-agent return (0.87). Taking on a typical
contract is neutral and dumping one is not free money. Reported cash by
season: Arenado to Arizona (2026), David Price to Los Angeles (2020).

**Free agency graded by contract year.** A season of a free-agent deal returned
1.06 wins per win of cost in year one, 0.80 in year two, 0.74, 0.69 and 0.50
from year five (2006-26 seasons, every priced deal by every club). A deal is
graded only for the seasons the signing club held it: a trade passes the rest
to the trade ledger; a release keeps the dead money. Seasons before 2006 use
$/win scaled from MLB's average payroll and their own era's typical return
(1.52x the curve, partly because the 1997-2005 lists over-represent big
deals). Extensions: 1.30 in year one down to 0.87 from year five, against the
service-class market. Nov-Dec re-signings now match that winter's deal, not
the previous one.

**Waivers before 2009.** The feed filed only the claiming side; the losing side
is now added from the claim, so the channel is two-sided in every era.

**International.** The expectation counts only league signings dated on or after
a regime's start (a regime hired in October is no longer charged for the July
class it could not sign); single signings are graded against their class's
average signee; a letter needs a class at least five seasons old.

**Evidence floors and the composite.** A channel letter needs priced decisions
with an expectation (matured picks, extensions with seasons played). A
channel too thin to grade counts at its expectation, zero (before, the
leaderboard filled it with a positive league average, about +1.4 wins a
season across channels).

**Validation, corrected.** The predictive check let seasons produced after each
date leak into the predictor (a trade's later seasons predicting the wins
they produced). Rebuilt on value as realized by each season, and run after the
archive scorer: partial r 0.11, 95% CI -0.01 to 0.27, out-of-sample R² 0.187
without decision value and 0.174 with it. The grades measure decisions
against expectation; they are not by themselves a forecast of next year's
standings. The page says so.

**Projections.** Rate times playing time: WAR per PA or IP over 2024-26 weighted
5/4/3 and regressed by sample size toward the role's league rate, times
expected playing time (60% the two fullest recent seasons, 40% the weighted
line with missed seasons at zero, capped at a full season). Missed time is no
longer counted twice; two seasons without MLB time means no projection.

**Contract offers.** One big platform year (3+ wins and 1.5x either prior
season) prices off the weighted three-year line in the rules (backtest on 61
such signings: bias +4.3 to +0.5) and the blended offer is cut to the
historical outcome for that group (median 0.89 of the offer, 0.27 years
shorter, 48 signings). A player who declined a player option is priced at
least at it. Brandon Lowe 4/$124M becomes 3/$83M; Luis Arraez 3/$53M becomes
2/$31M.

**Forward tools.** The assistant GM never recommends a qualifying offer the CBA
forbids (Skubal, Gausman, Griffin and Gray were the cases; Gallen's 2025 QO
is now recorded), names the actual hole, never says to go past our number for
a player under a win or 34 and older, filters targets by payroll capacity,
reads posture from 2026 wins and the 2027 roster together, and counts
deferred deals at CBT value for the tax note. Deal Desk trades grade on
surplus net of salary, leverage on near-term big-league value only; invalid
inputs are refused; only a player's own club can extend him. The 2026 draft
class (98 signed top-100 picks, MLB Stats API) joins the prospect and farm
boards at draft-slot value discounted three years.

**Facts.** Pujols 10/$240M (was $250M); Max Muncy signed with the Dodgers in
April 2017 (was 2015); deadline scenario records are the morning of the deal;
Billy Beane ran the Athletics through November 2022 (Forst from then); the
2020-21 Mets front office (Sandy Alderson) is in the archive; the Padres' 2011
handoff is dated October; Cooper Pratt 8/$50.75M; Contreras's option $14.5M;
championship medians 56/46/72%.

---

## v5.9: the adversarial review (November 2, 2026)

Three reviewers were asked to break the site before launch: a skeptical analyst on facts, a hostile QA engineer on the page, and a sabermetrician on the method. Their reports (about 70 findings) and the evidence scripts are in the working audit folder; every finding below is fixed unless marked otherwise.

### Engine (method)

1. **Extensions and the ownership rule.** v5.8 let any later contract own its seasons, so when an acquiring club extended a traded player, the trade lost his remaining controlled seasons and the seller was never charged for them (83 pieces, 228 wins); under archive regimes the extension seasons were graded by no channel (147 pieces, 334 wins). The Cabrera trade read DET -13.1. Fix: an extension owns only the seasons beyond the player's original club control. Inside control the acquiring decision keeps the value; the extension channel grades the salary it set there against the arbitration path it replaced, and the free-agent seasons it bought against a typical free-agent return. Each service class is centered on the league's average result per win of cost (the old fixed class discounts left early extensions at 1.39x expectation and veteran ones at 0.84x). Cabrera now reads DET -2.9 in the trade (two controlled seasons net of arbitration salary, against Maybin, Miller and Badenhop) and +27.3 in Dombrowski's 2008 extension.
2. **Club control is dated.** Control runs six years of service from the MLB debut (debut dates from the MLB Stats API, `debut_fetch.py`): a debut after April 15 runs control through the sixth season after the debut season. Options and Super Two are not modeled. The draft and international windows use the same span.
3. **Leverage removed from grades.** The win-curve weight was applied at the club where the wins were produced, so the seller was charged at the buyer's leverage: seats on clubs under 72 wins netted -375 wins with it and +33 without. Grades are unweighted (`asset_rules.USE_LEVERAGE = False`); the forward tools keep leverage for the club making the decision.
4. **Open trades.** A prospect with no MLB season before the deal carries his expected value (the rank curve at the time of the deal x 1.077, or 0.489 wins unranked, both fit on 2011-2018 trades in `trade_calib.py`) times the share not yet realized (by seasons since the deal: 0.03, 0.16, 0.30, 0.47, 0.65, 0.79, 0.90, 0.96, ...). The value-time series and the validation use realized value only.
5. **Draft centered by class.** With control dated from the debut and no extension cutoff, the pooled scale is 1.50 and the shape is re-fit on the matured 1998-2013 classes; each class has its own scale (league realized / slot x shape), shrunk toward the pool by 40 wins of expectation (`draft_calib.py`). Draft credit ends at a release or free-agent filing anywhere (before, the drafting club kept credit for production after it released the player).
6. **Trade windows run to the end of control**, so a prospect traded years before his debut is charged to the trade for his late control seasons (187.6 wins had been credited to the drafting club and charged to no one). October-December deals start with the next season.
7. **Money in one unit, by contract year and size.** Free-agent typical return is fit by contract year and by deal size (cost per season under 0.5 wins: 2.02x the year curve; 0.5-1.5: 0.94x; 1.5-3: 0.86x; 3+: 1.02x). Trade and waiver salary relief uses the moved contract's own year and size, so dumping the late years of a deal is neutral in expectation (A-Rod to Texas had been a +8.3 windfall). Posting fees are charged as year-one money in free agency.
8. **Arbitration salaries charged** in trades and waiver claims for arbitration seasons with no contract: (0.6 + basis) x step (1.0/1.5/3.1) x the $/win drift, the Desk's calibrated model. Rough for stars (it runs low), disclosed.
9. **Archive regimes graded on free agency and extensions** (`fa_grade.py`, `ext_grade.py` now run over `hist_results.json`). The salary relief archive regimes were credited for dumping their own signings is now matched by the charge for signing them.
10. **Waivers.** A claim moves the contract (Alex Rios to the White Sox, 2009: Toronto is no longer charged his extension); the four-season window stops at a later contract, a release or a filing, net of salary.
11. **Retention.** Expectation conditioned on age (multipliers 1.27 / 1.04 / 0.91 / 0.51 for 29 and under, 30-32, 33-35, 36+); deadline rentals who walk are excluded (the trade's window already ends at the filing).
12. **Qualifying offers.** The QO table held 51 of the QO signings since 2012. It is now complete for the 2012-13 through 2025-26 offseasons: 98 players who declined a QO and signed with a new club (MLB.com's QO decision history), excluding signings after that June's draft (Kendrys Morales 2014, Craig Kimbrel and Dallas Keuchel 2019), which forfeited no pick. Three missing contracts were added to the book (Kyle Lohse MIL 2013, Ervin Santana ATL 2014, Greg Holland STL 2018). The 1-win charge on the signing club and the 1-win credit to the losing club are on. Ryu 2019 and Gausman 2021 were wrongly listed (both had accepted a QO the year before and could not receive another) and are out. Pre-2012 Type A/B compensation is not modeled.
13. **Development.** A player drafted twice keeps his last (signed) pick; NPB pros (Ohtani, Sasaki) enter at their rank value with no development credit.
14. **Attribution.** Mozeliak's St. Louis start is his promotion (Oct 31, 2007). Interim GMs who traded are their own regimes: Lasorda (LAD 1998), Kullman/Maddox (CIN 2003), Pelekoudas (SEA 2008), Dipoto (ARI 2010), Minaya/Hinch/Uhlman (SD 2014), Stoneman (LAA 2015), Antony (MIN 2016), Minaya/Ricciardi/Ricco (NYM 2018), DeBartolo (WSH 2025).
15. **Feed repairs.** Rule 5 conduits (a pick traded within three days, e.g. Johan Santana 1999) are re-filed on the club that kept the player (`r5_conduit.py`); the Cliff Lee (2009-07-29) and Victor Martinez (2009-07-31) returns are added to `trade_repairs.json`.
16. **Grading curve.** A rate is net / (seasons + 2) (shrinkage toward average), and each channel's letter reads that rate in units of the channel's spread across every graded regime, on one z scale (A+ from 1.65, A 1.2, A- 0.85, B+ 0.55, B 0.3, B- 0.12, C within 0.12, C- to -0.4, D to -0.85, D- to -1.65, F below). The composite uses the same scale on its own spread. Free agency and extension nets count in the composite whenever a deal was priced (their seasons are graded nowhere else); letters still need three and two priced deals.
17. **Success.** The division-title bonus is a rate (titles per season in the seat).
18. **Head to head.** A club with two seats in one linked deal keeps both.
19. **Reliability, published.** Split-half correlation of each channel's decisions across regimes: free agency 0.28 (90 regimes), extensions 0.11 (54), trades -0.11 (131), draft -0.11 (128), waivers -0.01 (118). The letters are an accounting of results, not a skill estimate; the page says so.
20. **Validation.** The predictor now includes free agency and extensions in the season their value arrived. Partial r 0.107, cluster-bootstrap 95% CI [-0.02, 0.28], out-of-sample R-squared 0.186 without it and 0.154 with it: no out-of-sample predictive gain. The launch article and the README no longer carry the 0.27 claim.

### Forward tools

- Projections carry age attrition from the second season (0.97 at 26 and under down to 0.78 at 36+, pitchers 0.06 lower), fit to the backtested 5-year overshoot (13% for hitters 22-24 up to 74% at 34-36). The market-price suggestion keeps the calibrated walk without attrition (it predicts what the market pays).
- Desk letters are pricing grades: the projected edge over a typical deal as a share of the cost (A+ 30% or better, A 18%, B 6%, C within 6%, D to -18%, F beyond). The percentile-among-realized-outcomes letter compressed 79% of offers 50% over the model's price into a C.
- The Desk free-agent and extension verdicts use the channels' own expectations (contract year, size band, class centering, arbitration path).
- The assistant GM prices the luxury tax (a repeat payer's 30% plus surcharges) into its budget test and its quotes.
- Scenario Room hindsight comes from the trade book.

### Page and data (facts and UI reviews)

Current clubs and statuses for every Desk player from the MLB Stats API (319 changed, restricted-list and retired players out, inactive 36+ veterans off the boards); one resolver for same-name contracts (Will Smith, Luis Lara, Chris Young, Luis Garcia, Alex Gonzalez, Roberto Hernandez); curated card numbers read the trade book; champions never guess an acquisition; era-correct club names on archive cards; prospect SP/RP from minor-league starts; Deal Desk and Simulator input bounds; no self-trades; accent-insensitive search; shareable URLs for every view; persisted theme and intro; one h1 and accessible names; Escape closes overlays; payroll chart covers multi-year winter deals; the analytics placeholder is gone. Regression checks: `tests/t_ui2.mjs`, `tests/t_consistency.mjs`.

### Extension salary schedule and open-deal projections (November 2, 2026)

**The problem.** Corbin Carroll's 8 yr / $111M extension read −2.4 after four seasons of 4-7 wins. In his controlled seasons the extension is graded on salary only (the production belongs to the draft pick that brought him), and the engine charged the deal's average salary ($13.9M) in every season, against a pre-arbitration path of the minimum. Real extensions are back-loaded, so every young player's extension read as a loss in its early years.

**The fix.** `asset_rules.ext_salary` spreads the guaranteed total over the contract's seasons in proportion to what each season would have cost on the path it replaced: 2x the minimum in pre-arbitration seasons, the arbitration award model for the player's level at signing (at least a 3-win regular) in arbitration seasons, and the average salary (never below his last arbitration season) in free-agent seasons. The schedule is fixed at signing. Carroll's comes out about $3M a season through 2025, $7.6M, $11.7M and $24.1M in arbitration, and $29.1M in 2029-30, close to the deal's actual structure. Every consumer of contract cost (the extension channel, trade salary charges, the Desk's extension verdict) uses it.

**Tried and dropped.** Centering each season on the league's extensions of the same class in the same contract year. With the schedule in place, the late-year rates came almost entirely from the 2008-2014 team-friendly early extensions that have reached their free-agent years, so they set an unreachable bar for today's deals (Carroll projected −2.7 against it). One rate per class, per win of cost, is kept.

**Projected finish.** Deals still running carry a projected final net (5/4/3 weighted WAR, regressed 20% toward 1.5, aged, with attrition; arbitration seasons priced on the projected prior season), shown in the decision and in the full extension list, never in a grade. Carroll: −0.5 so far, projected +2.7. Bobby Witt Jr.: +0.5, projected +21.7.

**Page.** Full lists open Best first (then Worst first, Newest first). The leaderboard's introduction and "How to read a row" key are bullets above the table. The Methodology page was rewritten around the grading math and whether it holds up, with charts: free-agent return by contract year, the draft slot curve, an extension's salary schedule, roster Ledger WAR against team wins (326 team-seasons), and split-half reliability by channel. Notes on how the tools work were removed from it.

**Validation fixes (same day).** The accounting check keyed team-seasons by club name: a few players carry the current "Athletics" label beside the full "Oakland Athletics" roster, and both matched the same standings row by suffix, so Oakland's 2015-21 seasons appeared twice (once as a 2-WAR roster against a 49-win record), while clubs whose names changed dropped out. Keyed by club id, all 330 team-seasons 2015-2025 are in: r 0.926 (was 0.865), R² 0.858, slope 0.915, mean miss 4.8 wins. The split-half reliability figures are now produced by `engine/reliability.py` on every refresh (regimes with at least six decisions in a channel): free agency 0.29 (109 regimes), extensions 0.17 (54), draft 0.09 (135), waivers 0.02 (133), trades −0.12 (138). Only free agency clears the noise band at these sample sizes.

### Public page cleanup, Deal Desk and simulator upgrades (November 2, 2026, evening)

**Kept here, removed from the public page.** The site no longer narrates its own version history. These notes live only in this file: trade value carried a win-curve leverage weight from v5.2 to v5.8 (removed in v5.9; seats on clubs under 72 wins netted −375 wins with it, +33 without); an earlier predictive check reported a partial correlation of 0.27 before the look-ahead leak was found (corrected value 0.11); the accounting check read 0.865 before team-seasons were keyed by club id (0.926 after); the adversarial-review fix list (see "v5.9: the adversarial review" above). Data-source detail on the page is reduced to the footer's required notices; the repository is no longer linked from the site.

**Leaderboard.** The composite is labeled **Overall** (formerly FOR, Front Office Rating) and leads the row, followed by net wins vs expectation; tenure moved into the regime cell. The net-wins bar places zero where the column's spread puts it (largest gain at the right edge, largest loss at the left) on a square-root scale, so one +100 regime no longer flattens every other bar.

**Curated trees.** In order: the Betts trade; Soto part 1 (San Diego, both deals from its seat); Soto part 2 (the Yankees' one-season rental, the pennant, the walk to the Mets); the three-team Murphy/Contreras deal (Milwaukee's seat, all three seats' trade-book nets in the subtitle); the Rays' Archer compounder (Archer → Glasnow, Meadows, Baz; Glasnow → Pepiot, DeLuca; Meadows → Paredes → Morel, Bigge, Johnson); the Ortiz chain; the O'Hearn scrap-heap compounder. Every value is read from the trade book at render time.

**Deal Desk.** No default club. Clubs are chosen with team-color chips (move type too); the trade screen is the simulator's three-column board (their roster and farm, the deal, your assets) with its find, show, position and sort filters. **Assistant GM: complete the deal** asks for the counterparty piece that best fills your weakest depth-chart slot when you have not asked for anyone, removes cornerstones a non-seller will not move, then adds the cheapest of your non-cornerstone assets that closes the gap to the counterparty's asking price (the same 1.5x contender and 1.75x franchise rules), or asks for one more piece when you are paying more than 1.35x their price. The extension tab takes the player's own club automatically.

**Offseason simulator.**
- *Who you are matters to a free agent.* A player's asking price is multiplied by 0.94 for a contender and 1.12 for a rebuilding club (club posture from the average of its 2026 record and its 2027 projection: 88+ contender, under 76 rebuilding), scaled by stardom (full effect at a 4-win 2027 projection, none for depth).
- *Assistant GM on the trade board,* the same completion logic on the simulator's own valuation (gmAskPieces / gmGiveVal).
- *The rest of the market.* At "Close the winter" every other club bids on the 90 best free agents you did not sign. Bid = Ledger market AAV x posture (contender 1.08, middle 0.97, rebuilding 0.86, or 0.72 for players 31+) x fit (1.15 if he fills a depth-chart hole, else 0.9) x window (1.05 if under 40% of its 2-win core is controlled through 2029) x a deterministic per-club read (0.94-1.06), normalized by 1.13 so the clearing price centers on the Ledger offer (median 0% in the PIT test winter). A bid must fit under the club's payroll room (capacity = max(1.3 x committed, $150M), the user's own rule). The player weighs who he would play for (stars take up to 6% less from contenders, ask 10% more from rebuilders), and the winner pays just over the runner-up's bid, never more than its own. No offer at 75% of his market leaves him unsigned (a minor-league deal or a wait into spring). Deterministic: the same winter always clears the same way.

### Hand-written cards retired; market comps on every move (November 2, 2026, night)

**Retired.** The hand-written showcase cards for the Dodgers, Orioles and Brewers (and their decision pages, lenses and notes) and the two hand-written championship cards (2025 Dodgers, 2023 Rangers) are gone. Those three clubs now carry the same computed card as the other 27 (the engine had been grading them all along; the hand pages rode on top), and every title card is the computed ledger. The Trees tab's featured trades stay: every value on them is read from the trade book at render time.

**Market comps beyond trades** (`engine/market_comps.py`, after trade_comps in the chain). Every free-agent signing, extension and draft pick on a card shows its three nearest comparables league-wide:
- *Signings:* distance = 2 x |log cost in wins| + 0.04 per year apart + 0.8 if pitcher vs hitter differs + 0.12 per year of age apart + 0.5 if the comp's deal is still running; one entry per player. Shown: his production for the club and his result against a typical club's return for the same money.
- *Extensions:* same service class only; 2 x |log cost| + 0.03 per year apart + 0.1 per year of age + 0.25 per season short of three played. Shown: seasons played, result against the class, projected finish where still running.
- *Draft picks:* 6 x |log pick| + 0.02 per year apart, other drafts through 2019 only (old enough to have played out). Shown: wins in club control and the result against the slot.

**Trees off the Deal Desk.** The "tree" links are removed from the Desk's piece cards and board rows (the simulator keeps them); player names on the Big Boards now open the player's chain, as they do on report cards and the Trees page.

### Faster load, the live winter, reliability-weighted Overall, phone cards, share pages (November 2, 2026, late)

**Faster load.** Every card's decision lists (chanLedgers, allx, walk: about 4MB) moved out of the page into `cards.js`, loaded in parallel like `moves.js`. The page is 3.5MB (was 7.5MB; about 1.9MB was its compressed transfer before). Views that need the lists (report cards, trees, player chains, the Scenario Room) wait for `cards.js` and draw when it lands (`whenCards`). The test harness waits for both files.

**The live winter.** On every load the page reads the league's public transaction feed (statsapi.mlb.com, which allows browser requests) from Nov 2, 2026 to today and applies it before forward-looking views draw: a major-league free-agent signing takes the player off the boards and the simulator's market and puts him on his new club, carried at the Ledger offer (the feed does not publish terms) as an on-file contract; a minor-league signing takes him off the board; trades, waiver claims and Rule 5 selections move the player. Grades never move on it. A simulator winter already under way keeps the market it started with. The test suites block the feed so they run on the Nov 1 cut; t_winter checks the apply logic on a synthetic signing. The scheduled task is now a weekly winter check (Mondays): site health, feed reachability, the signings and trades since the cut, and a rebuild recommendation past 25 major-league signings or a blockbuster. A full rebuild needs the local database, so it stays a session task.

**Overall, weighted by reliability.** The composite now counts each channel's net wins with weight 0.5 + 0.5 x the full-record reliability, rho = 2r / (1 + r) (Spearman-Brown on `reliability.json`'s split-half r, floored at zero): free agency 0.73, extensions 0.65, draft 0.58, waivers 0.52, trades 0.50; international and retention (no usable split-half sample: international reads only 7 regimes with six graded signings) sit at the 0.50 floor. The Net wins column stays the unweighted total. `reliability.py` now drops a channel with fewer than 20 qualifying regimes.

**Phone leaderboard.** Under 640px the table is replaced by one card per front office: rank, name, club and tenure, the Overall grade, the net-wins bar, the two best channels, the weakest, and Success.

**Share pages.** `share_build.mjs` (run after regen) renders a 1200x630 preview image for every card (`og/<slug>.png`) and a share page (`c/<slug>.html`) carrying that card's title, description and image, which forwards to the card. Report cards have a "Share this card" button (the share sheet on phones, the clipboard elsewhere). The site-wide `og.png` was rebuilt: the old one still printed the github.io address. The sitemap lists every share page.

### Boards split, trade boards, depth chart image, tree labels (November 3, 2026)

- **Three tabs instead of Big Boards.** Top Prospects, Farm Rankings and Top Free Agents are their own nav tabs at the end of Look ahead (free agents last, beside the Offseason Simulator). One view underneath, so links and tests are unchanged.
- **The assistant GM completes your deal, never a different one.** It no longer removes or swaps a piece you chose. A cornerstone the other club will not move gets an explanation instead of a substitute. With only your offer on the table, it finds the piece on their board your offer pays for (one that fills a hole first); with nothing on the table, it asks for the player who fills your weakest spot; then it balances with the cheapest of your pieces that meets their price. Same rules on the Desk and in the simulator.
- **Trade boards.** Your club on the left, the deal in the middle, the partner on the right, on a three-column grid (stacking on phones with the deal first). Rosters sort by 2027 projection by default, then surplus, youngest, cheapest. The simulator's trade board now matches the Desk (team-color partner chips, no default partner, same filters) at full width, with the live depth chart, the assistant GM and the winter log beneath it.
- **Depth chart image.** The saved image holds the roster and the winter's biggest moves (by stake), nothing else; the holes, suggestions and call-up note sit below it on the page.
- **Tree labels.** Every tree card says whose side its numbers are from; each value carries that club's abbreviation; pieces sent away show what they cost the club; a flipped player's node reads "TB got X for him; the deal's net for TB"; trade arrivals read "acquired by TB from PIT".

**Nav (same day).** Shorter nav labels (Trees, Prospects, Farm Systems, Free Agents, Simulator; full names kept as tooltips) so the three groups fit on one line at the 1240px header width. When they do not fit, a small script stacks the nav into three rows, one per group with its label at the left, instead of an uneven two-line wrap. Phones keep the single scrolling row.

**Launch wiring (November 3, 2026).** GoatCounter visit counts (no cookies, no banner needed) on the main page, loaded with `no_onload` so the page counts one hit per view and club (`/cards/ari`, `/boards/fa`, `/desk/trade`) through `folCount`, never per filter change; share pages redirect into the main page and are counted there. The test harness blocks the counter so test runs never show up in the stats. Google Search Console verification tag added to the head.

**Corrections inbox (November 3, 2026).** A "Corrections and feedback" link in the footer and a matching section on How it works mail frontofficeledger@gmail.com (subject prefilled). The address is assembled at runtime so it never appears in the page source; the personal contact address was removed from the About paragraph. Search Console verified (sitemap: 153 URLs) and the site imported into Bing Webmaster Tools.

### Nav, boards, Horizon landing, share images (November 3, 2026)

- Nav: Beta badge back; Head to Head shortens to H2H, Horizon becomes 5-Year Horizon, Top Prospects and Top Free Agents; full names elsewhere. Fits one line at the 1240px header; the three-row fallback is unchanged.
- Top Prospects now shows the Top 100 beside all 30 farm systems, each pane scrolling on its own (sticky, independent overflow). Clicking a farm swaps that club's own prospects in on the left. Old `#view=boards&id=farm` links land here.
- 5-Year Horizon opens on a league landing (three "at a glance" cards, the who-is-built-for-when table, club chips); picking a club shows its five-year detail with a league rank per season and a way back.
- Long explainers split into bullets (`folBul`: sentence ends outside tags and open inline elements); the Free Agents header became four bullets with the backtest detail collapsed; the leaderboard key defines Waiver / Minor, Int'l, Ext, Ret (retention), Dev (development) and Success.
- Scenario Room wording: "names hidden" replaces "blind" everywhere a reader sees it.
- Share images: `folSave` builds a branded frame (title, subtitle, frontofficeledger.com footer) and html2canvas (loaded on demand) downloads it. Buttons on every tree (featured, regime, champions chains, player chains, the pop-out), the leaderboard, Top Free Agents (by position too), Top Prospects (or one club's), farm rankings, the league Horizon and each club's Horizon. Frames lay tree cards out inline and drop inset shadows, both of which html2canvas misdraws.
- The assistant GM speaks in bullets everywhere (simulator notes, trade notes, the Desk, the Scenario Room): `agmList` gives each note a bullet and nests a long note's later sentences under its first (`folSplit`).
- Trade verdict copy: "a big salary is not a trade chip" only appears when the offer sends real salary back ($8M+ of 2027 money); a "Close" gap never reads +0.0.

### Pre-launch math audit (November 3, 2026)

- **Ledger WAR v1.7, defense.** Infield innings use Defensive Runs Saved (Sports Info Solutions, 2003-2026); catchers and outfielders use Statcast Fielding Run Value from 2016 (catchers: framing, blocking, throwing; 2016-17 catchers add DRS framing, counted once), DRS before that. Each source is centered on the league average at its position every season, and the positional adjustment stays. New ingests `engine/frv_ingest.py`, `engine/drs_ingest.py`; rule in `engine/lvm15.py`; full rebuild `engine/lvm_v17_rebuild.py`. Team WAR vs wins 2015-2025: r 0.926 to 0.925, slope 0.915 to 0.879, MAE 4.82 to 4.78; 2003-2014 r 0.818 to 0.848. League totals 1,050-1,130 per full season. The old SDI-only years (2014-15) lose about 37 WAR each.
- **Prospects.** Top 100 peak and 2-win/4-win odds = 0.7 x a rank prior (2012-2019 lists, hitters and pitchers fitted apart, x = ln(max(rank, 2))) + 0.3 x the 25 nearest ranked comparables; ranked prospects with no minor-league line take the prior alone. Leave-one-cohort-out on 776 ranked prospects: peak r 0.330 to 0.388, 4-win Brier 0.1057 to 0.1014; ranks 1-5 peak 2.80 to 3.89 (realized 4.22), 4-win 26% to 44% (45%). The six-season value curve is split: hitters 1:12.4 ... 100:2.2, pitchers 1:6.7 ... 100:1.6 (`vrankH`, `vrankP`), in desk_data, asset_rules, sweep_score, proj_v1 and prospects_peak; trade_calib now passes the player. Eight Top 100 prospects with no Ledger record get desk rows. The Desk values 2026 draftees on slot value (it had priced them as unranked).
- **Contracts.** The page read `DESK.market.drift` (absent) and fell back to 1.16; it now reads `DESK.drift` (1.08). Catcher bump removed (regular catchers already landed ~7% under the blend); relievers x0.85; the big platform-year rule halves its AAV cut (x0.945, the -0.27 years kept); a 1-3 win platform year above 1.5x both prior seasons gets x1.10. Walk-forward backtest of this exact blend, 1,434 signings 2012-25 (`calib_blend.json`, shipped as CALIB): 0.53 years, $2.7M AAV, $10.3M total; $50M+ offers land at a median 95% of the offer (n=127). The likely-range bands come from the same file.
- **Playing time.** For players 26 and under whose 2026 playing time was at least 60% of a full season, expected 2027 playing time is floored at 85% of it, and a partial debut season leaves the average when a later season reached half a season (`desk_data.py`).
- **Simulator market.** Clubs bid within their own 2015-2025 free-agent history (biggest AAV x1.2, a winter budget from the 80th percentile), lean toward players whose Statcast profile matches what their acquisitions have favored (Org DNA fingerprints, `fa_skills.json`), and weigh the glove (DRS or Fielding Run Value). The league market table is no longer shown. The winter memo is an in-page sheet (depth chart, every move, grade, record, payroll, base rate, similar winters, where the money sits), saved as an image or printed to PDF.
- **Data clean-up.** No per-row computed badges or process notes; full trade headlines (affiliate clauses dropped, feed capitals lowered, cut at 300 characters with an ellipsis); re-signings are not walks (Clemens 2002); in-season signings never borrow next winter's contract (Oliver Perez 2018); minor-league free agency closes a player's control window (Berti); ten trade size bands for move letters; trade counts skip player-less fragments; card farm lines read the Top Prospects board. Scenario Room: no extension offers to players already extended, stronger trade packages, the generated what-if deadline deal retired.
- **Mobile.** A phone layout for every view (leaderboard cards with an aligned grade grid, wrapped tree cards, stacked boards, a pinned deal on the trade boards, thumb-sized simulator controls).

## Deal Desk and simulator additions (November 3, 2026)

- **Trade walk.** Pick one of your players and the desk takes him to the other 29 clubs. Each club values him at his surplus, 10% more if he fills one of its holes, 10% more if it is a contender, and about half as much if it is rebuilding and he is short-term or 32 and up. A club that has never paid his salary in free agency (max AAV x1.2) passes. Each club pays in its own pieces at its asking price, up to three pieces.
- **Available players.** A read, not a report: rebuilding clubs, one or two years of control, salary a club would shed, and good players who do not start on their own depth chart score toward Likely, Possible or Long shot. Cornerstones (surplus of 5+ wins and 4+ years of control) on clubs that are not rebuilding are left off. Contracts deep underwater are capped at Long shot.
- **Two-sided trade verdict.** Each club's net is its surplus in minus surplus out, weighted for its own place on the win curve. "Will it get done" combines the counterparty's asking-price check with the proposing club's net and roster fit.
- **Similar real trades.** Comps now match both sides of the deal (value in and value out), the control bucket, and the position group of the headline piece on each side (catcher, infielder, outfielder, pitcher), from the 1998-2023 buyer-seat archive.
- **Negotiation.** An offer at the camp's yearly rate but one year short of its term is a counter position, not a lowball.
- **Regimes.** Chris Antonetti's Cleveland tenure is one regime from October 16, 2010 (GM and then president of baseball operations).
- **Prospect lists.** The Top 100 is MLB Pipeline's October 2026 list (it was the June list). Ranked prospects are valued 70% on what players ranked there became and 30% on their 25 closest ranked comparables; everyone else is valued on the minor-league model. The boards order by Ledger value, not by Pipeline rank. Prospects who reached the majors in 2026 but are still under rookie limits show MLB as their level and their big-league line (debut26.py); their values are unchanged.
- **Trade block.** The trade walk is now called the trade block.

## Pre-launch run-through (November 3, 2026, late)

- **Leaderboard.** Every graded seat is ranked, partial samples included; short tenures carry the small-sample tag. (An earlier pass left seats under two seasons unranked.)
- **Trade lines.** Card headlines are rebuilt from the club's own side when the league's line leaves the club out, repeats a player or carries a minor-league leg (regen_v3.py, `_fix_h`). True three-team deals are labeled.
- **Simulator.** The Assistant GM's notes sit under the stage bar. The trade tab opens on a trade block (players who could move, best first, with a position filter), and a button returns to it from any club. Agents never open below the Ledger offer.
- **Pickers.** Report Cards, Transaction Trees, Org DNA and H2H carry the same club buttons as the Horizon.
- **Scenario Room.** Opens on the 2017 José Ramírez extension. Live free-agent decisions use the Ledger offer as the market price, the same number as the Top Free Agents board. Trade reveals say that extensions signed later are graded on their own.
- **Phones.** Big Boards show one list at a time; the trade board and free-agent class no longer scroll inside boxes; the winter memo's toolbar wraps.
- **Call-ups.** 2026 draftees add nothing in 2027.

## Deal sheets, origins and early seats (November 3, 2026, night)

- **Deal sheets.** Deal Desk verdicts (trade, free-agent signing, extension) use the report card's deal layout: a kicker with the club and regime, a headline, a date line, the two sides with values, the net with its status and the desk grade, a market comps table with a descriptor under each comp, a footnote and a note. The printed memo uses the same sheet.
- **Comps.** Trades: the nearest real trades by value in and out, control, buyer posture and position on each side. Signings and extensions: the nearest contracts by platform production, age and position type, with what each produced and its surplus. The simulator's deal card shows the three nearest trade comps; each free-agent negotiation has the three nearest signings one click away.
- **Career trees start at the origin.** Drafted players open on their draft slot and signing bonus (MLB draft results, 1985-2026; `origins.py`). International amateurs open on their first signing, with age and country; their bonuses are not in public data. Graded draft and international decisions keep their grade on that node.
- **Early seats.** Under two seasons in the seat, style descriptors (temperament, taste, development reads, shopping tags, nearest comparable) are not shown: there is not enough record to read a style. Grades and ranks still show.


## Cashman's seat and waiver pairs (November 3, 2026, late night)

- **Brian Cashman.** The Yankees' active record now starts with the 2005-06 winter, when Cashman signed a new contract that gave him more authority over personnel. February 1998 to October 2005 is its own archive record, flagged "ownership era": in those years George Steinbrenner's Tampa group often had the final say. The early record carries most of the old deficit (trades -66.1, draft -42.2, and the 2001 Jeter and Rivera extensions). From the 2005-06 winter on, he is a C over 21 seasons (-17.6). The stale "ledger floored at 2005" flag is gone.
- **A claim and its undoing are one decision.** Before, a waiver claim was credited the player's next four seasons wherever he played them (the claim season counted only with the claiming club), and the same club's later loss of him charged his next four seasons with his new club. Dan Otero, claimed by the Yankees on March 26, 2013 and claimed away by Oakland three days later, read +3.9 and then -5.1 for a pitcher who never pitched in New York. Now a claim (or Rule 5 pick) followed by the same club losing him on waivers or in the Rule 5 draft, inside the claim's four-season window and with no trade between, is one entry: what he produced for the club while he was there, net of the salary it paid (`asset_rules.waiver_pairs`, `held_window`). The loss is not charged again. Losing a player the club held for longer (drafted, traded for, or kept past the claim window) is still charged.
- **Trades are not weighted by the win curve.** Past trades have been graded on unweighted value since v5.9: weighting each season by the buying club's leverage moved value from bad clubs to good ones by construction. Weighting each seat at its own leverage instead would not help a club that contends every year, because the same multiplier lands on both sides of its deals and enlarges the gap. The Deal Desk and the simulator still weight a proposed deal for each club's current place on the win curve, because those are forward decisions for a known club.

## Market price vs. our value (November 3, 2026, night)

- **What we checked.** The Ledger offers for this winter's top 50 free agents were compared with four published projection sets: ESPN (Kiley McDaniel, all 50), MLB Trade Rumors (top 19 readable), Bleacher Report (top 10) and The Athletic (Jim Bowden, top 5 from a summary). FanGraphs was not used. Before the change, our yearly rate ran from about 40% under the projections' median (Michael King, 3 yr / $47M against a 4 yr / $92-120M range, after he opted out of $58M) to about 50% over (Kevin Gausman, David Peterson).
- **Which read is better.** On last winter's top free agents, MLB Trade Rumors' projections missed the real yearly rate by $6.0M on average and our market model (the walk-forward backtest) by $12.6M; on years they were close (1.9 vs 1.5). The market model ran low on almost every big contract (Tucker, Bichette, Cease, King).
- **The change.** The market price (the "Ledger offer", which the simulator, the scenario room and the free-agent board all use) now leans on the published median for the players it covers: the yearly rate is 80% the median (70% with one source) and 20% our model, in logs; the term is the average of the two. `market_consensus.json` holds the per-player median (years, AAV, number of sources), shipped as `DESK.cons`. Players outside the published lists keep our own read.
- **Our value stays ours.** The model-fair offer (full market price for his projected WAR) is unchanged. The free-agent board's new Ledger view column sets the market price against it, relative to the class median ratio: 15% or more cheaper is a value buy, 15% or more dearer is paid above value. This is where we disagree with the market (King and Peralta read as paid above value; Rogers and Skubal about right; older starters such as Gray and Gausman as value buys).
- **Prospects, for reference only.** TJStats' August 2026 Top 100 against our order: 94 of 100 matched (the rest debuted), rank correlation 0.69. The biggest gaps are prospects Pipeline does not rank (George Klassen, Carlos Lagrange, Luis De León): our values for unranked players come from minor-league comparables, and they run low on hard-throwing pitchers. No change made.

## Every draft round, retention through 2025, validation copy (November 3, 2026, night)

- **Draft: every round.** The draft channel graded rounds 1-5 only, so late-round hits (Tarik Skubal, 9th round, #255; Steven Kwan, 5th round in a later era; Joe Ryan, Bryan Woo, Dellin Betances) earned their clubs nothing. Every round is now graded. Rounds 6+ use the slot curve times a band factor fit on the matured 1998-2013 classes (realized value per unit of curve, relative to rounds 1-5): rounds 6-10 x1.235, rounds 11-20 x1.009, rounds 21+ x0.329 (`draft_calib.py` writes `band`; `asset_rules.draft_band`). A late pick's bar is a few hundredths of a win, so a hit is nearly all profit and a miss costs almost nothing; centering keeps a club from banking credit just for making picks. Late-round picks that produced under half a win are left out of the card's full list (they still count in the net). Skubal now reads +22.7 on Al Avila's Detroit card.
- **Retention through the 2025-26 winter.** The expectation curve is still fit on 1998-2023 departures (three full seasons seen). Departures from 2024 and 2025 are now graded on the seasons available, with the expectation cut to the share of a three-year total that past departures delivered in that many seasons (two seasons 0.75, one season 0.424). This winter's departures have nothing to read yet.
- **Rentals and re-signings.** Unchanged and now explained on the page: a re-signing or an extension before the filing is graded as that signing or extension; a deadline rental's walk belongs to the trade, which was credited only with the weeks he had left.
- **Validation copy.** The Methodology paragraph quoted an older run (partial r 0.11, interval crossing zero, no out-of-sample gain). The copy now reads the numbers from `validation.json` at render time. With every draft round in, the partial correlation of decision value with the next two seasons' W% (controlling for record to date) is 0.16, 95% interval [0.04, 0.28], out-of-sample R-squared 0.175 to 0.189.
- **Ledger WAR for pitchers** is now described on the page: park-adjusted FIP (strikeouts, walks, hit batters, home runs per inning) against the league, times innings, plus replacement; no leverage credit for relievers.
- **Footer** trimmed; the Retrosheet notice stays (their license requires it). Links to @SeanZerillo and @FrontOfficeLdgr on X; the header carries a Follow button.

## Simulator, free-agent reads, imports and Statcast (November 3, 2026, late night)

- **Org ranks.** A prospect's org rank counts everyone above him in the system: the club's Top 100 prospects first, then its other prospects in list order (`gmOrgRank`). A system with two Top 100 players starts its other list at #3.
- **Fair Ledger offer, side by side.** The free-agent board and the simulator now show the projected contract next to our fair offer for the same years (full market price for his projected WAR over those seasons, `dkSuggest().fairSame`), with the gap in dollars. The "Ledger view" labels are gone.
- **Qualifying offers are facts.** The eight QOs extended Nov 2 (Arozarena, Bauers, Bednar, Jeffers, Lowe, Morejón, Rogers, Suzuki; `qo_2027.json`, shipped as `DESK.qo27`) are attached automatically: signing one of them away from his club charges a draft pick, on the Deal Desk and in the simulator. The Deal Desk's "QO attached" checkbox is gone. The simulator's contract-decisions stage shows the real offers and lets the player answer.
- **Simulator trades read on the Deal Desk.** The trade tab keeps the trade block, available players and both rosters, and the deal on the table is read by the Deal Desk's sheet (both seats, market check, market comps), with the simulator's own counterparty answer as the call.
- **Simulator free agents.** The class sits in a list on the right; picking a player opens his terms in the middle (projected contract, fair offer, negotiation, contract comps).
- **"Try it"** on the Deal Desk prices the terms and scrolls to the verdict.
- **Posted players.** Their translated rows are already a comps average, so they are no longer regressed a second time. Where this winter's published projections price them, the projection is half the stat translation and half a money translation: across the 25 usable imports since 2017-18, what each was paid (AAV, drifted 5% a winter) against what he produced in his first two seasons (hitters v = 0.42 + 0.071 x AAV, pitchers v = -0.33 + 0.089 x AAV; `posted_build.py`). Teruaki Sato's 2027 projection moves from 1.2 to 1.6 WAR, Kaima Taira's from 1.0 to 1.2. Both remain below what their contracts imply: the imports most like them produced about 2 (Sato) and 1.3 (Taira) Ledger WAR a season.
- **Statcast skill read** (`skills_fit.py`, Baseball Savant leaderboards 2016-2026). The projection was already three seasons weighted 5/4/3, regressed by sample, times expected playing time, then aged on the curves with attrition. It now adds a residual fit on 2017-22 seasons: pitchers, fastball velocity, its change, and wOBA against beyond xwOBA; hitters, xwOBA beyond wOBA, sprint speed and its change. Out of sample (2023-25) it trims next-season RMSE about 1% (pitchers 0.899 to 0.888, hitters 1.567 to 1.551). Velocity carries little once three seasons of strikeouts and walks are in the rate (+0.08 WAR per mph of change). The hitter terms matter more: Randy Arozarena's 2026 wOBA ran .031 over his xwOBA and his sprint speed fell, so his 2027 projection drops 0.43. Bat speed (tracked since 2023) is too short a series to test. Adjustments are capped at +/-0.8 WAR.
- **Video v4.** A quick-cut opening across every feature, then slower demos (Deal Desk sheet and comps, trade block, available players, a priced signing, the simulator's trade read and a negotiation, the memo, leaderboard, champions, trees, horizon, prospects, free agents). Music: "Monkeys Spinning Monkeys" (alternate cut: "Hyperfun") by Kevin MacLeod (incompetech.com), CC BY 4.0, credited on the end card.

## Projection weights and playing time (November 9, 2026)

- **Checked against Steamer and Depth Charts (private benchmark, not used on the site).** Our 2027 projections correlate 0.88 with Steamer for hitters and 0.83 for pitchers. We run higher on glove-first players whose Ledger WAR leans on Defensive Runs Saved or Fielding Run Value (Brice Turang, Zach Neto, Isiah Kiner-Falefa, Jarren Duran) and on stars coming off a down year; lower on rookies and pitchers returning from injury, where Steamer uses minor-league and health assumptions we do not have.
- **Season weights 5/3/2, regression x1.5** (`proj_bt.py`, walk-forward on 8,696 player-seasons 2016-2026, target next-season Ledger WAR): RMSE 1.130 to 1.117 with actual playing time, 1.408 to 1.389 with expected playing time. After a large drop or jump (2+ wins per full season) the same weights still win with little bias: in Ledger terms, breakouts and collapses carry forward about as much as the weights already assume. A change in xwOBA from the prior season adds nothing out of sample; xwOBA beyond wOBA (luck) does, and is already in the Statcast read.
- **Defense regressed apart:** tested (defense and baserunning projected with their own regression), no gain in predicting Ledger WAR; not adopted.
- **Playing time, 28 and older** (`pt_bt.py`): 20% the two fullest recent seasons and 80% the weighted line, instead of 60/40 (RMSE 1.319 to 1.310, bias +0.02 to -0.01). A regular turning bench player is no longer projected for a regular's playing time. One injury season after full ones (last under half a season, one of the two before at 80%+) uses 40/60: those players rebound more (bias +0.12 at 60%, -0.08 at 20%, +0.02 at 40%). 27 and under keep 60/40.
- **Posted players:** the money translation now leads, 75/25 against the stat translation (the stat comps are 10 hitters and 15 pitchers). Teruaki Sato's 2027 projection is 1.75 WAR.

## Where we disagree with Steamer, and what changed (November 9, 2026, later)

- **Our WAR is not the problem.** Season Ledger WAR correlates 0.969 with fWAR and 0.955 with bWAR for hitters, 0.922 with fWAR for pitchers. Projecting next-season fWAR from Ledger history works as well as projecting it from fWAR history (hitters r 0.515 vs 0.519). Jarren Duran's fWAR line (2.5 / 6.9 / 4.0 / 0.5) is nearly the Ledger's.
- **The gap with Steamer has three sources** (`outliers.py`, 267 established hitters, R-squared 0.37 of the per-600-PA gap). Oneil Cruz is not one of them: we have him at 2.24, Steamer 2.53. Duran is: 2.78 vs 1.13, of which about 0.7 is defense, 0.44 the Statcast read, 0.3 playing time and 0.2 the weight on 2024-25.
  - *Defense at face value.* Ledger WAR counts Defensive Runs Saved (infield) and Statcast Fielding Run Value (outfield, catcher) as they happened; Steamer regresses fielding hard toward the positional norm. Hitters at -10 runs or worse over three years sit 0.55 WAR/600 below Steamer (Jacob Wilson, Brooks Lee, Bichette, Jung, Correa); glove-first players sit above (Turang +51 runs, Walls +51, Neto +33, Chapman +37). In the Ledger's own record, defense and baserunning per 600 PA are more persistent year to year than offense (r 0.585 vs 0.501, regulars 2016-26), and projecting defense apart with heavy regression never improves the backtest (`def_bt.py`). DRS is also a little more reliable than FRV for infielders year to year (0.51 vs 0.45; `ifdef_test.py`). Kept. The page now says so.
  - *The Statcast read.* Sprint speed is the strongest single correlate of the gap (r 0.46): fast players read higher here, slow hitters and catchers lower. Refit on the current baseline, the xwOBA gap carries nearly all of the out-of-sample gain; speed adds little and shrinks 40% once age is in the fit. The production coefficient (0.105 WAR per ft/s) is already below the age-controlled refit (0.157), so nothing was trimmed. The read helps catchers too (bias +0.07 to +0.02), so it is not a positional penalty.
  - *Aging.* The delta-method curves only see players who came back the next year (the survivor bias in the FanGraphs community joint-model piece, which puts the peak near 26.5). The curve over-projected hitters 31-34 by +0.43 WAR and 35+ by +0.77 with expected playing time. The decline side (27+) is now 1.5x the raw step (`proj_v1.py` DECLINE); growth is unchanged. Rate-only RMSE unchanged, expected-PT RMSE 1.389 to 1.380.
- **Playing time for established players** (`pt_war_bt2.py`, `pt_war_bt3.py`, `pt_pit_bt.py`). Hitters 27+ coming off 300+ PA got 7-25% less time than the formula said, more when older and when they had hit poorly (under 1 WAR/600: 75% of the estimate; 3.5+: 91%); full-timers came in 100 PA under and part-timers 130 over. Young players were unbiased (+2 PA). Starters showed the same shape (+30 IP for full-time 27+), relievers did not. For hitters and starters 27+ expected playing time is now regressed 15% toward half a season, then multiplied by 1 + 0.12 x (WAR per 600 minus 3.5) for hitters (floor 0.7, only when the estimate was 300+ PA) and 1 + 0.10 x (WAR per full season minus 3.0) for starters (floor 0.75, from 88 IP), never above 1. A player whose last season was full (75%+ of a season) keeps at least 75% of it (starters 70%): regulars who became regulars last year after partial seasons went on to play 25% more than the cut implied (`pt_floor_bt.py`). Jake Bauers: 578 PA in 2026 after 346 and 218, projected for 434 (the cut alone said 379). Hitters: WAR RMSE 1.661 to 1.637, 1.632 with the steeper decline; 31-34 bias +0.43 to +0.18. Starters 27+: 1.379 to 1.359. Duran's expected 2027 playing time goes from 671 to about 530 PA (Steamer and Depth Charts: 523).
- **Tested and not adopted:** regressing to a position-group mean instead of the league mean (worse); a hitter skills layer (strikeout, walk, power, BABIP, xwOBA, speed, age; about 1% RMSE gain, and it moves Duran up and Bauers down); year-over-year skill changes as breakout and collapse signals (nothing out of sample); a smaller regression constant for young regulars (their under-projection is selection: the ones who got 450 PA are the ones who hit).

## Hitter playing time: availability and role (November 9, 2026, night)

- **Why.** The formula could not tell an injury from a benching. Oneil Cruz's 419 PA in 2026 came from two months on the injured list with a broken left hand (he faced left-handers at a normal rate, .847 OPS); Jarren Duran's 608 came in 151 games while his PA per game fell from 4.8 in May to 3.2 in September and his share against left-handers dropped from 31% to 23%.
- **New inputs.** Injured-list days per player-season from the 2005-26 transaction sweep (`il_build.py`, 24,941 placements, transfers and activations; a stint with no activation on file ends with its season); league-wide splits against left- and right-handers and after the All-Star break, 2013-26, and bat side, from the MLB Stats API (`splits/`).
- **The model** (`pt_model.py`). Ridge regression, walk-forward (each season predicted from a fit on earlier seasons only), target next-season PA with zeros counted, hitters 37 or younger with 150+ PA in the last season or 300+ the season before. Features: the old formula, PA in each of the last three seasons, games played last season, PA per healthy team game in each season, the regressed WAR rate per 600, age, age past 30, and last season's PA per healthy game times years past 27.
- **Result, 2018-26 seasons (3,262 player-seasons).** PA RMSE 176.9 to 157.4, bias +25.5 to +2.1; WAR RMSE 1.541 to 1.532. Role-drop seasons (PA per healthy game down 0.4+): bias +100 to +11 PA. Hitters 31+: +78 to +9. Injury seasons (25%+ of the last season on the IL): RMSE 183 to 166, both unbiased.
- **Tested and left out.** Injured-list shares, vs-LHP share and its change, the platoon OPS gap and the second-half role add nothing once PA, games and PA per healthy game are in (with them 158.6, without 157.4). Gradient boosting matched the ridge (157.2) and is not used. A structural model (162 games x expected health x expected role) was worse than the old formula (194.5).
- **Effects.** Duran 531 to 500 PA, Cruz 455 to 481, Jake Bauers 434 to 445, Isiah Kiner-Falefa 312 to 209, Ronald Acuña Jr. 371 to 436, Brice Turang 619 to 665. Starters keep the formula. Also fixed: the hitter rate cut in desk_data was reading WAR per 680 PA where it had been tested per 600.
- **Display.** Projections on the free-agent board, the free-agent sheet, the simulator and each trade piece show playing time and the rate per 600 PA (per 180 IP for starters, 65 for relievers) beside the total.
- **Arbitration salaries never fall** (Nov 9, night). The estimate for a later award was priced only on the projected prior season, so a player paid on a big platform year could read a cut the next winter (Oneil Cruz: $13.1M in 2027, then $8.8M in 2028). Awards build on the last one and are almost never cut; a later award is now at least the one before (`gmArbSal`). Known limit, not yet fixed: the estimate prices WAR, while panels pay on playing time and counting stats, so a player who missed time (Cruz, 97 games in 2026) likely reads high.
- **Methodology copy.** The projections section is now in parts (rate, playing time for hitters and pitchers, aging, defense, Statcast read, what the page shows), followed by how the Deal Desk prices a trade beyond projected WAR (surplus net of salary over control, each club's place on the win curve, roster fit, the market check against real trades of the same shape, whether the other club says yes).

## Arbitration salaries anchored to MLB Trade Rumors (November 9, 2026, night)

- **Why.** Our estimate priced WAR: (0.6 + platform WAR) x class step x $/WAR drift, fit on 48 real 2026 awards, leave-one-out miss about $1.6M a player. Panels pay on playing time and counting stats, so it ran high for players who missed time and low for durable ones with modest WAR: Oneil Cruz (97 games in 2026) read $13.1M, Jarren Duran (151 games) $8.6M.
- **Source.** MLB Trade Rumors' annual arbitration projections (Matt Swartz's model), parsed from the post (`mlbtr_arb.py` -> `arb_mlbtr_2027.json`, 296 players; 294 matched to our player rows by name and club). The same model's 2026 projections, scored on our 48 real 2026 awards: MAE $0.49M, RMSE $0.71M, bias +$0.08M.
- **Use.** The 2027 salary is theirs where they list the player (including 19 players our service record had as pre-arbitration or gone; those keep our status otherwise). Later awards build on the one before: raise = 0.274 x last award + 0.68 x the platform season's projected WAR - $0.15M, never a cut, fit on 140 players on both their 2026 and 2027 lists. Players they do not list keep our estimate.
- **Effect.** Duran $11.1M in 2027, $15.4M in 2028 (was $8.6M / $8.7M); Cruz $6.3M, $9.3M (was $13.1M / $13.1M). Duran for Cruz from Boston's seat moves from -0.8 to +1.9 WAR of surplus; Pittsburgh now says no (it would want about +1.4 more).
- **Wording.** "Holes" is now "needs" across the Deal Desk, simulator and assistant GM.

## The front door, stories and games (November 9, 2026, night)

- **Your team first.** The site opens on a team picker (30 tiles in club colors, each with its front office's overall grade). Picking a club opens its page: the front office's grade as a stamp and its rank, net wins against a typical front office, on-field grade, a dot strip placing it among the 28 graded active front offices (net wins per season in the chair), the five-year Horizon outlook, its biggest single win and loss from the ledgers, and the tenure's cumulative net value with the six biggest moves pinned on the line. The choice is remembered in the browser and opens the Deal Desk, the simulator, Horizon and the report card on that club the first time each is visited.
- **Heists and disasters.** Every trade in the book since 1998 (4,172), ranked by the winning side's net Ledger WAR over each piece's control window, with each player's value as a bar and the front office in charge on each side at the date. Filters: since 1998 / 2010 / 2020, and by club (its best or worst). A second list ranks free-agent signings from the regime ledgers (production on the deal against what a typical club gets for that money). Stamps: grand larceny 15+, heist 10+, lopsided 6+.
- **Who won the trade?** Five real two-club trades a day (the same five for everyone, seeded by the date), drawn from deals through 2023 with at least a 4-win gap and a player worth 4+ wins either way. Pick a side, then see every player's value. Streak and best streak stay in the browser; the result copies as a five-square line.
- **Deal Desk.** The trade verdict opens over the deal screen with a close button (Esc also closes); a meter shows which club wins it, with a badge for whether it gets done. Every piece carries a not-interested button: the player comes off the table and out of every list and the assistant GM renegotiates without him ("bring them back" undoes it). "Make it fair" is the assistant GM's balance. With a team picked, the Desk opens on a suggested trade: the best available player who fills the club's weakest spot (never a franchise cornerstone, sellers first), balanced to the other club's price.
- **Simulator.** A sticky scoreboard (projected record, against standing pat, payroll, moves) that flashes when a move changes it, an "Up next" card with one decision at a time (non-tender calls, your own free agents, the free agent who fills your biggest need), and "Share my winter" as an image at the close.
- **Smaller things.** The leaderboard key and the Deal Desk, simulator and Horizon introductions fold into "How to read a row" and "How it works" dropdowns; three-season sparklines on the free-agent board; numbers count up and grades stamp in (off for reduced motion); a bottom bar on phones (your team, heists, quiz, trade, simulator). Player headshots are left out: they are MLB's images, beyond the data the site already credits.
- **Tests.** `t_fun.mjs` (26 checks); `t_ui2.mjs` intro checks now test the team picker on a first visit and the remembered team on return.

## Contract prices, posted hitters, the hub and the team page (November 9, 2026, late night)

- **Why contract prices moved.** Our fair offers ran well under the market for position players (board median fair value was 0.59 of the consensus contract for hitters, 0.92 for pitchers). We checked what free agents actually returned.
- **Backtest (`fa_value_bt.py`).** 295 multi-year free-agent deals from the 2014-22 winters, each scored on realized WAR for the signing club against our projection at signing.
  - Realized over projected: hitters 0.85 (0.90 weighted by dollars), pitchers 1.40 (1.46).
  - Dollars paid per realized win, against our $/WAR scale: hitters 1.45x, pitchers 1.53x.
  - Read: the market pays a premium over our $/WAR line for both, and pays it for wins we under-project on pitchers.
- **Change.** Fair offers now price each projected win at what clubs have actually paid per realized win on these deals: 1.45x the $/WAR scale for hitters, 1.53x for pitchers, before the usual later-year discount. Board median fair over consensus is now 0.88 for hitters and 1.08 for pitchers.
- **Posted hitters (`posted_build.py`).** NPB and KBO lines are now matched as ratios to their league's average OBP, SLG and HR rate for that season (2016-25), not raw lines, so a KBO hitter in a high-offense year no longer matches an NPB star. Each hitter's projected seasons blend the comparable players (half) with a straight-line fit of MLB WAR on those league-relative rates (half).
  - Effect: Teruaki Sato about 1.8 WAR in year one; Si Hwan Roh 1.14 (was 1.28). The earlier order came from KBO raw lines matching NPB stars, plus Ha-Seong Kim's defense-driven value pulling KBO comps up.
- **Home is a hub.** The "Is your GM any good?" banner is gone. Home leads with the heist of the day (with links to its transaction tree and to all heists), the Who won? game, the five best active front offices, an offseason simulator teaser, the scenario of the day and the top of the free-agent class, then a compact 30-chip team picker (club codes only, no GM names). The FRONT OFFICE LEDGER header returns home.
- **Team page.** Its own view. Actions in order: full report card, leaderboard, run the winter, make a trade. Then the club's spot on the leaderboard (two above, two below), its strip against the league, best and worst move, the Horizon outlook, the tenure timeline, and the best and worst trades under the current GM. The prospects and free-agent buttons are gone so the page stays on that front office.
- **Nav.** Home, Leaderboard, Report Cards, Champions, Org DNA, H2H, Heists, Transaction Trees. Who won? lives on the home page and the phone bar, not the nav.
- **Who won? with context.** Each player in a trade question shows position, age, his WAR the season before the deal and his career WAR to date (or "prospect, no big-league WAR yet"), and each deal is labeled offseason, in-season or trade-deadline. Two of the daily five are now free-agent contracts (192 finished deals from 2003-25 at $8M+ a year and 2+ years, where production and the typical return differ by 2+ wins): the player's last three seasons and the terms, a call of "earned it" or "fell short", then his WAR in each year for the club against what a typical club gets for that money (`quiz_ctx.py` -> `quiz_ctx.json`).
- **Deal Desk.** "Make it fair" and "Suggest a trade" now build the deal and stop; the verdict opens only on Evaluate. "Bring them back" is a single Undo that steps back one change (the removed player, the board and the deal as they were).
- **Tests.** `t_fun.mjs` adds hub teasers, the team page actions, nav order, player context and contract questions; `t_ui2.mjs` tests the hub and the compact picker; `t_winter.mjs` checks the assistant GM no longer opens the verdict on its own.

## Home page, trees, Org DNA and the scenario list (November 9, 2026, later)

- **Home.** The first block runs heist of the day, the leaderboard, Who won?, the offseason simulator and the scenario room, in that order. Below it, three sections:
  - Today in the ledger: the most lopsided trade made on today's date (nearest day within a week when none), a signing of the day and a draft steal of the day from the regime ledgers (moves worth 4+ wins either way, rotated by date), the rivalry of the day and the tree of the day.
  - This winter: the top free agents, players posted from Japan and Korea with their signing deadlines, the clubs with the most WAR under control in 2031, and the top prospects.
  - Play GM and explore: Deal Desk, follow any player's tree, how the latest champion was built, Org DNA.
  - A search box finds any player (his full chain), GM (report card) or club (team page). Counts under the headline read from the data.
- **Who won?** is back in the nav, fourth under Play GM.
- **Transaction trees.** Three tabs: featured trades, a club's biggest trades, follow a player; only one shows at a time, so picking a club no longer stacks under a player's chain. A player's main line (how he arrived, each trade, extensions, where he stands) stays open; each trade's other pieces fold under "Where the other pieces went". Club and featured trees fold from the third level down. "Open every branch" expands a card. Trade cards show one row per club: who ran it, what it got, its net.
- **Org DNA.** Leaders strip (best drafters, best traders, where pitchers and hitters improve, fewest IL stints, most picks over slot), then one card per club: style tags, what it shops for, arms and bats net by draft, trades and free agency as bars with its rank, and its habits against the league median (picks over slot, IL stints, buys after a down year, arrival changes). Sortable by any of them. The full table folds below.
- **Report cards.** "How this front office builds" (the same profile) now sits above the ledgers instead of at the bottom.
- **Scenario room.** With names hidden, the list shows no player names at all: live 2026-27 calls read "sign a free agent at SP", "extend a 25-year-old", "trade for a controlled star". The home tile for a hidden archive call shows the club's record and the moment, not the club and year.

## Sharing, phone pass, simulator fixes, qualifying offers, load speed (November 9, 2026, evening)

- **Qualifying offers.** Signing a free agent who declined a qualifying offer now costs what the 2022-26 CBA says, by the signing club's category for the 2027 draft (MLB Trade Rumors' October 2026 list):
  - Tax payors (TOR, ATL, CHC, LAD, NYM, SD, PHI, BOS, NYY): second- and fifth-highest picks plus $1M of international pool; a second signing costs the third and sixth.
  - Revenue-sharing recipients (ATH, MIL, STL, ARI, CLE, SEA, MIA, BAL, PIT, TB, CIN, COL, KC, DET, MIN): third-highest pick; a second costs the fourth.
  - Everyone else (LAA, HOU, SF, WSH, TEX, CWS): second-highest pick plus $500K; a second costs the third.
  - A third signing is modeled the same way, one pick further down. Re-signing your own player costs nothing; the highest first-round pick is never forfeited.
  - Each pick is valued at the slot curve (82% maturity, 10% a year discount) at a typical position for that pick; pool money at the 2027 dollars per win. One tax-payor signing is about 1.5 WAR, one revenue-sharing signing about 1.0. Before this, every qualified signing cost a flat 1.0 WAR.
- **Simulator.** An offer no longer moves the page: the negotiation is measured before the redraw and put back where it was. The player you are talking to stays selected even after he signs or drops out of a filter. "Open negotiations" lists only the talks not already on screen, and Resume jumps to that negotiation. The "Up next" suggestion in the open market shows once and steps aside as soon as you pick a player or make an offer.
- **Share pages.** New pages with their own preview images, built from the page by `share_more.mjs`: `t/<club>` (a front-office trading card: grade, rank, net wins, 2031 outlook, best and worst move, signature trait), `h/<date>-<club>-<player>` (the 116 trades the heist of the day draws from; the link opens that heist on top) and `play/who-won`. Report-card pages (`c/`) are unchanged. Team pages and heist cards have Share buttons (the phone share sheet, or a copied link); the team page saves its trading card as an image; Who won? saves the day's five as an image. Shares and saves are counted as GoatCounter events.
- **Phone pass** (a separate review at 390px):
  - The masthead is one row of about 106px instead of 208px.
  - The home "best front offices" and the team page's rank now use the leaderboard's own order (overall grade, then total net value).
  - Trade cards on a club's page read from that club's side ("Loss · -11.9"). Each side's number reads "net", bars share one scale, and the trade-card footnote appears once.
  - Club names are the ones used at the time (Indians, Devil Rays, Expos, Florida Marlins, Anaheim, Oakland).
  - Wide tables keep their first column; free-agent board text wraps; controls are larger.
  - The Evaluate button on the Deal Desk is solid and sticky on phones.
  - "Click" copy is gone. A retry banner appears if the card data never loads.
  - The team chart draws narrower on phones. Org DNA folds each club's habits. Home has a "Your team" picker under the search.
- **Load speed.** The page's big data blocks now ship as `JSON.parse('...')` strings (`jsonparse_pass.py`, run after `regen_v3.py`), which V8 parses faster than object literals: about 0.3-0.4s off a mid-range phone's parse. Home also paints a static headline and placeholder tiles before the data arrives. Measured live before the change: first paint 0.6-0.9s; home tiles 3.0s on 4G and 7.9s on slow 4G (1.1MB compressed).
- **Elite-peak hitters (not shipped).** Tested a pull toward the best recent season for hitters with a 6+ WAR-per-600 season in the last four and a sub-2.5 last season (95 cases, 2018-26, under-projected by 0.24 WAR). Picking the weight walk-forward made it worse (RMSE 1.651 to 1.671), so the projection is unchanged (`peak_bt.py`).

## Home page consolidated, Trade Grade (November 9, 2026, late)

- **One place for each thing.** Home now runs: the headline with search, your team and the counts (trades, free-agent signings, draft picks and regimes graded, each summed from the data); **Today** (trade of the day, signing of the day, Trade Grade, rivalry of the day, tree of the day); **The rankings and this winter** (leaderboard top five, top free agents with the posted players, 2031 outlook, top prospects); **Play GM** (simulator, Deal Desk, scenario room); **Explore** (heists, transaction trees, champions, Org DNA). The heist of the day, the separate "on this date" card and the draft steal are folded into the trade of the day; the club buttons at the bottom are gone (the Your team picker sits under the search).
- **Trade and signing of the day.** The most lopsided trade (4+ wins apart) and the biggest signing (3+ wins either way) made on today's date in past years; when there is none on the date, the biggest within a week either side ("this week in history").
- **Trade Grade.** The daily game's new name (nav, page, share text, saved image). Its share link is `play/trade-grade`; `play/who-won` still works.
- **Org DNA.** No club buttons: every club's card shows, and the leaders strip scrolls to a club instead of filtering.

## Home page, second pass; a club's page is its report card (November 9, 2026, night)

- **Picking a club** (home, the phone bar, or a shared `t/<club>` link) opens that club's report card, the same one the leaderboard opens. Above the channel charts it now carries where the front office stands: its five leaderboard neighbors, its spot among the 28 graded front offices, the next five years, and Run the winter / Make a trade / Save card image. Archive regimes don't get this section.
- **Home, Today:** the trade of the day links to all the heists; the tree of the day links to all transaction trees; the rivalry reads as two front offices ("Erik Neander's Rays vs. Andrew Friedman's Dodgers").
- **Home, the rankings and this winter** (three across): leaderboard; the 2027 title race (the five clubs with the most projected 2027 WAR under control, against a champion line: the median WAR the 2012-2026 title teams got from their top 16 players, 2020 left out); how the latest champion was built; top free agents with the posted players; top prospects; Org DNA's best drafters.
- **Home, Play GM and Explore** are one wide panel of links: run a winter, price any trade, the scenario of the day; report cards, head to head, the 5-year horizon, how it works. Nothing on home appears twice.

## Home page, third pass (November 9, 2026, night)

- **Four rows.** Today (trade of the day, signing of the day, Trade Grade, tree of the day, and the champions tile, which stays put rather than rotating); The rankings and this winter (leaderboard, 2027 title race, top free agents, top prospects and farm systems); Play GM (simulator, Deal Desk, scenario room); Around the league (an organization stat of the day rotating through the Org DNA leaderboards, and the GM rivalry of the day).
- **Free agents tile:** each player's Ledger offer beside his projected contract (the median of published predictions), with a link to every projected contract.
- **Prospects tile:** the top five prospects beside the top five farm systems (same order as the boards).
- **2027 title race** opens the all-30 horizon view, not your own club's. The horizon table, sorted by 2027, now draws the champion line (49 WAR); no club clears it yet, and the row says which club is closest. Each club's horizon page notes the line on its 2027 row.
- **Signings in plain words** (home's signing of the day and the heists page's signings list): what the player gave the club, what that money usually buys, and the difference, then one sentence on where the second number comes from: the salary paid over the seasons played so far, the price of a win on the open market that winter (salary paid divided by its wins of cost), and what signings like it usually return, counting the draft pick for qualifying-offer signings.

## No remembered club (November 9, 2026, night)

- **The site no longer remembers a club.** Earlier versions saved the last club picked and opened the Deal Desk, the simulator, the horizon and the report cards on it. Every tool now opens neutral. A pick saved by an earlier version is cleared on the first visit.
- **Jump to a club** on home and **Clubs** on the phone bar open a club's report card; nothing is stored.
- **Run the winter / Make a trade** on a report card open the simulator or the Deal Desk on that club for that click only.

## The Wire: every move of the winter, graded as it happens (November 9, 2026, night)

- **What it is.** A live feed of every transaction since November 1, read straight from the league's public transaction feed in the visitor's browser and refreshed every two minutes. Nothing runs on a server.
- **Trades** are graded from both seats with the Deal Desk's accounting: each player's surplus over his remaining control, net of salary, weighted for where the club stands; prospects at their rank or comparables expectation; players not on our boards at the unranked-prospect expectation. The letter ranks the deal among every real trade of its size since 1998. Deals with under half a win at stake either way are labeled depth deals and get no letter.
- **Signings** are graded once terms are reported (wire.json, or typed in by the reader): projected WAR against what a typical club gets back for that money in those contract years, minus the draft pick for a qualifying-offer player. The player's side compares his deal with the Ledger's number for him. Before terms are out, the card shows the Ledger's number.
- **Qualifying offers.** A QO player signing back with his own club before the deadline is read as the acceptance; signing elsewhere, or no acceptance by 4pm ET November 17, is read as a decline. Readers can call each decision in advance.
- **Waiver claims** are graded on the claimed player's surplus over his control (a claim costs only a roster spot). Releases, DFAs and 40-man additions show the player's projection or prospect peak.
- **The winter so far** adds up each club's graded moves.
- **Sharing.** Every move has its own link, a Post on X button with the grades, a reply-to-a-post button, and a saved image.
- **Trade Grade** now counts days in a row played.

## The Wire as deal screens; home consolidated (November 9, 2026, late)

- **Every real trade on the Wire carries the Deal Desk's sheet**: what each club gets with salary, control and 2027 projection, net to each seat, the letter, the market check against deals of the same shape, comparable trades and both front offices' records (folded). The wire's letters are computed the same way as the sheet's, so they always match. Players not on our boards come along as pieces valued as unranked prospects, so "Rework it in the Deal Desk" opens the whole deal.
- **Signings with terms carry the free-agent sheet** (what he brings by season, cost in wins, comps, payroll before and after). Signings without terms show the player's last three seasons, his 2027 projection, the Ledger's number and the projected contract. Claims, releases and DFAs show the same player line.
- **QO poll.** One call per browser per player, pooled in a public counter (two tallies per player, nothing personal). After voting you see how everyone called it and the Ledger's read; votes are locked once cast.
- **Copy link** copies the link alone on desktop (phones still use the share sheet).
- **Trade Grade** can be walked back through after finishing, without changing the day's result.
- **Home** is three blocks: the Wire with a Play today rail (Trade Grade, the QO poll, the simulator, the Deal Desk, the scenario), the rankings and this winter (four even tiles; free agents trimmed to one line each), and From the archive (trade and signing of the day, then tree, champions, org stat and GM rivalry as one list).

## Ranking by net wins a season; contract projections and free agent pick'em (November 9, 2026, late night)

- **Leaderboard order.** The overall ranking is now the composite's net wins a season, continuous: every channel's net weighted by how much it repeats, divided by seasons in the seat plus two average seasons (so one hot year cannot top the board). Before, regimes were grouped by letter and ordered by total net inside each letter, which rewarded long tenures; letters are unchanged. The leaderboard shows each regime's plain net wins a season under its bar. Effect at the top: Matt Arnold (MIL) moves from 7th to 3rd and Peter Bendix (MIA) from 9th to 4th; Antonetti and Friedman stay 1-2.
- **Home leaderboard tile** shows each GM's net wins a season and the channel that produced the most wins, in place of the letter.
- **Every projection on a free agent.** Signings, players electing free agency and QO decliners on the Wire show the Ledger offer, the published projections median, the market model, the model-fair offer, the nearest comps, the crowd's median and your own call; once terms are public each is shown against the actual AAV.
- **Free agent pick'em.** For the top 20 free agents by the Ledger's number: over or under that number on total guarantee, then an exact prediction (years and total). Pooled in the same public counter as the QO poll: over/under tallies, and histograms of predicted years and AAV, from which the crowd's median deal is read. Resolved when he signs. "Your calls" scores your QO calls, over/unders and exact predictions (average miss a year against the Ledger's).
- **Home** puts From the archive above the rankings.
- **Who has won the offseason** moved up: first on the Wire's side column and under the Wire on home. Each club opens to its graded moves (each links to the move) and to every move it made this winter. The side column no longer sticks while scrolling, so the QO poll and pick'em scroll normally.
