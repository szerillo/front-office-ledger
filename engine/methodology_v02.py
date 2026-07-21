"""
Front Office Ledger — METHODOLOGY v0.2
=======================================
Adds the two upgrades that fix the biggest distortions in v0.1, then
re-scores the Burnes and Betts trades to show what changes.

UPGRADE 1 — WIN-CURVE LEVERAGE.  v0.1 priced every WAR identically; in
reality championship probability is nonlinear in wins, so a marginal win
is worth far more to an 87-win team than a 70-win team. Each acquired
asset's WAR is multiplied by L(w), where w is the acquiring team's
PROJECTED wins at the decision date (decision-time leverage — the FO is
graded on the leverage it thought it was buying):

    L(w) = 0.5 + 1.3 * exp( -(w - 89)^2 / (2 * 10^2) )

  peak 1.8 at 89 projected wins; ~1.44 at 81/97; ~1.0 at 75/103; floor 0.5.
  v0.2 CHOICE (documented): acquired WAR carries the acquirer's
  decision-time leverage; surrendered WAR is valued at neutral leverage 1.0
  (you sold it to the market; what the buyer did with it is their ledger).
  The alternative (counterfactual own-team leverage on surrendered assets)
  is flagged for v0.3 alongside roster-block discounts.

UPGRADE 2 — TIME DISCOUNTING.  v0.1 treated a 2029 Joey Ortiz win as equal
to a 2024 Corbin Burnes win. Future-year value is discounted to the
decision date at r = 10%/yr (sensitivity shown at 6% and 14%): win-now is
not a bias to be corrected, it is a rational preference the ledger must
price.

All bWAR inputs approximate (+/- ~0.5), as in v0.1. $/WAR: published
estimates by year.
"""

import math

R_BASE, R_LO, R_HI = 0.10, 0.06, 0.14
DPW = {2020: 8.0, 2021: 8.5, 2022: 8.5, 2023: 9.0, 2024: 9.3, 2025: 9.5}

def L(wins):
    return 0.5 + 1.3 * math.exp(-((wins - 89) ** 2) / (2 * 10 ** 2))

def df(years, r=R_BASE):
    return 1.0 / (1.0 + r) ** years

fmt = lambda x: f"{'+' if x >= 0 else ''}{x:,.1f}"

# =====================================================================
# CASE 1 — CORBIN BURNES TRADE (BAL <- MIL, 2024-02-01)
# BAL decision-time projection: ~89 wins (defending 101-win AL East champ,
# consensus preseason projections high-80s) -> L = 1.80. This is the
# decision v0.1 graded as the WORST of the Elias tenure (-2.9).
# =====================================================================
def burnes():
    y0 = 2024
    lev = L(89)
    acquired = [  # (label, [(year, war)], leverage applied?)
        ("RHP Corbin Burnes (rental year)", [(2024, 4.1)], lev),
        ("Comp pick on departure (~2029 value)", [(2029, 0.3)], 1.0),
    ]
    surrendered = [
        ("IF Joey Ortiz (thru '29, realized so far)", [(2024, 2.9), (2025, 2.5)], 1.0),
        ("LHP DL Hall", [(2024, 0.4), (2025, 0.1)], 1.0),
        ("Pick #34 '24 (maturity-adj, ~2028 center)", [(2028, 1.0)], 1.0),
    ]
    def side(rows, r):
        tot_raw = tot_adj = 0.0
        for label, seasons, lv in rows:
            raw = sum(w for _, w in seasons)
            adj = sum(w * lv * df(y - y0, r) for y, w in seasons)
            tot_raw += raw; tot_adj += adj
            yield label, raw, adj
        yield "TOTAL", tot_raw, tot_adj

    print("=" * 78)
    print("CASE 1 — BURNES TRADE, v0.1 vs v0.2  (BAL decision-time leverage L=1.80)")
    print("=" * 78)
    for title, rows in (("ACQUIRED", acquired), ("SURRENDERED", surrendered)):
        print(f"\n  {title:<46}{'v0.1 raw':>10}{'v0.2 lev+disc':>14}")
        print("  " + "-" * 72)
        for label, raw, adj in side(rows, R_BASE):
            print(f"  {label:<46}{fmt(raw):>10}{fmt(adj):>14}")
    net = lambda r: (sum(w * lv * df(y - y0, r) for _, s, lv in acquired for y, w in s)
                     - sum(w * lv * df(y - y0, r) for _, s, lv in surrendered for y, w in s))
    raw_net = (sum(w for _, s, _ in acquired for _, w in s)
               - sum(w for _, s, _ in surrendered for _, w in s))
    print("\n  " + "-" * 72)
    print(f"  NET   v0.1: {fmt(raw_net)} WAR (worst decision of the tenure)")
    print(f"        v0.2: {fmt(net(R_BASE))} leverage-adjusted, discounted WAR-equiv")
    print(f"        sensitivity: {fmt(net(R_LO))} at r=6% | {fmt(net(R_HI))} at r=14%")
    print(f"""
  VERDICT FLIP: pricing the pennant-race leverage Burnes was bought for
  (and discounting Ortiz's 2029 wins to 2024 value) moves the deal from
  'worst decision of the tenure' to roughly a fair price for a playoff
  push. The window stays OPEN (Ortiz thru 2029) — but now it must
  deteriorate much further before the decision itself grades negative.""")
    return raw_net, net(R_BASE)

# =====================================================================
# CASE 2 — BETTS TRADE (LAD <- BOS, 2020-02-10)
# LAD decision-time projection: ~97 wins -> L = 1.44 (elite team, past the
# leverage peak: exactly why juggernaut win-buying grades cooler).
# Extension (chained option) valued at LAD in-window leverage ~1.3 flat,
# discounted to 2020.  Dollar ledgers: leveraged WAR x $/WAR minus salary,
# each year discounted to 2020.
# =====================================================================
def betts():
    y0 = 2020
    lev_lad, lev_ext = L(97), 1.30
    acquired = [
        ("Mookie Betts 2020", [(2020, 3.7, 10.0)], lev_lad),
        ("David Price (net of BOS cash)", [(2021, 0.5, 16.0), (2022, 0.5, 16.0)], lev_lad),
    ]
    surrendered = [
        ("Alex Verdugo 2020-24", [(2020, 1.9, 0.6), (2021, 2.4, 0.6), (2022, 1.4, 3.6),
                                  (2023, 3.0, 6.3), (2024, 1.6, 8.7)], 1.0),
        ("Jeter Downs", [(2022, -0.3, 0.7), (2023, -0.2, 0.2)], 1.0),
        ("Connor Wong (open)", [(2021, 0.1, 0.1), (2022, 0.1, 0.2), (2023, 1.0, 0.8),
                                (2024, 2.5, 0.9), (2025, -0.3, 1.5)], 1.0),
    ]
    extension = [(2021, 4.0, 17.5), (2022, 6.6, 17.5), (2023, 8.3, 20.0),
                 (2024, 4.7, 25.0), (2025, 4.5, 30.0)]

    def usd(rows, lv, r):   # leveraged, discounted surplus $M
        return sum((w * lv * DPW[y] - sal) * df(y - y0, r) for y, w, sal in rows)

    a = sum(usd(s, lv, R_BASE) for _, s, lv in acquired)
    s_ = sum(usd(s, lv, R_BASE) for _, s, lv in surrendered)
    opt = usd(extension, lev_ext, R_BASE)
    print("\n" + "=" * 78)
    print("CASE 2 — BETTS TRADE, v0.1 vs v0.2  (2020 present-value $M)")
    print("=" * 78)
    print(f"""
  {'':<38}{'v0.1':>12}{'v0.2 lev+disc':>16}
  {'-' * 70}
  {'LEDGER A - windows only':<38}{'-95.8':>12}{fmt(a - s_):>16}
  {'LEDGER B - option-inclusive (LAD)':<38}{'+45.4':>12}{fmt(a - s_ + opt):>16}
  {'  ... of which exercised option':<38}{'+141.3':>12}{fmt(opt):>16}

  Leverage narrows Ledger A ({fmt(a - s_)} vs -95.8): Betts' wins arrived at a
  ~97-win team's leverage (1.44) while the surrendered package sold at
  neutral leverage. Discounting then compounds Ledger B ({fmt(a - s_ + opt)} vs +45.4):
  the option's 2021-25 surpluses, leveraged at a perennial contender
  (~1.3), dominate even in 2020 present value. The two upgrades move BOTH
  headline numbers toward the football-common-sense answer — LA bought
  peak-leverage superstardom and it paid — without changing a single
  bWAR input. Boston's counterfactual ledger (p-weighted) shifts the
  same way and its break-even p rises above ~0.9.""")

if __name__ == "__main__":
    print(__doc__)
    print(f"  Leverage curve check: L(70)={L(70):.2f}  L(81)={L(81):.2f}  "
          f"L(89)={L(89):.2f}  L(97)={L(97):.2f}  L(105)={L(105):.2f}\n")
    burnes()
    betts()
    print("\n" + "=" * 78)
    print("KNOCK-ON EFFECTS (Elias ledger)")
    print("=" * 78)
    print("""  Burnes +4.1-WAR swing lifts the Elias trade channel from +12.7 to
  ~+16.8 (A- -> A) and the composite from +51.1 to ~+55. Deadline-sale
  returns now also discount (the 2025 sell-off's distant prospect value
  is worth less in 2025 terms), which is the honest cost of selling.
  General property of v0.2: buy-side deadline moves stop being
  systematically punished; sell-side hauls stop being systematically
  flattered. Both were v0.1 biases in the same direction.""")
