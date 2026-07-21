"""
Front Office Ledger — proof-of-concept decision scorer
=======================================================
Scores the Mookie Betts trade (Feb 10, 2020) under the Ledger methodology:

  * A DECISION is scored over the club-control windows exchanged on the date
    of the transaction. The Betts EXTENSION (July 22, 2020) is a SEPARATE
    decision — the trade bought one control year plus the exclusive
    negotiating window; the extension is scored on its own ledger.
  * Two currencies: WAR captured, and surplus dollars
    (WAR x market $/WAR in that season, minus salary actually paid).
  * Two ledgers: EX-ANTE (asset values as they were reasonably estimable on
    the transaction date) and EX-POST (realized to date). The gap is the
    luck-vs-skill diagnostic.

DATA PROVENANCE
  bWAR figures: Baseball-Reference values. 2020 Betts (3.7) and the
  "4.0+ every season since" anchor verified via Feb-2026 retrospective
  coverage; other season values are approximate (+/- ~0.5) pending a
  licensed or self-computed WAR feed — direct programmatic access to
  B-Ref/FanGraphs is blocked (403) from this environment, which is itself
  a key design-doc finding. Salary figures: publicly reported contract
  terms; market $/WAR: published estimates (~$8M in 2020 trending ~$9.5M
  by 2025). Every input is in the INPUTS block below — swap in exact
  values and rerun.
"""

# ---------------- reference: market $/WAR by season ($M) ----------------
DOLLARS_PER_WAR = {2020: 8.0, 2021: 8.5, 2022: 8.5, 2023: 9.0,
                   2024: 9.3, 2025: 9.5}

# ---------------- INPUTS ----------------
# Each asset: seasons in the control window exchanged in THIS decision,
# with (bWAR, salary paid $M by the controlling club that season).
# 'approx' flags values pending an exact feed.

TRADE = {
    "name": "Mookie Betts trade",
    "date": "2020-02-10",
    "teams": ("LAD acquires", "BOS acquires"),
    "acquired": {  # by LAD
        "Mookie Betts": {
            "window": "2020 (final arbitration year)",
            "seasons": {2020: dict(war=3.7, sal=10.0, note="$27M arb salary prorated to 60-game season", approx=False)},
            "flags": ["2020 World Series title", "exclusive extension window -> separate decision"],
        },
        "David Price": {
            "window": "2020-22 ($96M owed; BOS sent $48M cash)",
            "seasons": {
                2020: dict(war=0.0, sal=0.0, note="opted out; salary forfeited", approx=False),
                2021: dict(war=0.5, sal=16.0, note="net of BOS cash offset", approx=True),
                2022: dict(war=0.5, sal=16.0, note="net of BOS cash offset", approx=True),
            },
            "flags": ["3.47 ERA / 79 G across 2021-22 (verified); bWAR split approximate"],
        },
    },
    "surrendered": {  # to BOS
        "Alex Verdugo": {
            "window": "2020-24 (five control years; FA after 2024)",
            "seasons": {
                2020: dict(war=1.9, sal=0.6, approx=True),
                2021: dict(war=2.4, sal=0.6, approx=True),
                2022: dict(war=1.4, sal=3.6, approx=True),
                2023: dict(war=3.0, sal=6.3, approx=True),
                2024: dict(war=1.6, sal=8.7, note="traded to NYY; window value follows the asset", approx=True),
            },
            "flags": [],
        },
        "Jeter Downs": {
            "window": "2020-26 (six-plus control years)",
            "seasons": {2022: dict(war=-0.3, sal=0.7, approx=True),
                        2023: dict(war=-0.2, sal=0.2, note="20 MLB G total; DFA'd", approx=True)},
            "flags": ["ex-ante consensus top-50 prospect; realized bust"],
        },
        "Connor Wong": {
            "window": "2021-26+ (window still OPEN)",
            "seasons": {
                2021: dict(war=0.1, sal=0.1, approx=True),
                2022: dict(war=0.1, sal=0.2, approx=True),
                2023: dict(war=1.0, sal=0.8, approx=True),
                2024: dict(war=2.5, sal=0.9, approx=True),
                2025: dict(war=-0.3, sal=1.5, approx=True),
            },
            "flags": ["window open — value still accruing"],
        },
    },
    # EX-ANTE asset values on 2020-02-10, $M surplus (documented estimates):
    "ex_ante": {
        "Mookie Betts":  25,   # ~6.5 projected WAR x $8M minus $27M salary
        "David Price":  -12,   # ~4.5 projected WAR over 3y minus $48M net obligation
        "Alex Verdugo": -45,   # young cost-controlled ~2-3 WAR OF, 5 control years
        "Jeter Downs":  -28,   # consensus ~#44 overall prospect (FV50 hitter curve)
        "Connor Wong":   -3,   # FV40 catcher
    },
}

EXTENSION = {
    "name": "Mookie Betts extension (separate decision)",
    "date": "2020-07-22",
    "terms": "12 yr / $365M, 2021-2032, ~$115M deferred (PV ~ $306M)",
    "seasons": {   # realized 2021-2025; 7 years remain
        2021: dict(war=4.0, sal=17.5, approx=True),
        2022: dict(war=6.6, sal=17.5, approx=True),
        2023: dict(war=8.3, sal=20.0, approx=True),
        2024: dict(war=4.7, sal=25.0, approx=True),
        2025: dict(war=4.5, sal=30.0, approx=True),
    },
    "flags": ["WS titles 2024, 2025 inside window", "window open through 2032"],
}

# ---------------- RETENTION-RIGHTS / OPPORTUNITY-COST PARAMETERS ----------------
# A trade transfers more than the control window: it transfers the EXCLUSIVE
# RIGHT TO EXTEND the player. Pricing that right at zero is what produces the
# skewerable headline "Boston won the trade." Parameters (documented judgments,
# methodology-versioned):
RETENTION = {
    # Probability Boston retains Betts had they kept him through 2020.
    # Context: BOS reportedly offered ~10/$300M in 2019; Betts countered near
    # ~12/$420M and was publicly committed to testing free agency.
    "p_retain_grid": [0.0, 0.25, 0.50, 0.75, 1.0],
    "p_retain_est": 0.30,
    # Haircut on the surplus Boston would have realized relative to LAD's
    # actual deal: no exclusive pre-FA window at COVID-depressed terms, no
    # equivalent deferral structure, likely bidding against the open market.
    "boston_surplus_haircut": 0.80,
}

# ---------------- ENGINE ----------------
def value(seasons):
    war = sum(s["war"] for s in seasons.values())
    sal = sum(s["sal"] for s in seasons.values())
    dollars = sum(s["war"] * DOLLARS_PER_WAR[y] for y, s in seasons.items())
    return war, dollars, sal, dollars - sal

def side_total(side):
    rows = []
    for name, a in side.items():
        war, gross, sal, surplus = value(a["seasons"])
        rows.append((name, a["window"], war, gross, sal, surplus, a["flags"]))
    return rows

def fmt(x): return f"{'+' if x >= 0 else ''}{x:,.1f}"

def report(trade, ext):
    W = 78
    print("=" * W)
    print(f"DECISION: {trade['name']}  ({trade['date']})")
    print("=" * W)
    net_war, net_sur = 0.0, 0.0
    for label, side, sign in (("ACQUIRED (LAD)", trade["acquired"], +1),
                              ("SURRENDERED (to BOS)", trade["surrendered"], -1)):
        print(f"\n{label}")
        print(f"  {'asset':<16}{'control window':<40}{'WAR':>6}{'surplus $M':>12}")
        print("  " + "-" * (W - 4))
        for name, window, war, gross, sal, surplus, flags in side_total(side):
            print(f"  {name:<16}{window:<40}{fmt(war):>6}{fmt(surplus):>12}")
            for f in flags:
                print(f"  {'':<16}  * {f}")
            net_war += sign * war
            net_sur += sign * surplus
    print("\n" + "-" * W)
    print(f"EX-POST (realized through 2025):  net {fmt(net_war)} WAR, "
          f"net {fmt(net_sur)} $M surplus to LAD   [Wong window still open]")
    ea = trade["ex_ante"]
    ea_net = sum(ea.values())
    print(f"EX-ANTE (Feb 2020 asset ledger):  net {fmt(ea_net)} $M to LAD")
    print(f"PROCESS-VS-LUCK GAP:              {fmt(net_sur - ea_net)} $M "
          f"(outcome vs. at-the-time expectation)")

    print("\n" + "=" * W)
    print(f"CHAINED DECISION: {ext['name']}  ({ext['date']})")
    print("=" * W)
    war, gross, sal, surplus = value(ext["seasons"])
    print(f"  Terms: {ext['terms']}")
    print(f"  Realized 2021-25: {fmt(war)} WAR, {fmt(surplus)} $M surplus; "
          f"7 seasons remain")
    for f in ext["flags"]:
        print(f"    * {f}")

    print("\n" + "=" * W)
    print("RETENTION RIGHTS & OPPORTUNITY COST (the ledger that stops the skewering)")
    print("=" * W)
    print("""  The trade transferred a third asset the windows-only ledger prices at
  zero: the EXCLUSIVE RIGHT TO EXTEND Betts. LA exercised it. So the trade
  is scored three ways, and all three are shown:""")
    opt_realized = surplus  # extension surplus realized to date (option exercised)
    print(f"\n  DODGERS CARD, lens 1 (windows only):      net {fmt(net_sur)} $M to LAD")
    print(f"  DODGERS CARD, lens 2 (option inclusive):  net {fmt(net_sur + opt_realized)} $M to LAD")
    print(f"      (windows {fmt(net_sur)} + exercised retention option "
          f"{fmt(opt_realized)}, still accruing thru 2032)")
    p0, hc = RETENTION["p_retain_est"], RETENTION["boston_surplus_haircut"]
    print(f"\n  BOSTON'S CARD (same deal, their seat): their alternative wasn't 'keep the")
    print(f"  surplus for free' — it was 1 yr of Betts + a comp pick + a p-weighted")
    print(f"  chance of extending him themselves (haircut {hc:.0%} for worse terms):")
    print(f"\n      {'p(retain)':>10}{'BOS forfeited option':>22}{'BOS net vs alternative':>24}")
    for p in RETENTION["p_retain_grid"]:
        opp = p * hc * opt_realized
        print(f"      {p:>10.2f}{fmt(opp):>22}{fmt(-net_sur - opp):>24}")
    opp0 = p0 * hc * opt_realized
    print(f"\n      documented estimate p = {p0:.2f} -> BOS net "
          f"{fmt(-net_sur - opp0)} $M vs. its realistic alternative")
    print("\n" + "=" * W)
    print("VERDICT (all three ledgers on the page)")
    print("=" * W)
    print(f"""  Boston maximized a depreciating asset it had already decided not to pay:
  {fmt(-net_sur)} $M of windows surplus against a realistic alternative of one walk
  year plus a comp pick. Los Angeles bought an option and exercised it
  brilliantly: option-inclusive net {fmt(net_sur + opt_realized)} $M and climbing, plus three
  World Series titles. Once retention rights are priced, the deal stops
  being zero-sum — BOTH sides beat their alternatives unless p(retain)
  exceeds ~{(-net_sur)/(hc*opt_realized):.2f}. What Betts did after re-signing counts: on LA's
  ledger as realized option value, on Boston's as p-weighted regret.""")

if __name__ == "__main__":
    report(TRADE, EXTENSION)
