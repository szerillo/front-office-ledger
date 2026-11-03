# Acceptance tests

Headless regression harnesses (node + Playwright + chromium). Each check
encodes a bug that actually shipped once and was fixed; a failure is a
regression, not noise. Run before shipping (local page at
/work/front-office-ledger-prototype.html) and after deploying:

    PAGE=/path/to/front-office-ledger-prototype.html node t_gm_core.mjs
    TARGET=live node t_gm_core.mjs   # deployed page
    # PAGE defaults to /work/front-office-ledger-prototype.html

Covers: surplus trade logic (the Witt refusal), FA pricing bands, the
2026-27 class reality (options/opt-outs/service), negotiation structure
(extra years are not free money; no counter echoes), payroll integrity on
trades, backward-looking arbitration (non-tenders exist), every major
feature surface, the date-vs-window boundary audit, and phone-width
overflow on every tab.

`t_math.mjs` (v5.1) encodes the November 2026 full-site math audit:
service time and calibrated arbitration (Baty, Alvarez, Witt, Skenes,
Stephenson), the real qualifying offer, one grade rule and one net figure
for every card, retention without re-signings, champions' biggest channel,
head-to-head symmetry across all 30 seats, the salary book closing to every
payroll widget, control (no own free agents, no six-year veterans), full
career trees (Betts, Lindor, Halladay's recovered return, no pass-through
seats), extend-then-trade payroll, and clean text on every tab.

`t_winter.mjs` (v5.2) encodes the real 2026-27 winter: contracts on file
(Sale, Hoerner, Rasmussen, Acuña), declined options and opt-outs as free
agents, opt-ins staying, retirements and the restricted list off the boards,
open decisions tagged, on-file rows never used as comps, CBA qualifying-offer
eligibility, the posted class (presence, posted-market pricing, posting fee
tiers, fee charged in surplus), and org prospects (a farm for every club,
prospect trades moving farms, promotion onto the depth chart, undo).

`t_launch.mjs` (v5.4) encodes the public-launch review: no internal jargon
("LVM"), the About/disclaimer note and repo link, plain theme labels,
pluralization, the +/- WAR guide, free-agent deals ending in free agency
(Senga), extension start seasons (Acuña, Griffin, Altuve), era-correct
champion names that still resolve to their regimes, a Scenario Room without
hindsight (Betts), the Ramírez extension priced against extensions, the
complete Greinke package, offseason comps that see the 2024-25 and 2025-26
winters, and the curated Burnes cards agreeing with the computed trade book.

`t_consistency.mjs` (v5.5) checks that traded draftees are never draft
misses for having been traded (Abrams, Gore), every trade in a tenure is
listed with per-move letters and no channel stamp on the "best" tables, the
tree finder browses the full list and renders a chain, open branches carry
projections, "lev-adj" is glossed, and the nav, beta tag, and "Evaluating the evaluators" line.
