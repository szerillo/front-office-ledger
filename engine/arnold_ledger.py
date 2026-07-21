"""
Front Office Ledger: the ARNOLD REGIME, auto-scored with Ledger WAR v0
=======================================================================
First regime scored with COMPUTED values end to end: player value comes
from ledger_war.py (self-computed from the MLB Stats API), person ids come
from the Chadwick crosswalk built by the pipeline, decision structure from
the assembler. Hand-entered inputs are now limited to: decision selection
(the ~15 highest-consequence moves), control windows, and contract terms.

Matt Arnold, Milwaukee Brewers: GM Oct 2022, POBO thereafter. Storyline the
numbers should reveal: he inherited a loaded Stearns-era pipeline (Chourio,
Frelick, Misiorowski, Turang are INHERITED and excluded), then sustained a
winner while monetizing stars on their way out (Burnes, Williams, Adames)
and buying almost nothing in major-league free agency.
"""
import sqlite3
from ledger_war import player_seasons

def ids_by_name(*names):
    con = sqlite3.connect("ledger.sqlite")
    out = {}
    for n in names:
        row = con.execute("select mlbam, name from crosswalk where name like ?", (f"%{n}%",)).fetchall()
        if row: out[n] = int(row[0][0])
        else: out[n] = None
    return out

NAMES = ["William Contreras", "Joel Payamps", "Esteury Ruiz", "Corbin Burnes",
         "Joey Ortiz", "DL Hall", "Devin Williams", "Nestor Cortes", "Caleb Durbin",
         "Quinn Priester", "Aaron Civale", "Andrew Vaughn", "Rhys Hoskins",
         "Jose Quintana", "Tobias Myers", "Jackson Chourio", "Brandon Woodruff",
         "Willy Adames", "Isaac Collins"]
IDS = ids_by_name(*NAMES)
DATA = player_seasons([v for v in IDS.values() if v])

def war(name, years):
    pid = IDS.get(name)
    if not pid or pid not in DATA: return 0.0, False
    rec = DATA[pid]
    tot, found = 0.0, False
    for y in years:
        if y in rec["seasons"]:
            s = rec["seasons"][y]; tot += s["bat"] + s["pit"]; found = True
    return round(tot, 1), found

fmt = lambda x: f"{'+' if x >= 0 else ''}{x:,.1f}"

# ---- decisions: (label, ins [(name, years)], outs [(name, years)], note) ----
TRADES = [
 ("Dec 2022 · 3-team Sean Murphy deal: Contreras + Payamps in, Esteury Ruiz out",
  [("William Contreras", [2023, 2024, 2025]), ("Joel Payamps", [2023, 2024, 2025])],
  [("Esteury Ruiz", [2023, 2024, 2025])],
  "the signature move: an everyday all-star catcher for a spare outfielder"),
 ("Feb 2024 · Burnes to BAL for Ortiz + Hall + pick 34",
  [("Joey Ortiz", [2024, 2025]), ("DL Hall", [2024, 2025])],
  [("Corbin Burnes", [2024])],
  "the seller's side of the deal we scored from Baltimore's seat; pick 34 adds ~+1 unrealized"),
 ("Dec 2024 · Devin Williams to NYY for Cortes + Durbin",
  [("Nestor Cortes", [2025]), ("Caleb Durbin", [2025])],
  [("Devin Williams", [2025])],
  "selling a closer's walk year"),
 ("Apr 2025 · Quinn Priester from BOS for comp pick + prospect",
  [("Quinn Priester", [2025])], [],
  "pick cost ~-1.5 expected (unrealized); Priester broke out"),
 ("2024-25 · Civale in (for prospect), then flipped for Andrew Vaughn",
  [("Aaron Civale", [2024, 2025]), ("Andrew Vaughn", [2025])], [],
  "chain: rental arm converted into a buy-low bat"),
]
FA = [  # (label, ins, $M paid to date, years)
 ("Rhys Hoskins · 2 yr / $34M", [("Rhys Hoskins", [2024, 2025])], 34.0),
 ("Jose Quintana · 1 yr / $4.25M", [("Jose Quintana", [2025])], 4.25),
 ("Brandon Woodruff · 2 yr / $17.5M injury re-sign", [("Brandon Woodruff", [2024, 2025])], 17.5),
]
EXT = [
 ("Dec 2023 · Jackson Chourio extension, 8 yr / $82M signed PRE-DEBUT",
  [("Jackson Chourio", [2024, 2025])], 6.0,
  "the boldest kind of retention decision: option exercised before the market ever saw him"),
]
FOUND = [
 ("Tobias Myers · minor-league acquisition", [("Tobias Myers", [2024, 2025])]),
 ("Isaac Collins · minor-league FA", [("Isaac Collins", [2025])]),
]
PASSIVE = [
 ("Willy Adames walks (FA, post-2024; comp pick in)", [("Willy Adames", [2025])]),
]

if __name__ == "__main__":
    DPW = 9.4
    print("=" * 74)
    print("ARNOLD REGIME, MILWAUKEE · scored with LEDGER WAR v0 (computed values)")
    print("=" * 74)
    t_net = 0.0
    print("\nTRADES (net LVM in minus out, realized through 2025)")
    for label, ins, outs, note in TRADES:
        wi = sum(war(n, y)[0] for n, y in ins); wo = sum(war(n, y)[0] for n, y in outs)
        t_net += wi - wo
        print(f"  {fmt(wi - wo):>7}  {label}")
        print(f"           in {fmt(wi)} / out {fmt(wo)} · {note}")
    print(f"  TRADES TOTAL: {fmt(t_net)} LVM")

    f_net = 0.0
    print("\nFREE AGENCY (LVM minus contract-implied wins)")
    for label, ins, paid in FA:
        w = sum(war(n, y)[0] for n, y in ins)
        n = w - paid / DPW; f_net += n
        print(f"  {fmt(n):>7}  {label} · {fmt(w)} LVM vs {paid / DPW:.1f} implied")
    print(f"  FA TOTAL: {fmt(f_net)} LVM vs cost")

    e_net = 0.0
    print("\nEXTENSIONS (retention decisions)")
    for label, ins, paid, note in EXT:
        w = sum(war(n, y)[0] for n, y in ins)
        n = w - paid / DPW; e_net += n
        print(f"  {fmt(n):>7}  {label}")
        print(f"           {fmt(w)} LVM realized vs ~{paid / DPW:.1f} implied by $ paid to date · {note}")

    fm_net = 0.0
    print("\nFOUND MONEY (baseline zero)")
    for label, ins in FOUND:
        w = sum(war(n, y)[0] for n, y in ins); fm_net += w
        print(f"  {fmt(w):>7}  {label}")
    print(f"  FOUND TOTAL: {fmt(fm_net)} LVM")

    print("\nPASSIVE LEDGER (informational)")
    for label, ins in PASSIVE:
        w = sum(war(n, y)[0] for n, y in ins)
        print(f"  {label}: departed value {fmt(w)} LVM elsewhere, comp pick credited")

    total = t_net + f_net + e_net + fm_net
    print("\n" + "=" * 74)
    print(f"REGIME NET (major decisions, realized through 2025): {fmt(total)} LVM")
    print("Inherited and excluded: Chourio signing, Frelick/Turang/Misiorowski")
    print("drafts (Stearns era). Arnold's fingerprint: sell stars at the peak of")
    print("their windows, convert to volume, extend the future before it debuts.")
