"""
Front Office Ledger — full-regime proof of concept
===================================================
Scores the MIKE ELIAS regime (Baltimore Orioles, Nov 2018 – present) across
all four acquisition channels, and demonstrates the two remaining
methodology pieces the Betts POC didn't need:

  1. THE DRAFT-SLOT EXPECTATION CURVE — a pick is graded against what that
     slot historically returns, not against zero. Pick 1-1 carries a ~10-WAR
     bar; a 2nd-rounder carries ~1.4.
  2. THE MATURITY SCHEDULE — a 2024 pick hasn't had time to produce yet, so
     its expectation is prorated by years-since-draft. Without this, every
     recent class grades as a failure.

CHANNEL DEFINITIONS
  Draft/Amateur — draft picks + international amateur signings, credited
    with WAR captured BY BALTIMORE during the control window. When a drafted
    player is traded, his remaining window moves to that trade's
    "surrendered" side (no double counting).
  Trades — two-sided, realized WAR through 2025 (open windows flagged).
  Free agency — graded as ROI: realized WAR minus the WAR the contract
    price implied at market $/WAR.
  Waiver/Minor/Rule 5 — baseline zero; pure found money.

DATA PROVENANCE: transactions, contract terms, draft slots, and season
narratives verified via public coverage (Wikipedia season pages, MLB.com,
Camden Chat / Baltimore Banner / BirdlandFlock deadline coverage, MLBTR).
Per-player bWAR figures are approximate (+/- ~0.5, flagged 'approx') —
B-Ref/FanGraphs block programmatic access, so a production build needs a
licensed or self-computed feed. 2026 half-season moves are listed but NOT
graded. Grades are robust to the stated tolerances; individual line items
are not gospel.
"""

TENURE_SEASONS = 7.6          # Nov 2018 through the 2026 All-Star break
DPW = {2019: 7.8, 2020: 8.0, 2021: 8.2, 2022: 8.5, 2023: 9.0,
       2024: 9.3, 2025: 9.5}  # market $M per WAR (published estimates)

# ---------------------------------------------------------------
# 1) DRAFT-SLOT EXPECTATION CURVE
#    Expected WAR over the full control window (~first 7 pro years),
#    historical means from published draft-value research lineage
#    (Baseball America / FanGraphs / TPOP draft studies).
# ---------------------------------------------------------------
def slot_expectation(pick):
    table = [(1, 9.9), (2, 7.5), (3, 6.7), (5, 5.5), (8, 4.6), (12, 3.6),
             (17, 3.0), (22, 2.6), (30, 2.1), (45, 1.5), (65, 1.1),
             (90, 0.85), (120, 0.6), (200, 0.35), (400, 0.18), (620, 0.10)]
    if pick <= 1: return table[0][1]
    for (p1, v1), (p2, v2) in zip(table, table[1:]):
        if pick <= p2:  # log-linear interpolation between anchors
            import math
            f = (math.log(pick) - math.log(p1)) / (math.log(p2) - math.log(p1))
            return v1 + f * (v2 - v1)
    return 0.10

# Maturity: share of a class's control-window value realized N years on
MATURITY = {1: 0.02, 2: 0.10, 3: 0.22, 4: 0.38, 5: 0.55, 6: 0.70, 7: 0.82}
def maturity(draft_year, asof=2025):
    return MATURITY.get(max(0, asof - draft_year), 0.0 if asof <= draft_year else 0.82)

# ---------------------------------------------------------------
# 2) INPUTS — the Elias ledger
# ---------------------------------------------------------------
# Draft classes: MLB-relevant picks individually; the long tail of each
# class is carried as a single expectation line (its realized WAR ~0 so far).
DRAFTS = [
  dict(year=2019, picks=[
      ("C Adley Rutschman", 1, 13.7, "5.2/4.8/3.2/0.5 2022-25 (approx)"),
      ("SS Gunnar Henderson", 42, 20.3, "1.0/6.2/9.1/4.0 2022-25 (approx; 9.1 in '24)"),
      ("OF Kyle Stowers", 71, -0.9, "BAL only; MIA window -> Rogers trade"),
      ("IF Joey Ortiz", 108, 0.6, "BAL only; MIL window -> Burnes trade"),
    ], tail_expect=2.6),   # rounds 5-40 aggregate expectation
  dict(year=2020, picks=[
      ("OF Heston Kjerstad", 2, -0.5, "approx"),
      ("IF Jordan Westburg", 30, 7.2, "1.6/4.1/1.5 2023-25 (approx)"),
      ("3B Coby Mayo", 103, -1.0, "approx"),
    ], tail_expect=0.9),   # 5-round draft
  dict(year=2021, picks=[
      ("OF Colton Cowser", 5, 4.6, "-0.2/3.8/1.0 2023-25 (approx)"),
      ("2B Connor Norby", 41, 0.2, "BAL only; MIA window -> Rogers trade"),
    ], tail_expect=1.8),
  dict(year=2022, picks=[
      ("SS Jackson Holliday", 1, 1.4, "-0.6/2.0 2024-25 (approx)"),
      ("OF Dylan Beavers", 33, 0.5, "2025 debut (approx)"),
      ("3B Max Wagner", 42, 0.0, ""),
      ("OF Jud Fabian", 67, 0.0, ""),
    ], tail_expect=1.4),
  dict(year=2023, picks=[
      ("OF Enrique Bradfield Jr.", 17, 0.2, "approx"),
    ], tail_expect=2.2),
  dict(year=2024, picks=[
      ("OF Vance Honeycutt", 22, 0.0, ""),
      ("SS Griff O'Ferrall", 34, 0.0, ""),
    ], tail_expect=2.0),
  dict(year=2025, picks=[
      ("C/OF Ike Irish", 19, 0.0, ""),
      ("OF Slater de Brun", 37, 0.0, "pick acquired in Bryan Baker trade"),
    ], tail_expect=2.0),
]
INTL = [  # international amateur channel (folded into Draft/Amateur)
  ("C Samuel Basallo", 2021, 0.5, 0.4, "signed Jan 2021 ($1.3M); debut 2025 (approx)"),
]

# Trades: (name, year, WAR in [received, during window], WAR out, open?, note)
TRADES = [
  ("Dylan Bundy to LAA for Kyle Bradish + 3 arms", 2019, 10.2, 1.0, False,
   "Bradish ~8.2 through '23 + injury-shortened return; Bundy ~1.0 for LAA (approx)"),
  ("Jonathan Villar salary dump to MIA", 2019, 0.0, 0.3, False,
   "saved ~$10M for a ~0-WAR season out; scored ~ +$8M in surplus terms"),
  ("2022 deadline: Mancini/Lopez sales", 2022, 5.0, 1.0, False,
   "Cade Povich ~1.5 + Yennier Cano ~2.5 + McDermott et al. vs. rentals out (approx)"),
  ("Austin Hays to PHI for Dominguez + Laureano", 2024, 3.3, 1.0, False,
   "Laureano's 2.5-WAR 2025 the surprise win; Hays ~1.0 elsewhere (approx)"),
  ("Zach Eflin from TB for three prospects", 2024, 2.3, 0.0, True,
   "Eflin 1.8 in '24 + injured '25; Baumeister/Horvath/Etzel windows open"),
  ("Corbin Burnes from MIL for Ortiz + Hall + pick 34", 2024, 4.1, 7.0, True,
   "Burnes ~4.1 rental year; Ortiz ~5.4 and controlled thru '29 + DL Hall 0.5 + pick ~1.0 maturity-adj (approx) — OPEN, deteriorating"),
  ("Trevor Rogers from MIA for Stowers + Norby", 2024, 3.5, 4.0, True,
   "Rogers -1.0 in '24 then 1.81 ERA in '25 (~4.5); Stowers broke out for MIA ~2.5 + Norby ~1.5 — OPEN, trending back to even"),
  ("2025 deadline sell-off (8 deals)", 2025, 0.1, 1.5, True,
   "Baker/Soto/Dominguez/Kittredge/Urias/Mullins/O'Hearn+Laureano/Morton out for 16 prospects + pick 37; essentially all value OPEN"),
]
TRADES_UNGRADED = [
  ("Grayson Rodriguez to LAA for Taylor Ward", 2025, "2026 in progress — not graded"),
]

# Free agency: (player, year, total $M, yrs, WAR realized, $M paid so far, open?, note)
FREE_AGENTS = [
  ("Kyle Gibson", 2023, 10.0, 1, 1.1, 10.0, False, ""),
  ("Adam Frazier", 2023, 8.0, 1, 0.4, 8.0, False, ""),
  ("Craig Kimbrel", 2024, 13.0, 1, 0.2, 13.0, False, "released in September"),
  ("Tyler O'Neill", 2025, 49.5, 3, -0.5, 16.5, True, "injured/ineffective '25 (approx)"),
  ("Charlie Morton", 2025, 15.0, 1, -0.5, 15.0, False, "flipped for lottery arm at deadline"),
  ("Tomoyuki Sugano", 2025, 13.0, 1, 1.0, 13.0, False, "approx"),
  ("Andrew Kittredge", 2025, 10.0, 1, 0.5, 10.0, False, "flipped at deadline"),
]
FA_UNGRADED = [
  "2025-26 winter class — Pete Alonso, Ryan Helsley, Chris Bassitt, Zach Eflin "
  "(re-sign), Leody Taveras: 2026 in progress, listed not graded",
]

# Waiver / minor-league / Rule 5 / cash: (player, year in, WAR for BAL, ~$M paid, note)
FOUND_MONEY = [
  ("IF Ramon Urias (waivers, STL)", 2020, 6.5, 12.0, "approx; traded 7/25"),
  ("SS Jorge Mateo (waivers, SD)", 2021, 4.3, 9.0, "approx"),
  ("RHP Tyler Wells (Rule 5)", 2020, 4.0, 3.0, "approx"),
  ("LHP Cionel Perez (waivers, CIN)", 2022, 2.3, 6.0, "approx"),
  ("1B Ryan O'Hearn (from KC for cash)", 2023, 4.2, 16.0, "approx; traded 7/25 in 6-prospect deal"),
  ("LHP Danny Coulombe (minor-lg/cash)", 2023, 2.2, 8.0, "approx"),
]

# Passive ledger (departures without return): informational in this POC
PASSIVE = [
  ("Anthony Santander walks (FA, post-2024)", "+comp pick; Santander ~-0.5 for TOR '25 — walking him graded WELL"),
  ("Corbin Burnes walks (FA, post-2024)", "+comp pick; Burnes hurt in '25 — the non-extension aged fine"),
]

# ---------------------------------------------------------------
# 3) ENGINE
# ---------------------------------------------------------------
def grade(net_per_season):
    for thr, g in [(2.6,80),(1.8,75),(1.2,70),(0.8,65),(0.5,60),(0.2,55),
                   (-0.2,50),(-0.6,45),(-1.0,40),(-1.6,35)]:
        if net_per_season >= thr: return g
    return 30

def grade_composite(net_per_season):
    # the composite sums four channels, so its bar is higher than any one
    # channel's: a uniformly-elite FO runs ~+10/season across the four.
    for thr, g in [(8.0,80),(5.5,75),(3.5,70),(2.2,65),(1.2,60),(0.4,55),
                   (-0.4,50),(-1.2,45),(-2.2,40),(-3.5,35)]:
        if net_per_season >= thr: return g
    return 30
LETTER = lambda g: {80:'A+',75:'A',70:'A',65:'A-',60:'B+',55:'B',50:'C+',
                    45:'C',40:'D+',35:'D',30:'F'}[g]
fmt = lambda x: f"{'+' if x>=0 else ''}{x:,.1f}"

def score_draft():
    print("="*78); print("CHANNEL 1 — DRAFT / AMATEUR"); print("="*78)
    print(f"  {'class':<7}{'realized WAR':>14}{'expectation':>13}{'net':>9}   note")
    total_r = total_e = 0.0
    for d in DRAFTS:
        m = maturity(d['year'])
        realized = sum(p[2] for p in d['picks'])
        expect = (sum(slot_expectation(p[1]) for p in d['picks']) + d['tail_expect']) * m
        total_r += realized; total_e += expect
        star = max(d['picks'], key=lambda p: p[2] - slot_expectation(p[1])*m)
        print(f"  {d['year']:<7}{realized:>14.1f}{expect:>13.1f}{fmt(realized-expect):>9}"
              f"   best: {star[0]} ({fmt(star[2])})")
    for name, yr, war, exp, note in INTL:
        m = maturity(yr)
        total_r += war; total_e += exp*m
        print(f"  int'l  {war:>14.1f}{exp*m:>13.1f}{fmt(war-exp*m):>9}   {name} — {note}")
    net = total_r - total_e
    print(f"  {'TOTAL':<7}{total_r:>14.1f}{total_e:>13.1f}{fmt(net):>9}")
    return net

def score_trades():
    print("\n" + "="*78); print("CHANNEL 2 — TRADES  (baseline: value in = value out)"); print("="*78)
    net = 0.0
    for name, yr, w_in, w_out, open_, note in TRADES:
        n = w_in - w_out; net += n
        print(f"  {fmt(n):>7}  {name}{'  [OPEN]' if open_ else ''}")
        print(f"           {note}")
    for name, yr, note in TRADES_UNGRADED:
        print(f"  {'n/g':>7}  {name} — {note}")
    print(f"  TOTAL net: {fmt(net)} WAR")
    return net

def score_fa():
    print("\n" + "="*78); print("CHANNEL 3 — FREE AGENCY  (baseline: WAR the contract price implied)"); print("="*78)
    net = surplus = 0.0
    for player, yr, total, yrs, war, paid, open_, note in FREE_AGENTS:
        implied = paid / DPW[yr]           # WAR the money paid so far implied
        n = war - implied; net += n
        s = war * DPW[yr] - paid; surplus += s
        print(f"  {fmt(n):>7}  {player} ({yr}, {yrs}x${total/yrs:.1f}M): "
              f"{fmt(war)} WAR vs {implied:.1f} implied; surplus {fmt(s)} $M"
              f"{'  [OPEN]' if open_ else ''}{('  — ' + note) if note else ''}")
    for line in FA_UNGRADED: print(f"  {'n/g':>7}  {line}")
    print(f"  TOTAL net: {fmt(net)} WAR  ({fmt(surplus)} $M surplus)")
    return net

def score_found():
    print("\n" + "="*78); print("CHANNEL 4 — WAIVERS / MINOR-LG / RULE 5  (baseline: zero)"); print("="*78)
    net = surplus = 0.0
    for player, yr, war, paid, note in FOUND_MONEY:
        net += war; s = war * DPW.get(yr+2, 9.0) - paid; surplus += s
        print(f"  {fmt(war):>7}  {player} — {note}; surplus ~{fmt(s)} $M")
    print(f"  TOTAL net: {fmt(net)} WAR  (~{fmt(surplus)} $M surplus)")
    return net

if __name__ == "__main__":
    print(__doc__)
    d = score_draft(); t = score_trades(); f = score_fa(); w = score_found()
    print("\n" + "="*78); print("REGIME SUMMARY — Mike Elias, Baltimore (Nov 2018 – 2026 ASB)"); print("="*78)
    rows = [("Draft/Amateur", d), ("Trades", t), ("Free agency", f), ("Waiver/Minor", w)]
    for name, v in rows:
        g = grade(v / TENURE_SEASONS)
        print(f"  {name:<15}{fmt(v):>8} WAR vs expectation   grade {LETTER(g)} ({g}/80)")
    total = d + t + f + w
    g = grade_composite(total / TENURE_SEASONS)
    print(f"  {'TOTAL':<15}{fmt(total):>8} WAR  ->  FOR {LETTER(g)} ({g}/80) "
          f"over {TENURE_SEASONS} seasons ({fmt(total/TENURE_SEASONS)}/season)")
    print("\n  TEAM SUCCESS (separate grade): .484 W% (~527-562 + 46-51 in '26),")
    print("  1 division title ('23), 2 playoff berths ('23,'24), 0 playoff-series")
    print("  wins, 0 playoff GAME wins (0-5), 0 pennants  ->  grade C (45/80)")
    print("\n  PASSIVE LEDGER (informational):")
    for name, note in PASSIVE: print(f"    - {name}: {note}")
    print("\n  THE STORY THE GAP TELLS: elite value creation (draft + scrap heap),")
    print("  competent trading, poor FA record — and none of it has produced a")
    print("  single October win. FOR grades the machine; Success grades the harvest.")
