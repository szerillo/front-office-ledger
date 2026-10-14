# Methodology addendum: Ledger WAR v1.5 (park factors) + the Archive sweep

October 14, 2026. Two additions, both versioned here with what changed and why.

## 1. Park factors (Ledger WAR v1 -> v1.5)

### The factor

For every team-year 2004-2026 (`ingest/park_ingest.py`, output `data/parks.json`):

    raw PF = (home runs scored + home runs allowed, per home game)
           / (away runs scored + away runs allowed, per away game)

Both sides of the ball are included so the factor reads the park, not the roster.
The raw factor is smoothed with a 3-year centered rolling average (stability), then
halved toward 1:

    PF = 1 + (PF_3yr - 1) x 0.5

The halving is not regression for its own sake: a player plays roughly half his
games on the road in ~neutral aggregate parks, so the season-applicable factor is
the midpoint of the home factor and 1. This is the same convention that makes a
published "Coors 115" apply to all of a hitter's plate appearances.

Coverage: 690 team-years, mean 1.002 (the league is its own baseline, as it must
be). Sanity anchors: Coors 1.15-1.19 across eras, Fenway 1.01-1.10, Petco and
T-Mobile 0.91-0.97, extremes 0.88-1.23. Seasons before 2004 and any team-year
without 20+ home and road games use PF = 1 (disclosed).

### The application (FanGraphs-style)

Batting: the park gives or takes runs at the league scoring rate, so

    wRAA_adj = wRAA - (PF - 1) x lgRuns/PA x PA

A Coors hitter is docked what the park handed him; a Petco hitter gets it back.
Positional adjustment and replacement offset are park-free and unchanged.

Pitching: the FIP comparison to league is made park-neutral by

    FIP_adj = FIP / PF

so a Coors pitcher's 4.2 FIP reads as the ~3.5 it would be elsewhere. HR-driven
FIP is the component park moves most, which is why the simple divisor is the
standard treatment.

### Effects and validation

The full 25,589-player cache was rebuilt at v1.5 with the defense/baserunning
join reapplied once (`engine/lvm_v15_rebuild.py`; caches carry a `__lvm_v15__`
mark so the join can never double).

- Arenado's 2017-2019 Coors seasons: 8.2/8.0/7.9 -> 6.8/6.7/6.5 (fWAR had 5.6-7.0).
- German Marquez 2018: +1.2 wins of credit returned to a Coors pitcher.
- League-wide sum across the cache: 16,199 -> 16,212 wins, i.e. park adjustment
  is zero-sum to three significant figures, as it must be.

Validation (engine/validation.py, rerun on v1.5):

- Accounting check: park adjustment alone left team sums unchanged, as it
  must (it moves value between a club's hitters and pitchers). The final v3.1
  numbers then jumped to r = 0.861, R2 = 0.741, MAE 5.2 wins (from 0.804 /
  0.647 / 6.8) for a coverage reason: the archive sweep added ~12,800 role
  players to the value cache that current-regime windows had never needed,
  and fuller rosters sum closer to team records. Coverage improving the
  accounting check is itself evidence the metric is additive the way a
  WAR-class metric must be.
- Predictive check: partial r of decision value on future W% (controlling for
  record to date) finishes at 0.338, R2 0.282 -> 0.364, after the unsigned-pick
  screen and the coverage change (it had read 0.344 pre-v1.5 and 0.360 on the
  park-factor-only rerun; the final number is the one that ships).

## 2. The Archive sweep (71 historical regimes, 2005-2024)

`data/regimes_hist.json` curates 71 past regimes with start AND end dates;
`engine/hist_score.py` generalizes the sweep to bounded windows over the full
2005+ re-ingest of all 30 clubs (`ingest/hist_ingest.py`, 244k rows).

Window rules:

- A decision belongs to the regime whose window contains its date.
- Value realized AFTER the regime ends still credits the decision. Credit
  follows the decision-maker: if you drafted Posey, his 2012 belongs to your
  ledger even if you are gone. This is the same philosophy as the DEV pillar's
  traded-prospect rule and avoids the classic attribution error of crediting
  the successor with the predecessor's pipeline.
- Draft maturity reads as of 2026 for all regimes, so a 2005 draft class is
  fully mature and graded on what it became.
- Success (W%, division titles, postseason detail) counts only seasons the
  regime held the seat.

Channel coverage for archive windows: trades, drafts, waivers/Rule 5 grade
exactly as the active sweep. FA is shown raw and ungraded (the graded FA book
is built on the current-regime contract universe; the historical contract
backfill is the open item). DEV and extensions are not scored for past windows
(the Pipeline top-100 archive starts 2011 and the extension book covers active
windows). Every archive card discloses this on its badge.

Data floor: the transaction feed is reliable from 2005. Regimes seated earlier
(Epstein BOS 2002-11, Sabean SF 1996-09, Beane 1997-10) are truncated at
2005-01-01, flagged, and shown with their true start date on the card.

Headline results (net decision value over the window):

| Regime | Window | Trades | Draft | Total |
|---|---|---|---|---|
| Brian Sabean, SF | 2005-2018 | +59.7 | +127.3 | +191.0 |
| Theo Epstein, BOS | 2005-2011* | +23.1 | +62.6 | +85.1 |
| Theo Epstein, CHC | 2011-2020 | +53.8 | +28.9 | +83.6 |
| David Stearns, MIL | 2015-2022 | +75.5 | +27.5 | +98.2 |
| Jeff Luhnow, HOU | 2011-2020 | +0.9 | +60.7 | +78.3 |
| Dave Dombrowski, DET | 2005-2015 | +61.8 | +2.3 | +60.1 |
| Billy Beane, ATH | 2005-2015* | -40.1 | +3.3 | -32.2 |
| Jon Daniels, TEX | 2005-2020* | -46.2 | -65.9 | -113.4 |

(*truncated at the 2005 data floor.)

The Sabean draft room (+127 wins over slot: Posey, Bumgarner, Cain-era picks)
is the best of the data era, ahead of Cashman's +70 among active regimes. Late
Beane grades underwater on trades, a reminder that the archive floor cuts off
the Moneyball years; the flag on the card says exactly that.

Prototype: the leaderboard Era filter serves archive rows with full report
cards (channel ledgers, cumulative charts, transaction trees, walkaway lists).
Regeneration for both eras is `ingest/regen_v3.py`.

## 3. Retention v2 (expectation-conditioned; joins the composite)

Raw leakage scaled with stars employed, so v1 retention was display-only. v2
conditions on who left: from every free-agency departure league-wide
2005-2023 (3 observable future seasons), the empirical curve of next-3yr
value elsewhere given last-3yr value here:

    prior ~0.7 -> 0.74 expected    prior ~5.4 -> 2.08
    prior ~2.5 -> 1.25             prior ~10.8 -> 5.23

A regime is graded on SUM(expected - actual) over its material departures
(prior > 0.5), plus +1.0 win per qualifying-offer walkaway (the comp pick,
mirroring the QO charge on the signing club's FA ledger). League mean +0.1,
median +0.2: centered by construction, so it now joins the FOR composite
(`engine/ret2.py`, runs after archetype in the chain). Post-2023 departures
are right-censored and excluded, disclosed. Yankees +44 (their walkaways
underperform expectation: good exit timing); Dodgers -43 (their departures
keep outperforming what departures of that caliber usually do).

## 4. The controlled-years deadline market (methodology v0.4)

The complement of the v0.3 rental study: 1,372 deadline deals 2005-2023 where
acquired players carried control beyond the season, control measured from the
feed (seasons to first FA declaration, capped at 6). Price per win received,
by control bucket (`engine/controlled_market.py`, appended to
`data/rental_market.json`):

| Control | n | paid/received | bust rate |
|---|---|---|---|
| deal yr + 1 | 144 | 0.99 | 48% |
| deal yr + 2 | 70 | 0.86 | 39% |
| deal yr + 3+ (mostly prospect packages, the seller's seat) | 1,156 | 0.37 | 71% |

The deadline premium on controlled players is real and exceeds the 0.8
star-rental rate; sellers buy future wins at about a third of the price of
present ones and pay for the discount in variance.

## 5. Unsigned-pick screen (draft channel fix)

Found while reading the Yankees dossier: Gerrit Cole, drafted #28 by New York
in 2008, did not sign, and the draft channel was crediting his 2020+
free-agent-era Yankee production to the 2008 pick. The screen: a player who
appears in the draft table again in a LATER year by definition did not sign
the earlier pick, so the earlier pick's realized value is zero (any later
production with that club came through a different, separately graded
decision) and its slot charge is halved (the compensation pick an unsigned
early pick returns). Applied to both the active and archive sweeps.
