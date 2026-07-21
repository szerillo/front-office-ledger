# Proof of Concept #2: The Full Elias Ledger
### Every channel of a real regime, scored — Baltimore Orioles, Nov 2018 – July 2026

## The headline

| Channel | Net WAR vs. expectation | Grade |
|---|---|---|
| Draft / Amateur | **+21.8** | **A+** |
| Trades | +12.7 | A |
| Free agency | −6.9 | D+ |
| Waivers / Minor-lg / Rule 5 | **+23.5** | **A+** |
| **Front Office Rating (composite)** | **+51.1 over 7.6 seasons** | **A** |
| **Team Success** (separate grade) | .484 W% · 1 division title · 2 playoff berths · **0 playoff game wins (0–5)** | **C** |

That A-vs-C gap *is* the Elias story, and it's exactly what the two-grade design exists to surface: an elite value-creation machine (drafting and scrap-heap work both grade A+), competent trading, a genuinely poor free-agent record — and none of it has yet produced a single October win. Whether you weight the machine or the harvest is the debate; the Ledger's job is to put real numbers under both sides. It also matches the July 2026 discourse: [ownership is publicly supportive](https://www.baltimorebaseball.com/sports/orioles-mlb/2026/07/16/pondering-future-orioles-president-baseball-operations-mike-elias-richdubroff/) while the fanbase calls for his job — both camps are reading the same ledger and weighting different columns.

## The two new methodology pieces

**The draft-slot expectation curve.** Every pick is graded against what its slot historically returns over the control window (log-interpolated from published draft-value research: ~9.9 WAR for 1-1, ~5.5 at pick 5, ~2.1 at pick 30, ~1.1 at pick 65, fading to ~0.1 by round 20), so Rutschman at 1-1 clears a 9.9-WAR bar while Henderson at pick 42 clears a 1.35-WAR bar — which is why Henderson (+~19 vs. slot) grades as the single best draft decision of the regime even though Rutschman (+~7) was the better prospect.

**The maturity schedule.** A class's expectation is prorated by years-since-draft (~2% at year one, ~22% at three, ~55% at five, ~70% at six). Without this, every recent class grades as a failure; with it, the 2022 class (Holliday at 1-1) grades a fair −1.6 — *behind the pace* of a #1 pick, not yet a bust. Class-by-class: 2019 is one of the great draft hauls of the era (+24 net: Rutschman, Henderson, plus Stowers and Ortiz who became trade currency); 2020 graded dead-even (Westburg's +6 vs. slot canceled by Kjerstad at 1-2); 2021 positive (Cowser); 2023–25 too young to say.

## Channel notes

**Trades (+12.7, A).** The wins are sell-side and buy-low: Bundy→Bradish (+9.2) remains the signature heist, the 2022 deadline sales (+4.0, Cano and Povich in) and Hays→Domínguez/Laureano (+2.3) behind it. The two "go-for-it" buys are the drag: Burnes (−2.9 and deteriorating — Joey Ortiz is controlled through 2029) and Rogers (−0.5 but trending back to even after his 1.81-ERA 2025; Stowers' Miami breakout keeps it honest). The 2025 sell-off (8 deals, 16 prospects + pick #37 in) is almost entirely open windows — it will move this channel for a decade. Grayson Rodriguez→Taylor Ward is 2026-in-progress, listed but ungraded.

**Free agency (−6.9, D+).** Seven graded signings, one roughly break-even (Gibson), none clearly positive, and the 2024–25 winter (O'Neill 3/$49.5M, Morton, Kimbrel) ≈ −$52M of surplus on its own. This channel is the documented weakness — consistent with the local criticism of "unsuccessful veteran starter signings." The big 2025–26 winter (Alonso, Helsley, Bassitt, Eflin, Taveras) is ungraded until the season closes.

**Found money (+23.5, A+).** Urías, Mateo, Wells (Rule 5), Pérez, O'Hearn (bought for cash, turned into ~4 WAR *and* a six-prospect deadline package), Coulombe — ≈ $155M of surplus acquired for roughly nothing. Per-season this is the best waiver/minor operation in the sport over the window, and it's a pro-scouting signature that the site's later attribution layer could trace to individuals.

**Passive ledger.** Letting Santander and Burnes walk both aged well (comp picks in, decline/injury out) — passive decisions counted, as the methodology requires.

## Caveats

Per-player bWAR inputs are approximate (±~0.5, all flagged in the script) pending a licensed or self-computed WAR feed; channel totals and grades are robust to those tolerances, individual line items are not. Values realized through the 2025 season; 2026-in-progress moves listed but ungraded. Minor transactions (depth signings, small claims) are omitted and would collectively shift totals by a few WAR at most. Composite grading (channel sum vs. a higher composite bar) is methodology v0.1 and versioned — this is exactly the kind of parameter the public methodology page would document and archive.

## Sources

[BaltimoreBaseball.com on Elias's status](https://www.baltimorebaseball.com/sports/orioles-mlb/2026/07/16/pondering-future-orioles-president-baseball-operations-mike-elias-richdubroff/) · [CBS Sports on his promotion to POBO](https://www.cbssports.com/mlb/news/orioles-searching-for-new-gm-after-quietly-promoting-mike-elias-to-president-of-baseball-ops-per-report) · [Wikipedia: 2025 Orioles season](https://en.wikipedia.org/wiki/2025_Baltimore_Orioles_season) (75–87, Hyde firing, Rogers 1.81 ERA, O'Neill/Morton/Sugano/Kittredge terms) · [BirdlandFlock: every 2025 deadline trade](https://www.birdlandflock.com/p/orioles-deadline-2025-breaking-down-every-trade) · [Eutaw Street Report: 2025–26 offseason review](https://eutawstreetreport.com/offseason-2026/) (Alonso, Helsley, Bassitt, Ward-for-Rodriguez) · [MLB.com: Bassitt signing](https://www.mlb.com/news/chris-bassitt-orioles-contract) · [MLB.com: 2024 wild-card exit](https://www.mlb.com/news/orioles-lose-to-royals-get-swept-in-al-wild-card-series)
