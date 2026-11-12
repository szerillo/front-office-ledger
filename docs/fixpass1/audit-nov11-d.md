# Audit, Nov 11 part 4 (fix pass 1 on a production-shaped ledger)

Paper only. Nothing went to the site or to X. Pre-registration: 5e81190, amendments 8e79455 (ledger_v2),
d6656e3 (rule 12), 1457561 (rule 12 counted and replaced). Traces and patches: docs/fixpass1 (latest 7591d71).

## 29. Round results against 5e81190

| Round | Engine | Ledger | Result | First difference |
|---|---|---|---|---|
| 1 | rules 1-4 | frozen | FAIL | sweep_results, cards, moves (ties, unordered reads) |
| 2 | rules 1-8 | frozen | FAIL (stopped after 2 runs) | allx_intl order |
| 3 | rules 1-9 | frozen | FAIL (stopped after 2 runs) | moves.js (regen_v3 duplicate text) |
| 4 | rules 1-10 | frozen | FAIL (stopped after 2 runs) | prototype SCEN order |
| 5 | rules 1-11 | v2 | stopped before a run finished | (rule 12 added) |
| 6 | rules 1-12 | v2 | FAIL (stopped after 2 runs) | Rule 5 conduit copies (PHI Vasil, MIN Susac) |
| 7 | rules 1-13 | v2 | FAIL | reversed reads: draft_picks order (rule 14) |
| 8 | rules 1-14 | v2 | **PASS** | none |

Each stop came after the bar had already failed. Each new rule was traced and committed before the round that
used it.

## 30. The ledger

**Why it changed.** The Step 0 frozen ledger was built from the league-wide feed with one row per receiving club and
no tx_id, from_team or to_team. 7,661 of 7,661 trade rows from 2009 on had no clubs, so it graded 1,443 trades
against production's 4,172. "Live matches no run" (round 24) came from that ledger, not from the site.

**ledger_v2** (md5 d192a2bd): sweep_tx 282,564 rows (244,767 feed, 37,797 Retrosheet), draft_picks 34,439.
Built with: `ingest/hist_ingest.py` logic (md5 36166c3a, unchanged at main f68f9f9), reimplemented as
`docs/fixpass1/ledger_v2_pull.py` with END = 2026-11-10 and raw responses cached; then `ingest/retro_backfill.py`
(md5 2da191c2) with only the database path changed; then the Step 0 draft_picks (freeze_drafts.py, 4464e38).
Production's own ledger is not available (/work/ledger.sqlite is 0 bytes), so the tests compare outputs.

**Tests that would show it is not production-shaped, and results** (unpatched engine on ledger_v2 = RV0, against
production's /work outputs):
- Trade book, order-free: 4,170 of 4,172 production trades identical. RV0 has 4,178. The 6 extra are trades filed
  after production's build: 947273 (ATH-BOS, Oct 29), 947461 (BOS-DET, Oct 29), 947637 (SF-WSH, Nov 1), 947670
  (HOU-TB, Nov 2), 947930 (BOS-STL, Nov 3), 949789 (SF-WSH, Nov 6). The 2 changed: ARI-STL 2026-08-03 gains its
  player named later (Brian Curley, 947254, filed Oct 1); NYY-PHI 2021-11-19 (600337 and 610581) is split into two
  PHI seats by the unpatched grouping (production: one seat; the patched engine also gives one seat).
- Channel cells (n, net, grade, 30 regimes): 58 of 660 differ. Waiver n (19) and intl n (16) are filings after
  production's build; trade n, net and grade (19) follow the 6 new trades and the ARI player named later; draft net
  +0.1 for CLE, NYY, SD and SEA is not yet traced.
- Patched build vs live: winter table 816 of 816 with 0 numeric cells different; trade_parts 8,611 of 8,611 equal
  (11 more in v2, all Oct 29 to Nov 6).
- Not testable: whether production's first year per regime came from sweep_ingest (partial) or hist_ingest (full).

## 31. Round 8: PASS
Engine 79922d7 (rules 1 to 14), ledger_v2, W0 unshuffled, W1 to W5 shuffled (seeds 20261161 to 20261165), W6
reversed reads. One md5 per published file across all seven: cards.js 52fee312, moves.js 25e94287, prototype
e42ae083, offseasons.json 39e25875, trade_parts.json ef4bc7c3 (mid files one md5 each too). 0 guard aborts.
Secondary bar: every W0 vs RV0 value difference is traced to a rule (section 32). Results:
docs/fixpass1/round8_results.json.

## 32. What reaches the public pages from code (W0 vs RV0, same ledger)
Report cards:
- Departures (ret net2), rule 1: ARI 22.4 to 22.3, CLE 22.9 to 22.8, NYM 4.5 to 4.4, NYY 15.1 to 15.0,
  PHI 1.4 to 1.3, SD -16.0 to -16.1.
- Waivers, rule 13: PHI -0.5 to +0.4 and 56 to 55 decisions (Mike Vasil's 2024 Rule 5 loss belonged to the Mets;
  the old step re-filed the Mets' copy and left PHI charged); PIT 1.3 to 1.1 and 88 to 87.
- International signings, rule 6: SEA 202 to 201, TOR 359 to 360 (Bello).
- No overall or channel letter grade changes. Regime totals move 0.1 for ARI, CLE, NYM, NYY, SD; PHI -5.8 to -5.1;
  PIT 7.1 to 6.9.
- PHI trades 110 to 109 and PHI 2021-22 winter (6 to 5 trades, -0.3 to -0.5): the patched engine matches live here.
Text only: 51 winter trade headlines name a different player for a tie or spell a name differently (rule 12);
head-to-head deal texts; the comparable-deal lists on 154 trade cards (rule 7); 7 waiver best/worst entries tied
on value (rule 5). Winter numbers, trade parts and trade grades: 0 changes.

Data, not code (RV0 vs live): HOU trade grade 50 to 80 and overall 50 to 70 (Reifert, Nov 2); ATH 50 to 30
(Eaton, Oct 29); WSH 75 to 70 and 65 to 60 (Nov 1 and 6 trades); waiver and international counts +1 to +3.

## 33. Other checks
- Draft picks restore: by sorted row content the restored table equals the copies made before the damage
  (ledger_R3 from 18:32, the G0 and H0 run copies): 34,439 rows, 0 differ.
- Found doing that: `r5_conduit.py` rewrites the run's ledger in place (29 Rule 5 rows in the G0 copy). Its
  rewrite was order-dependent on a production-shaped ledger (rule 13).
- Dual signings: Bello (806593) is the only same-day two-club minor-league signing in both ledgers, 1 of 13,847
  international first signings; 0 rows name a club other than the filing club. Source: MLB.com transaction log
  (assigned to the DSL Blue Jays on 2022-08-03; Toronto affiliates 2022-24).
- 2020 fix with rates held, on ledger_v2 (IV0 vs V0rec): class rates byte-identical; Cole -1.9 to +1.0, Strasburg
  -18.9 to -16.0, Rendon -16.2 to -13.3; WSH 2019 -22.7 to -17.4, LAA 2019 -20.6 to -16.8; 84 of 826 extensions
  change (23 by a win or more, +58.0), Trout 2019 -2.7 to +0.3, Arenado -5.6 to -1.9, Yelich -3.2 to -1.0; 71
  winters change numbers, 37 by a win or more.
