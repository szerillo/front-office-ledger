"""Extend the historical regime table to the 1998 floor: unclamp every regime
whose true seat date is 1998+ (start = trueStart), clamp pre-1998 seats at
1998-01-01 (truncated flag, trueStart shown), and add the 1998-2004 regimes.
Dates are from well-documented GM history; month-level precision, 'approx'
flagged where the exact day is uncertain. Also updates regimes.json: Cashman's
active window extends to his real 1998-02 seat, and team 120 gains the
Montreal Expos alias so Expos-era value rows join."""
import json

h = json.load(open("/home/claude/regimes_hist.json"))
FLOOR = "1998-01-01"

def ts_to_date(ts):
    return ts + "-01" if len(ts) == 7 else ts

# 1) unclamp / reclamp existing records
for r in h["regimes"]:
    ts = r.get("trueStart")
    if not ts: continue
    full = ts_to_date(ts)
    if full >= FLOOR:
        r["start"] = full
        r["flags"] = [f for f in r.get("flags", []) if f != "truncated"] or []
        r.pop("trueStart", None)
    else:
        r["start"] = FLOOR
        if "truncated" not in r.get("flags", []):
            r.setdefault("flags", []).append("truncated")

# a few starts refined to known dates
REFINE = {("BOS", "Theo Epstein"): "2002-11-25", ("PIT", "Dave Littlefield"): "2001-07-13",
          ("SEA", "Bill Bavasi"): "2003-11-07", ("TOR", "J.P. Ricciardi"): "2001-11-14"}
for r in h["regimes"]:
    k = (r["abbr"], r["exec"])
    if k in REFINE: r["start"] = REFINE[k]

T = {"LAA": (108, "Los Angeles Angels"), "ARI": (109, "Arizona Diamondbacks"),
     "BAL": (110, "Baltimore Orioles"), "BOS": (111, "Boston Red Sox"),
     "CHC": (112, "Chicago Cubs"), "CIN": (113, "Cincinnati Reds"),
     "CLE": (114, "Cleveland Guardians"), "COL": (115, "Colorado Rockies"),
     "DET": (116, "Detroit Tigers"), "MIA": (146, "Miami Marlins"),
     "HOU": (117, "Houston Astros"), "KC": (118, "Kansas City Royals"),
     "LAD": (119, "Los Angeles Dodgers"), "MIL": (158, "Milwaukee Brewers"),
     "NYM": (121, "New York Mets"), "ATH": (133, "Oakland Athletics"),
     "PHI": (143, "Philadelphia Phillies"), "PIT": (134, "Pittsburgh Pirates"),
     "SEA": (136, "Seattle Mariners"), "TB": (139, "Tampa Bay Rays"),
     "TEX": (140, "Texas Rangers"), "TOR": (141, "Toronto Blue Jays"),
     "WSH": (120, "Washington Nationals"), "CWS": (145, "Chicago White Sox")}

def R(abbr, ex, start, end, flags=None, trueStart=None, team=None):
    tid, tm = T[abbr]
    d = dict(teamId=tid, team=team or tm, abbr=abbr, exec=ex, start=start, end=end)
    if flags: d["flags"] = flags
    if trueStart: d["trueStart"] = trueStart
    return d

NEW = [
 R("LAA", "Bill Bavasi", FLOOR, "1999-10-01", ["truncated", "approx"], "1994-10"),
 R("ARI", "Joe Garagiola Jr.", FLOOR, "2005-08-31", ["truncated", "approx"], "1995-09"),
 R("BAL", "Pat Gillick", FLOOR, "1998-10-31", ["truncated", "smallish"], "1995-11"),
 R("BAL", "Frank Wren", "1998-11-01", "1999-10-31", ["smallish", "approx"]),
 R("BAL", "Syd Thrift", "1999-12-01", "2002-10-31", ["approx"]),
 R("BAL", "Jim Beattie / Mike Flanagan", "2002-12-01", "2007-06-19", ["approx"]),
 R("BOS", "Dan Duquette", FLOOR, "2002-02-28", ["truncated"], "1994-01"),
 R("BOS", "Mike Port (interim)", "2002-03-01", "2002-11-24", ["smallish", "interim"]),
 R("CHC", "Ed Lynch", FLOOR, "2000-07-19", ["truncated", "approx"], "1994-10"),
 R("CHC", "Andy MacPhail (GM term)", "2000-07-20", "2002-07-05", ["smallish", "approx"]),
 R("CWS", "Ron Schueler", FLOOR, "2000-10-23", ["truncated", "approx"], "1990-09"),
 R("CIN", "Jim Bowden", FLOOR, "2003-07-28", ["truncated"], "1992-10"),
 R("CIN", "Dan O'Brien", "2003-10-27", "2006-01-23", ["approx"]),
 R("CLE", "John Hart", FLOOR, "2001-11-01", ["truncated"], "1991-09"),
 R("COL", "Bob Gebhard", FLOOR, "1999-08-20", ["truncated", "approx"], "1991-09"),
 R("DET", "Randy Smith", FLOOR, "2002-04-08", ["truncated"], "1995-10"),
 R("MIA", "Dave Dombrowski", FLOOR, "2001-11-05", ["truncated"], "1991-09", team="Florida Marlins"),
 R("HOU", "Gerry Hunsicker", FLOOR, "2004-11-01", ["truncated"], "1995-11"),
 R("HOU", "Tim Purpura", "2004-11-02", "2007-09-19", []),
 R("KC", "Herk Robinson", FLOOR, "2000-06-16", ["truncated", "approx"], "1990-09"),
 R("KC", "Allard Baird", "2000-06-17", "2006-05-30", ["approx"]),
 R("LAD", "Fred Claire", FLOOR, "1998-06-21", ["truncated", "smallish"], "1987-04"),
 R("LAD", "Kevin Malone", "1998-09-01", "2001-04-25", ["approx"]),
 R("LAD", "Dan Evans", "2001-10-01", "2004-02-15", ["approx"]),
 R("LAD", "Paul DePodesta", "2004-02-16", "2005-10-29", ["smallish"]),
 R("MIL", "Sal Bando", FLOOR, "1999-08-12", ["truncated", "approx"], "1991-10"),
 R("MIL", "Dean Taylor", "1999-09-01", "2002-09-25", ["approx"]),
 R("NYM", "Steve Phillips", FLOOR, "2003-06-12", ["truncated"], "1997-07"),
 R("NYM", "Jim Duquette", "2003-06-13", "2004-09-29", ["smallish"]),
 R("PHI", "Ed Wade", "1998-01-01", "2005-11-01", ["approx"], "1997-12"),
 R("PIT", "Cam Bonifay", FLOOR, "2001-06-11", ["truncated"], "1993-06"),
 R("SEA", "Woody Woodward", FLOOR, "1999-09-01", ["truncated", "approx"], "1988-07"),
 R("SEA", "Pat Gillick", "1999-10-25", "2003-11-01", ["approx"]),
 R("TB", "Chuck LaMar", FLOOR, "2005-10-06", ["truncated"], "1995-07"),
 R("TEX", "Doug Melvin", FLOOR, "2001-10-02", ["truncated", "approx"], "1994-10"),
 R("TEX", "John Hart", "2001-11-01", "2005-10-03", ["approx"]),
 R("TOR", "Gord Ash", FLOOR, "2001-11-13", ["truncated"], "1995-09"),
 R("WSH", "Jim Beattie", FLOOR, "2001-10-31", ["truncated", "approx"], "1995-10", team="Montreal Expos"),
 R("WSH", "Omar Minaya (Expos)", "2002-02-12", "2004-09-29", ["approx"], team="Montreal Expos"),
]
h["regimes"].extend(NEW)
h["comment"] = ("Historical regimes, 1998-2024. Transaction floor 1998-01-01 "
                "(feed 2009+, Retrosheet backfill 1985-2008; rows before 1998 serve "
                "provenance only). Regimes seated before 1998 are truncated and "
                "flagged with their true start. Dates are month-precise; 'approx' "
                "marks records where the exact day is uncertain.")
json.dump(h, open("/home/claude/regimes_hist.json", "w"), indent=1)
print(f"regimes_hist: {len(h['regimes'])} records")

# 2) regimes.json: Cashman true window + Expos alias
cfg = json.load(open("/home/claude/regimes.json"))
for r in cfg["regimes"]:
    if r["abbr"] == "NYY" and "Cashman" in r["exec"]:
        r["start"] = "1998-02-03"
        r["flags"] = [f for f in r.get("flags", []) if f != "truncated"]
cfg["aliases"].setdefault("120", ["Washington Nationals"])
if "Montreal Expos" not in cfg["aliases"]["120"]:
    cfg["aliases"]["120"].append("Montreal Expos")
if "Washington Nationals" not in cfg["aliases"]["120"]:
    cfg["aliases"]["120"].insert(0, "Washington Nationals")
json.dump(cfg, open("/home/claude/regimes.json", "w"), indent=1)
print("regimes.json: Cashman 1998-02-03; Expos alias added")
