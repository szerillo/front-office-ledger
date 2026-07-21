# Methodology v0.2 — Win-Curve Leverage & Time Discounting
### Addendum: what changed, and what it did to our two case studies

## The two upgrades

**Win-curve leverage.** Championship probability is nonlinear in wins, so a marginal win is worth far more at 89 projected wins than at 70 or 105. Every acquired asset's WAR is now multiplied by L(w) = 0.5 + 1.3·exp(−(w−89)²/200), where w is the acquirer's *projected wins at the decision date* — the front office is graded on the leverage it thought it was buying. The curve peaks at 1.80 (89 wins), reads ~1.44 at 81 or 97, ~1.0 at 75 or 103, floor 0.5. A documented v0.2 choice: acquired WAR carries the acquirer's decision-time leverage; surrendered WAR is priced at neutral 1.0 (you sold it to the market — what the buyer does with it is their ledger). The alternative (counterfactual own-team leverage on surrendered assets) is queued for v0.3 alongside roster-block discounts.

**Time discounting.** Future-year value discounts to the decision date at 10%/yr (sensitivity at 6% and 14%). Win-now is not a bias to correct — it's a rational preference the ledger must price. A 2029 Joey Ortiz win was never worth a 2024 Corbin Burnes win to a defending division champion.

## Case 1: the Burnes trade flips

| | v0.1 | v0.2 |
|---|---|---|
| Burnes rental year (+ comp pick) | +4.4 | **+7.6** (L=1.80 at BAL's ~89-win projection) |
| Ortiz + Hall + pick #34 out | −6.9 | −6.3 (2029 wins discounted to 2024) |
| **Net** | **−2.9 — "worst decision of the tenure"** | **+1.2 — a fair price for a pennant push** |

Robust across discount rates (+1.1 at 6%, +1.4 at 14%). The window stays open — Ortiz is controlled through 2029 — but the deal now has to deteriorate much further before the *decision* grades negative. This is the methodology correcting itself in the right direction: v0.1 systematically punished buy-side deadline moves and flattered sell-side hauls (the same bias, in both directions). v0.2 also discounts the Orioles' 2025 sell-off returns — the honest cost of selling is that the value arrives late.

Knock-on: the Elias trade channel rises from +12.7 to ~+16.8, the composite from +51.1 to ~+55. FOR stays A; the FA channel stays D+ — leverage doesn't rescue bad signings, and in fact the 2023–24 *inaction* winter now looks worse, since the wins not bought were peak-leverage wins (the #4 "inaction ledger" upgrade will quantify that).

## Case 2: both Betts headlines move toward common sense

| Ledger (2020 present value) | v0.1 | v0.2 |
|---|---|---|
| A — windows only | −$96M | **−$59M** |
| B — option-inclusive (LAD) | +$45M | **+$106M** |
| of which the exercised extension option | +$141M | +$166M |

Leverage narrows Ledger A: Betts' wins arrived at a ~97-win team's 1.44 leverage while the surrendered package sold at neutral. Discounting then compounds Ledger B: the extension's 2021–25 surpluses, leveraged at a perennial contender (~1.3), dominate even in 2020 present value. Not one bWAR input changed. Boston's counterfactual break-even p(retain) rises above ~0.9 — the trade grades well for Boston only against its own realistic alternative, and spectacularly for LA on the option ledger.

## Parameters (all versioned, all public)

Leverage curve center 89 / width 10 / amplitude 1.3 / floor 0.5; discount rate 10% (6–14% sensitivity); decision-time projected wins per case (BAL 2024: ~89; LAD 2020: ~97; LAD in-extension-window: 1.3 flat). Every one is a judgment the methodology page must defend — and every verdict that depends on one should expose it, slider-style, the way p(retain) already does.

*Engine: `methodology_v02.py` (self-contained, runs both cases with before/after). bWAR inputs remain approximate ±0.5 as in v0.1.*
