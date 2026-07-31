# Methodology v0.3: The Empirical Rental Market

*Front Office Ledger, sweep v2 data, July 2026*

## The question

Every deadline argument eventually reduces to "but what did one year of that
player actually cost?" Until now the ledger answered with a lens stack:
window-for-window value, option-inclusive value, the seller's counterfactual.
v0.3 replaces intuition with a fitted market: the observed price of rental
production, measured from 237 classified deadline rental deals in the
transaction archive.

## Classification

A rental is defined exactly, not by service-time guesswork: a player acquired
in a June 1 to August 31 trade who appears in the league transaction feed as
**Declared Free Agency within five months of the deal**. The buyer's receipt
is the player's Ledger WAR on the buying club in the deal season (season
splits are per-team, so this isolates rest-of-season production). The price
is the surrendered players' control-window value realized on the selling
club: not prospect-list hype, what the pieces actually became.

## The fitted market

| Era | Deals | Fit sample | Wins paid per rental win (pooled) | Bust rate |
|-----|-------|-----------|------------------------------------|-----------|
| 2005-2011 | 6 | 3 | ~0 (sample too small) | 50% |
| 2012-2016 | 16 | 8 | 1.29 | 47% |
| 2017-2021 | 89 | 41 | 0.86 | 51% |
| 2022-2025 | 126 | 46 | 0.33* | 62% |
| Star rentals (>=1.5 wins delivered), all eras | 8 | 8 | 0.79 | n/a |

*The 2022-2025 ratio is right-censored: surrendered prospects from recent
deadlines are still accruing value on their new clubs, so the true ratio
will drift up as those windows mature. The 2017-2021 era is the cleanest
read.*

## Three findings

**1. A star rental win costs about 0.8 realized wins.** Across the star
segment of the market (J.D. Martinez 2017, Machado 2018, Montgomery 2023),
buyers surrendered roughly 0.8 wins of eventually-realized value per win the
rental delivered. Rentals are not free, but they are systematically cheaper
than the anguish suggests.

**2. The median deadline rental costs approximately nothing.** The median
paid/received ratio is near zero in every era, because most surrendered
packages never produce for the seller. More than half of all rental
acquisitions also deliver under 0.3 wins to the buyer. The deadline is a
lottery on both sides of the table, and the market prices it that way.

**3. Sellers should expect lottery tickets, not value.** The bust rate on
what sellers receive is the mirror of finding 2. A seller who converts a
rental into ANY realized value beat the median outcome. This is why the
ledger's trade channel credits sellers only for what returns actually
became, and why "they only got prospects" is not, by itself, a criticism.

## Consolidating the lens stack

With a market price in hand, a trade grades on two questions instead of
four lenses:

- **Paid vs the market at the time.** Given the expected rental (or
  controlled-year) wins changing hands, did the club pay above or below the
  fitted ratio for that era and segment?
- **Realized vs paid.** Did the wins actually show up?

Applied to the canonical case: Boston received Verdugo, Downs, and Wong for
one expected season of Mookie Betts (~6.5 projected wins, star segment). At
the star-market ratio of ~0.8, the market price for that year was roughly 5
wins of eventually-realized value; the package delivered in that range.
**Boston sold at market rate. The ledger's criticism was never the price:
it is the decision to be a seller of that asset at all, and what the
counterfactual of extending him was worth.** The lens stack said this in
four exhibits; the market baseline says it in one sentence.

## What v0.3 does not change

Sweep grading is unchanged: channels still grade realized value vs
expectation with control windows, leverage, and discounting (sweep v2). The
rental baseline is a pricing reference that decision pages and curated cards
cite, and the foundation for the eventual controlled-years market (the same
method applied to non-rental deadline deals, where the prospect-rank archive
prices the surrendered side at deal time instead of in hindsight).

## Data

`engine/rental_baseline.py`, `data/rental_market.json` (all 237 classified
deals included, with buyer, season, receipt, and price). Sample skews toward
recent seasons because the archive covers current regime windows; the
pre-2012 market is under-sampled and reported only for completeness.
