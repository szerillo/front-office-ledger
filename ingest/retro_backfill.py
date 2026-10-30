"""
RETROSHEET BACKFILL, 1998-2008: the MLB Stats API transaction feed turns out
to be empty before 2009 (zero trades 2005-2008; ~170 rows in all of 2008),
so every window touching 2005-2008 was being scored on drafts and standings
alone, and championship provenance before 2009 was untraceable. The repo has
carried the Retrosheet transaction archive (1873-2022) since the backfill
was first planned; this script finally joins it in.

Maps Retrosheet rows 1985-01-01 .. 2008-12-31 into sweep_tx (scoring windows
floor at 1998; 1985-1997 rows serve provenance tracing only):
  T/Tp -> Trade            F/Fo -> Signed as Free Agent
  Fg   -> Declared Free Agency    W -> Claimed Off Waivers
  D    -> Rule 5 Selection        R -> Released
Players map retro id -> MLBAM via the Chadwick crosswalk; team codes map to
era-correct API names (Devil Rays, Florida Marlins, Angels of Anaheim) so
control-window value lookups match the LVM cache's season team strings.
Each deal emits rows under BOTH clubs' team_ids with one shared description
(the scorer's deal-grouping key). 2009+ stays feed-only; rows before 2005
only serve provenance tracing (regime windows are floored at 2005).

The information used here was obtained free of charge from and is
copyrighted by Retrosheet (www.retrosheet.org).

Idempotent: deletes previous retro-* rows first.
"""
import csv, json, os, sqlite3, zipfile
from collections import defaultdict

def find(*cands):
    for c in cands:
        if os.path.exists(c): return c
    raise FileNotFoundError(cands)

TRAN = "/tmp/retro/tran.txt"
if not os.path.exists(TRAN):
    z = find("/work/repo/data/retrosheet_tranDB.zip", "retrosheet_tranDB.zip",
             "front-office-ledger/data/retrosheet_tranDB.zip")
    os.makedirs("/tmp/retro", exist_ok=True)
    zipfile.ZipFile(z).extractall("/tmp/retro")

TEAM = {  # retro code -> (teamId, canonical name)
 "ANA": 108, "LAA": 108, "ARI": 109, "ATL": 144, "BAL": 110, "BOS": 111,
 "CHA": 145, "CHN": 112, "CIN": 113, "CLE": 114, "COL": 115, "DET": 116,
 "FLO": 146, "MIA": 146, "HOU": 117, "KCA": 118, "LAN": 119, "MIL": 158,
 "MIN": 142, "MON": 120, "WAS": 120, "NYA": 147, "NYN": 121, "OAK": 133,
 "PHI": 143, "PIT": 134, "SDN": 135, "SEA": 136, "SFN": 137, "SLN": 138,
 "TBA": 139, "TEX": 140, "TOR": 141,
}
def era_name(code, year):
    tid = TEAM[code]
    if tid == 139: return "Tampa Bay Devil Rays" if year <= 2007 else "Tampa Bay Rays"
    if tid == 146: return "Florida Marlins" if year <= 2011 else "Miami Marlins"
    if tid == 108:
        if code == "ANA" and year <= 2004: return "Anaheim Angels"
        return "Los Angeles Angels of Anaheim" if year <= 2015 else "Los Angeles Angels"
    if tid == 114: return "Cleveland Indians" if year <= 2021 else "Cleveland Guardians"
    if tid == 120: return "Montreal Expos" if code == "MON" else "Washington Nationals"
    if tid == 133: return "Oakland Athletics"
    CANON = {108:"Los Angeles Angels",109:"Arizona Diamondbacks",110:"Baltimore Orioles",
     111:"Boston Red Sox",112:"Chicago Cubs",113:"Cincinnati Reds",115:"Colorado Rockies",
     116:"Detroit Tigers",117:"Houston Astros",118:"Kansas City Royals",119:"Los Angeles Dodgers",
     121:"New York Mets",134:"Pittsburgh Pirates",135:"San Diego Padres",136:"Seattle Mariners",
     137:"San Francisco Giants",138:"St. Louis Cardinals",140:"Texas Rangers",141:"Toronto Blue Jays",
     142:"Minnesota Twins",143:"Philadelphia Phillies",144:"Atlanta Braves",145:"Chicago White Sox",
     147:"New York Yankees",158:"Milwaukee Brewers"}
    return CANON[tid]

# retro -> mlbam from the full Chadwick Bureau register (retro2mlbam.json,
# built from github.com/chadwickbureau/register people shards), with the
# project's crosswalk.csv as a fallback.
RET2MLB, RETNAME = {}, {}
for row in csv.DictReader(open(find("/work/repo/data/crosswalk.csv", "crosswalk.csv", "front-office-ledger/data/crosswalk.csv"))):
    if row.get("retro") and row.get("mlbam"):
        RET2MLB[row["retro"]] = row["mlbam"]
        RETNAME[row["retro"]] = row["name"]
for r, (mm, nm) in json.load(open(find("/work/retro2mlbam.json", "retro2mlbam.json", "front-office-ledger/data/retro2mlbam.json"))).items():
    RET2MLB[r] = mm
    RETNAME.setdefault(r, nm)

TYPEMAP = {"T": "Trade", "Tp": "Trade", "F": "Signed as Free Agent",
           "Fo": "Signed as Free Agent", "Fg": "Declared Free Agency",
           "W": "Claimed Off Waivers", "D": "Rule 5 Selection", "R": "Released"}

deals = defaultdict(list)   # txid -> rows
n_raw = 0
for raw in open(TRAN, encoding="latin-1"):
    f = next(csv.reader([raw]))
    if len(f) < 13: continue
    d = f[0]
    if not ("1985" <= d[:4] <= "2008"): continue
    if d[4:6] == "00": continue
    if d[6:8] == "00": d = d[:6] + "15"
    date = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    ttype = f[7].strip()
    if ttype not in TYPEMAP: continue
    txid, player = f[5], f[6].strip()
    ft, tt = f[8].strip(), f[10].strip()
    if ft and ft not in TEAM: ft = ""
    if tt and tt not in TEAM: tt = ""
    if not ft and not tt: continue
    yr = int(date[:4])
    pid = RET2MLB.get(player)
    pname = RETNAME.get(player) or (player if " " in player else None)
    deals[(txid, TYPEMAP[ttype])].append(dict(
        date=date, t=TYPEMAP[ttype], pid=pid, pname=pname,
        ft=era_name(ft, yr) if ft else None, ftid=TEAM.get(ft),
        tt=era_name(tt, yr) if tt else None, ttid=TEAM.get(tt)))
    n_raw += 1
print(f"retro rows mapped: {n_raw} in {len(deals)} transactions")

con = sqlite3.connect("/work/ledger.sqlite")
con.execute("delete from sweep_tx where tx_id like 'retro-%'")
ins = 0
for (txid, ttype), rows in deals.items():
    date = rows[0]["date"]
    if ttype == "Trade":
        sides = defaultdict(list)
        for r in rows:
            who = r["pname"] or "player"
            if r["ft"] and r["tt"]: sides[(r["ft"], r["tt"])].append(who)
        parts = [f"{a} traded {', '.join(ps)} to {b}" for (a, b), ps in sides.items()]
        desc = "; ".join(parts)[:220] + " (Retrosheet archive)"
        tids = {r["ftid"] for r in rows if r["ftid"]} | {r["ttid"] for r in rows if r["ttid"]}
        for tid in tids:
            for r in rows:
                con.execute("insert into sweep_tx values (?,?,?,?,?,?,?,?,?)",
                    (tid, f"retro-{txid}-{tid}", date, "Trade", r["pid"], r["pname"],
                     r["ft"], r["tt"], desc))
                ins += 1
    else:
        for r in rows:
            tid = r["ttid"] or r["ftid"]
            if not tid: continue
            who = r["pname"] or "player"
            verb = {"Signed as Free Agent": f"signed free agent {who}",
                    "Declared Free Agency": f"{who} elected free agency",
                    "Claimed Off Waivers": f"claimed {who} off waivers",
                    "Rule 5 Selection": f"selected {who} in the Rule 5 draft",
                    "Released": f"released {who}"}[r["t"]]
            club = r["tt"] or r["ft"]
            desc = f"{club} {verb}. (Retrosheet archive)"
            con.execute("insert into sweep_tx values (?,?,?,?,?,?,?,?,?)",
                (tid, f"retro-{txid}-{tid}", date, r["t"], r["pid"], r["pname"],
                 r["ft"], r["tt"], desc))
            ins += 1
con.commit()
print(f"inserted {ins} sweep_tx rows from Retrosheet")
for y, n in con.execute("select substr(date,1,4), count(*) from sweep_tx where type_desc='Trade' and date<'2009' group by 1 order by 1"):
    print(y, n)
