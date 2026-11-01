"""Arbitration award calibration (v5.1): 2026 one-year arbitration salaries
(agreed figures, or the filing midpoint where a hearing was pending), as
reported at the January 2026 exchange deadline, against the model's award
for the same player computed from information available that winter
(service through 2025, platform WAR 2025 and 2024, the 2026 $/WAR)."""
import json
REAL = {  # $M, 2026 season
 "Spencer Steer":4.0,"Gavin Lux":5.525,"TJ Friedl":3.8,"Will Benson":1.725,"Matt McLain":2.3,"Brady Singer":12.75,
 "Nick Lodolo":4.725,"Tony Santillan":1.8,"Tyler Stephenson":6.675,"Graham Ashcraft":1.5,
 "Jo Adell":5.2,"Zach Neto":4.15,"Brock Burke":2.325,"Logan O'Hoppe":2.625,"José Soriano":2.9,"Reid Detmers":2.775,
 "Michael Massey":1.57,"Kyle Isbel":2.7,"Bailey Falter":3.6,"Daniel Lynch IV":1.025,"John Schreiber":3.715,"Nick Mears":1.9,
 "Jonathan India":8.0,"James McArthur":0.81,"Vinnie Pasquantino":4.25,"Kris Bubic":5.65,
 "Riley Greene":5.0,"Spencer Torkelson":4.075,"Kerry Carpenter":3.275,"Will Vest":3.95,"Zach McKinstry":4.2,"Casey Mize":6.15,
 "Tyler Holton":1.575,"Matt Vierling":3.255,"Beau Brieske":1.1575,"Jake Rogers":3.05,
 "Brice Turang":4.15,"Andrew Vaughn":7.65,"Trevor Megill":4.7,"Angel Zerpa":1.095,"Garrett Mitchell":0.95,"William Contreras":9.225,
 "Joe Ryan":6.1,"Randy Arozarena":15.65,"Matt Brash":1.55,"Logan Gilbert":10.927,"George Kirby":6.55,"Luke Raley":2.05,"Gabe Speier":2.125,
}
D = json.load(open("/work/desk_data.json")); S = json.load(open("/work/service.json"))
import unicodedata
fold = lambda x: unicodedata.normalize("NFD", x).encode("ascii", "ignore").decode().lower()
by = {fold(p[0]): p for p in D["players"]}
rows = []
for nm, sal in REAL.items():
    p = by.get(fold(nm))
    if not p: print("  not in pool:", nm); continue
    sv = S.get(str(p[1]))
    if not sv: print("  no service:", nm); continue
    arbw = [w for w in sv["arb_winters"] if w <= 2025]
    k = len(arbw) if 2025 in arbw else 0
    basis = max(p[6], 0.5 * (p[5] + p[6]), 0)
    rows.append(dict(nm=nm, sal=sal, k=k, basis=basis, pit=p[3], svc=sv["svc"], w24=p[5], w25=p[6]))
print("calibration rows:", len(rows))
for r in sorted(rows, key=lambda r: (r["k"], r["sal"])): print(f"  {r['nm']:20} arb#{r['k']} basis {r['basis']:.2f} ({r['w24']}/{r['w25']}) real ${r['sal']}M")
json.dump(rows, open("/work/arb_calib_rows.json", "w"))
