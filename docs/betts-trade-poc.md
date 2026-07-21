# Proof of Concept: Scoring the Mookie Betts Trade
### Front Office Ledger methodology, applied to a real decision · July 2026 · **rev. 2 — retention-rights accounting**

## The lens stack (perspective rule: rev. 3)

A trade transfers more than control windows: it transfers the **exclusive right to extend the player**. Pricing that right at zero produces the skewerable headline ("Boston won the trade!") that rev. 1 of this document flirted with. What Betts did after re-signing has to count somewhere, and the methodology now says exactly where: on LA's ledger as **realized option value**, on Boston's as **p-weighted regret**.

**Perspective rule (added in rev. 3):** every lens on a regime's card is signed from that regime's seat. This decision lives on Friedman's card, so its lenses read from Los Angeles; Boston's side of the same deal grades on Boston's card (Bloom regime), against Boston's own alternative. Lens names use words, not letter-dash codes, so nothing reads as a minus sign.

The Dodgers' card (Friedman regime):

| Lens | Question it answers | Verdict |
|---|---|---|
| **Windows only** | Did the control years alone pay for themselves? | **LAD −$96M** (an overpay on windows alone; real, and shown) |
| **Option inclusive** (the headline) | Counting the extension right the trade delivered and LA exercised (+$141M realized, accruing through 2032)? | **LAD +$45M**, plus 3 WS titles |
| **Versus passing on the deal** | Against no 2020 Betts and bidding on him in open-market FA at ~zero expected surplus? | **LAD clearly ahead**: nearly all the option value is real gain |

Boston's card (same deal, their seat): windows surplus of ≈ +$96M against a realistic alternative of one walk year plus a comp pick, minus p(retain) × forfeited extension surplus. At the documented p = 0.30, **Boston beat its alternative by ≈ +$62M**; the decision only grades negative there if p(retain) exceeded ~0.85.

Ledger A components: LAD received one arbitration year of Betts (3.7 bWAR, ≈+$20M) plus the Price obligation (≈−$24M net of Boston's $48M cash); Boston received five control years of Verdugo (≈10.3 WAR, ≈+$70M), Wong (≈+$28M and open), and Downs (bust, ≈−$5M). Ex-ante the same ledger read ≈−$63M — the market scored it a Boston asset win at the time, and the realized gap (−$33M) roughly nets Wong's overperformance against Downs' bust.

**The retention parameters are published judgments, not hidden ones.** p(retain) = 0.30 reflects the documented 2019 negotiation (Boston ~10/$300M, Betts countering near ~12/$420M and publicly committed to testing the market); the 80% haircut on Boston's counterfactual surplus reflects that Boston would likely have paid open-market terms without LA's COVID-window timing and deferral structure. The sensitivity table runs p from 0 to 1: **Boston's decision only grades negative if you believe p(retain) exceeded ~0.85** — i.e., that Betts was overwhelmingly likely to re-sign in Boston. Nobody credible believed that in February 2020.

## The verdict, skewer-proofed

Once retention rights are priced, the deal stops being zero-sum. **Boston maximized a depreciating asset it had already decided not to pay** — nearly $100M of windows surplus against a realistic alternative of a walk year plus a comp pick. **Los Angeles bought an option and exercised it brilliantly** — option-inclusive net +$45M and climbing, with the extension itself (+28 WAR, ≈+$141M surplus so far, seven years left) standing as its own separately-graded decision. Both front offices beat their alternatives. That's the honest answer, it's more interesting than a scoreboard, and each ledger is one click from its assumptions.

## Methodology rules this generalizes to

**Retention rights on every trade.** Any traded player's page carries the option ledger; if the acquirer extends him, realized extension surplus flows into Ledger B and into the seller's p-weighted opportunity line. The p parameter is set per case from documented negotiation context, versioned, and exposed — the site should let readers drag the slider and watch the verdict move.

**Passive retention failures too.** The same machinery scores the *non-trade*: a team that lets a star reach free agency and walk gets charged p × (extension surplus a realistic deal would have carried) on its passive ledger — with the comp pick credited. Boston 2019 (keeping Betts, then trading him) and Washington 2021–22 (trading Soto with 2.5 years left) become directly comparable decisions.

**FA and extensions are always net-of-cost.** No raw WAR accumulation anywhere a contract exists: a signing's displayed value is realized WAR minus the WAR its price implied (surplus dollars alongside). Signing a star who then plays like a star is a *pass*, not a win; found-money channels (waivers, minor-league deals) keep their zero baseline, which is why Muncy-type finds grade enormous while Freeman-type signings grade merely solid. This was already how the Elias FA channel was scored; it is now the display rule everywhere, including extensions like Betts' (+28.1 raw WAR → **+15.9 net of the ~$110M paid so far**).

## Data provenance & caveats

Verified via public coverage: Betts' 3.7 bWAR 2020 and "4.0+ every season since" ([Dodgers Nation retrospective, Feb 2026](https://dodgersnation.com/dodgers-trade-for-mookie-betts-revisited-6-years-later/2026/02/04/)); Price's 3.47 ERA / 79 G over 2021–22 (same source); extension terms and season arcs ([Wikipedia: Mookie Betts](https://en.wikipedia.org/wiki/Mookie_Betts), [Alex Verdugo](https://en.wikipedia.org/wiki/Alex_Verdugo), [Connor Wong](https://en.wikipedia.org/wiki/Connor_Wong)). Remaining per-season bWAR values are approximate (±~0.5) and flagged in the script; market $/WAR uses published estimates. Postseason value excluded (would further favor LA). Programmatic access to B-Ref/FanGraphs is blocked (403) for unlicensed scripts — production requires a data license or self-computed open WAR from Retrosheet/Statcast; the MLB Stats API remains available for transactions and drafts.
