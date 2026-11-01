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
