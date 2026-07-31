"""SWEEP v2 part 1: real postseason detail in the Success grade.

Pulls postseason series 2005-2025 from statsapi, derives per team-season:
berth (played any postseason game), series wins (WC counts when won),
pennant (won LCS), WS title. Blends into the Success grade:

  base = W% points (as v1)  +  2.0/season-normalized bonus mix:
  score/season = 1.2*div + 0.8*berth + 0.6*seriesW + 1.5*pennant + 3.0*WS
  Success 20-80 = W% anchor shifted by postseason rate vs league norm.

Concretely (documented): success_pts = wpct_z + october_z where
  wpct_z = (wpct - .500) * 40      (a .560 club ~ +2.4/season)
  october = (0.8*berths + 0.6*sw + 1.5*pen + 3.0*ws + 1.2*div) / seasons
  october_z = october - 0.55       (league mean: ~1/3 berth rate etc.)
Bands: >=3.2 A+ ... same ladder as channels scaled 2x.

Writes postseason.json {teamId: {year: {berth,sw,pennant,ws}}} and updates
sweep_results.json success blocks in place (po, sw, pen, ws, g).
"""
import json, time, urllib.request

def get(u, tries=3):
    req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception: time.sleep(2 + 2*a)
    return {}

import os
PS = {}  # (teamId, year) -> dict(berth, sw, pennant, ws)
if os.path.exists("/home/claude/postseason.json"):
    for k, rec in json.load(open("/home/claude/postseason.json")).items():
        tid, y = k.split(":"); PS[(int(tid), int(y))] = rec
def bump(tid, y, k, v=1):
    rec = PS.setdefault((tid, y), dict(berth=0, sw=0, pennant=0, ws=0))
    rec[k] = rec[k] + v if k == "sw" else max(rec[k], v)

for yr in ([] if PS else range(2005, 2026)):
    d = get(f"https://statsapi.mlb.com/api/v1/schedule/postseason/series?season={yr}&fields=series,id,gameType,games,teams,away,home,team,id,isWinner")
    for s in d.get("series", []):
        gt = s["series"]["gameType"]      # F=WC, D=DS, L=LCS, W=WS
        wins = {}
        teams = set()
        for g in s.get("games", []):
            for side in ("away", "home"):
                t = g["teams"][side]; tid = t["team"]["id"]
                teams.add(tid)
                if t.get("isWinner"): wins[tid] = wins.get(tid, 0) + 1
        if not teams: continue
        winner = max(wins, key=wins.get) if wins else None
        for tid in teams:
            bump(tid, yr, "berth")
        if winner is not None:
            bump(winner, yr, "sw")
            if gt == "L": bump(winner, yr, "pennant")
            if gt == "W": bump(winner, yr, "ws")
    print(yr, "series:", len(d.get("series", [])), flush=True)
    time.sleep(0.6)

json.dump({f"{tid}:{y}": rec for (tid, y), rec in PS.items()},
          open("/home/claude/postseason.json", "w"))
print("saved postseason.json:", len(PS), "team-seasons")

# ---- blend into sweep_results ----
cfg = json.load(open("/home/claude/regimes.json"))
REG = {r["teamId"]: r for r in cfg["regimes"]}
res = json.load(open("/home/claude/sweep_results.json"))

def sgrade(pts):
    for thr, g in [(4.5,80),(3.4,75),(2.6,70),(1.9,65),(1.3,60),(0.7,55),
                   (0.0,50),(-0.8,45),(-1.6,40),(-2.6,35)]:
        if pts >= thr: return g
    return 30

print(f"\n{'team':<6}{'W%':>6}{'div':>4}{'PO':>4}{'SW':>4}{'pen':>4}{'WS':>4}   success")
for r in res:
    tid = r["teamId"]
    y0 = max(int(REG[tid]["start"][:4]), 2005)
    if REG[tid]["start"][5:7] > "07": y0 += 1     # regime started after the season
    yrs = list(range(y0, 2026))
    po = sw = pen = ws = 0
    for y in yrs:
        rec = PS.get((tid, y))
        if rec:
            po += rec["berth"]; sw += rec["sw"]; pen += rec["pennant"]; ws += rec["ws"]
    s = r["success"]
    wpct = float(s["wpct"])
    seasons = max(1, len(yrs))
    october = (1.2 * (s["div"] if isinstance(s["div"], int) else 0)
               + 0.8 * po + 0.6 * sw + 1.5 * pen + 3.0 * ws) / seasons
    pts = (wpct - 0.500) * 40 + (october - 0.55)
    s.update(po=po, sw=sw, pen=pen, ws=ws, g=sgrade(pts))
    r["titles"] = ws
    print(f"{r['abbr']:<6}{s['wpct']:>6}{s['div']:>4}{po:>4}{sw:>4}{pen:>4}{ws:>4}   {sgrade(pts)} ({pts:+.2f})")

json.dump(res, open("/home/claude/sweep_results.json", "w"), indent=1)
print("\nupdated success blocks in sweep_results.json")
