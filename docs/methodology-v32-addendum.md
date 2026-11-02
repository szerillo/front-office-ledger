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
data"; and the validation section opens by asking who watches the Watchmen.

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

**Why so many "partial" badges.** A channel letter needs evidence: 3 priced
free-agent deals, 2 extensions. The contract book is deep for the 2006-21
winters (about 90-110 major-league deals each) but holds only about 30 per
winter for 2022-25, so regimes hired since 2022 often lack a free-agent or
extension letter; the composite fills those at the league-average rate.
The free-agent evidence floor drops from 8 deals to 3 (the per-move letters
already carry the uncertainty). Filling the 2022-25 book from public
trackers is the next data task.

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
or younger. Contract backtest after the WAR rebuild: typical miss 0.65 years /
$2.9M AAV / $12.8M total; $50M+ offers at a median 100% of the real deal;
2021-25 market drift 14% over the published $/win curve.

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
top 45 free agents the median miss moves from 0.47 to 0.41 in log terms and
the median ratio from 0.95 to 1.03. Ryan Jeffers prices at 2 years / $29M
($14.5M AAV); the remaining gap to the public consensus (about four years)
is term: his 2026 was 92 games (fractured hamate), and catchers his age with
his blended platform have historically signed for two years.
