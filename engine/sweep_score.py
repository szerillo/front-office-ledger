"""
THE 30-REGIME SWEEP: score every active MLB front office with Ledger WAR v0.
Outputs sweep_results.json for the prototype leaderboard.

Sweep v1 rules (documented; versioned):
  TRADE   acquired = LVM seasons with this club, [tx_year, tx_year+5];
          surrendered = LVM seasons elsewhere, same window. Net from this seat.
  WAIVER/RULE 5  claim: LVM with club [y, y+3]; loss: -LVM elsewhere [y, y+3].
  DRAFT   picks rounds 1-5 (value tail beyond r5 noted, not graded):
          realized = LVM while on drafting org; expectation = slot curve x
          maturity schedule. FA: raw LVM captured [y, y+3], UNGRADED pending a
          contracts feed. Success: W% + division titles from standings feed.
SWEEP v2: trades use CONTROL WINDOWS (value counts while the player stays
with the club, 6-season cap, stopping when he leaves the org: a re-signing
is a new decision), win-curve LEVERAGE (each delivered season weighted by
L(w) = 0.5 + 1.3*exp(-(w-89)^2/200) at the receiving club's win total, so
wins delivered to a contender count up to ~1.8x and wins to a 70-win club
~0.65x) and 10%/yr TIME DISCOUNTING back to the deal date, per methodology
v0.2. FA/waiver channels stay unweighted (cost and value accrue in the same
seasons, so leverage cancels to first order there).
LEGACY CRUDENESS (v1): windows were calendar approximations (5-yr cap
mitigates); no leverage/discounting (v0.2 applies at the decision page
level, not yet in the sweep); LVM gaps as documented in ledger_war.py.
"""
import json, math, sqlite3, sys
from collections import defaultdict
from ledger_war import get, API, lvm_batting, lvm_pitching

DB = "/home/claude/ledger.sqlite"
END_YEAR = 2026

# ---------- draft curve (from elias_ledger) ----------
def slot_expectation(pick):
    table = [(1, 9.9), (2, 7.5), (3, 6.7), (5, 5.5), (8, 4.6), (12, 3.6), (17, 3.0),
             (22, 2.6), (30, 2.1), (45, 1.5), (65, 1.1), (90, 0.85), (120, 0.6),
             (200, 0.35), (400, 0.18), (620, 0.10)]
    if pick <= 1: return table[0][1]
    for (p1, v1), (p2, v2) in zip(table, table[1:]):
        if pick <= p2:
            f = (math.log(pick) - math.log(p1)) / (math.log(p2) - math.log(p1))
            return v1 + f * (v2 - v1)
    return 0.10
MATURITY = {0: 0.0, 1: 0.02, 2: 0.10, 3: 0.22, 4: 0.38, 5: 0.55, 6: 0.70, 7: 0.82}
def maturity(dy, asof=2025):
    n = max(0, asof - dy)
    return MATURITY.get(n, 0.82 + min(0.18, 0.02 * (n - 7)))

def grade(nps):
    for thr, g in [(2.6,80),(1.8,75),(1.2,70),(0.8,65),(0.5,60),(0.2,55),
                   (-0.2,50),(-0.6,45),(-1.0,40),(-1.6,35)]:
        if nps >= thr: return g
    return 30
def grade_comp(nps):
    for thr, g in [(8.0,80),(5.5,75),(3.5,70),(2.2,65),(1.2,60),(0.4,55),
                   (-0.4,50),(-1.2,45),(-2.2,40),(-3.5,35)]:
        if nps >= thr: return g
    return 30
def success_grade(wpct, div):
    base = 65 if wpct>=.560 else 60 if wpct>=.540 else 55 if wpct>=.520 else \
           50 if wpct>=.500 else 45 if wpct>=.480 else 40 if wpct>=.460 else 35 if wpct>=.440 else 30
    return min(80, base + min(10, 3*div))

# ---------- per-team per-year LVM ----------
def player_team_seasons(ids):
    out = {}
    ids = [i for i in ids if i]
    for i in range(0, len(ids), 40):
        chunk = ",".join(str(x) for x in ids[i:i+40])
        try:
            d = get(f"{API}/people?personIds={chunk}&hydrate=stats(group=[hitting,pitching],type=[yearByYear])")
        except Exception as e:
            print(f"  batch fail {i}: {e}", flush=True); continue
        for p in d.get("people", []):
            pos = p["primaryPosition"]["abbreviation"]
            rows = []
            for grp in p.get("stats", []):
                g = grp["group"]["displayName"]
                for sp in grp.get("splits", []):
                    tm = (sp.get("team") or {}).get("name")
                    if not tm: continue
                    yr = int(sp["season"]); st = sp["stat"]
                    if g == "hitting" and st.get("plateAppearances"):
                        rows.append((yr, tm, lvm_batting(st, yr, pos)))
                    elif g == "pitching" and st.get("inningsPitched"):
                        rows.append((yr, tm, lvm_pitching(st, yr)))
            out[p["id"]] = dict(name=p["fullName"], rows=rows)
        if (i // 40) % 10 == 0: print(f"  LVM {i}/{len(ids)}", flush=True)
    return out

def val(pid, teams, y0, y1, inside=True):
    rec = LVM.get(int(pid)) if pid else None
    if not rec: return 0.0
    tot = 0.0
    for yr, tm, v in rec["rows"]:
        if y0 <= yr <= y1 and ((tm in teams) == inside):
            tot += v
    return tot

# ---------- main ----------
cfg = json.load(open("/home/claude/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
con = sqlite3.connect(DB); con.row_factory = sqlite3.Row

# collect universe
universe = set()
regime_rows = {}
for reg in cfg["regimes"]:
    tid = reg["teamId"]; start = max(reg["start"], "2005-01-01")
    rows = [dict(r) for r in con.execute(
        "select * from sweep_tx where team_id=? and date>=? and type_desc in "
        "('Trade','Claimed Off Waivers','Rule 5 Selection','Signed as Free Agent','Declared Free Agency')",
        (tid, start))]
    regime_rows[tid] = rows
    for r in rows:
        if r["person_id"]: universe.add(int(r["person_id"]))
drafts = {}
for reg in cfg["regimes"]:
    tid = reg["teamId"]
    names = ALIAS.get(tid, {reg["team"]})
    y0 = max(int(reg["start"][:4]) + (0 if reg["start"][5:7] < "07" else 1), 2005)
    q = "select * from draft_picks where cast(year as int)>=? and cast(round as int)<=5 and team in (%s)" % \
        ",".join("?"*len(names))
    picks = [dict(r) for r in con.execute(q, (y0, *names))]
    drafts[tid] = picks
    for p in picks:
        if p["person_id"]: universe.add(int(p["person_id"]))
print(f"universe: {len(universe)} persons", flush=True)
import os
if os.path.exists("/home/claude/lvm_cache.json"):
    LVM = {int(k): v for k, v in json.load(open("/home/claude/lvm_cache.json")).items()}
    missing = sorted(universe - set(LVM))
    if missing: LVM.update(player_team_seasons(missing))
else:
    LVM = player_team_seasons(sorted(universe))
json.dump(LVM, open("/home/claude/lvm_cache.json", "w"))
print(f"LVM ready for {len(LVM)} persons", flush=True)

# standings for success
wl = defaultdict(lambda: [0, 0, 0])  # (team, year) -> [w, l, divrank1]
for yr in range(2005, 2027):
    try:
        d = get(f"{API}/standings?leagueId=103,104&season={yr}&standingsTypes=regularSeason")
    except Exception: continue
    for recgrp in d.get("records", []):
        for t in recgrp.get("teamRecords", []):
            wl[(t["team"]["id"], yr)] = [t.get("wins",0), t.get("losses",0), 1 if str(t.get("divisionRank"))=="1" else 0]
print("standings loaded", flush=True)

NAME2TID = {}
for _reg in cfg["regimes"]:
    NAME2TID[_reg["team"]] = _reg["teamId"]
    for _al in ALIAS.get(_reg["teamId"], set()):
        NAME2TID[_al] = _reg["teamId"]

import math
def lev(team_name_or_names, yr):
    """win-curve leverage at the receiving club's final win total (proxy
    for decision-time projection); 1.0 when unknown (minors, pre-2005)."""
    if isinstance(team_name_or_names, set):
        tids = {NAME2TID.get(n) for n in team_name_or_names} - {None}
        tid = next(iter(tids), None)
    else:
        tid = NAME2TID.get(team_name_or_names)
    rec = wl.get((tid, yr)) if tid else None
    if not rec or (rec[0] + rec[1]) < 100: return 1.0
    w = rec[0] * 162 / (rec[0] + rec[1])
    return 0.5 + 1.3 * math.exp(-((w - 89) ** 2) / 200.0)

def val_control(pid, teams, y0, cap=6, weight=True):
    """value on `teams` from y0 while continuously in the org (control
    window): stops the first season the player logs MLB time only elsewhere
    after the deal year. Each season weighted by leverage x 0.9^(yr-y0)."""
    rec = LVM.get(int(pid)) if pid else None
    if not rec: return 0.0
    byyear = {}
    for yr, tm, v in rec["rows"]:
        byyear.setdefault(yr, []).append((tm, v))
    tot = 0.0
    for yr in range(y0, y0 + cap):
        rows = byyear.get(yr, [])
        here = [v for (tm, v) in rows if tm in teams]
        if rows and not here and yr > y0:
            break                      # left the org: window closes
        if here:
            wgt = (lev(teams, yr) * (0.9 ** (yr - y0))) if weight else 1.0
            tot += sum(here) * wgt
    return tot

results = []
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    start = max(reg["start"], "2005-01-01"); y_start = int(start[:4])
    seasons = round((END_YEAR + 0.55) - (y_start + (1 if start[5:7] > "07" else 0)), 1)
    seasons = max(seasons, 0.7)
    decs = []
    ynet = defaultdict(float)
    # trades
    trades = defaultdict(list)
    seen_fa = set(); fa_raw = 0.0; n_fa = 0; walk = []
    n_wv = n_r5 = 0; wv_net = 0.0
    for r in regime_rows[tid]:
        t = r["type_desc"]; yr = int(r["date"][:4])
        if t == "Trade":
            trades[(r["date"], r["description"])].append(r)
        elif t == "Claimed Off Waivers":
            claim = r["to_team"] in names
            v = val(r["person_id"], names if claim else {r["to_team"]}, yr, yr+3, inside=True)
            net = v if claim else -v
            wv_net += net; n_wv += 1; ynet[yr] += net
            if abs(net) > 0.05:
                decs.append(dict(d=r["date"], ch="waiver", net=round(net,1),
                                 h=(r["description"] or "waiver claim")[:110]))
        elif t == "Rule 5 Selection":
            pick = r["to_team"] in names
            v = val(r["person_id"], names if pick else {r["to_team"]}, yr, yr+3, inside=True)
            r5n = (v if pick else -v)
            wv_net += r5n; n_r5 += 1; ynet[yr] += r5n
        elif t == "Declared Free Agency":
            pid = r["person_id"]
            if pid:
                played_here = val(pid, names, yr - 2, yr, inside=True)
                if played_here > 0.5:
                    lost = val(pid, names, yr + 1, yr + 3, inside=False)
                    if lost > 1.0:
                        walk.append(dict(d=r["date"], ch="walk", net=round(-lost, 1),
                            h=f"Let {r['person_name']} walk as a free agent · {lost:.1f} LVM elsewhere over the next 3 seasons"))
        elif t == "Signed as Free Agent":
            key = (r["date"], r["person_id"])
            if key in seen_fa or "minor league" in (r["description"] or "").lower(): continue
            seen_fa.add(key); n_fa += 1
            fa_raw += val(r["person_id"], names, yr, yr+3, inside=True)
    tr_net = 0.0
    for (d, desc), rs in trades.items():
        yr = int(d[:4])
        pids_in  = {x["person_id"] for x in rs if x["to_team"] in names and x["person_id"]}
        outs = {x["person_id"]: x["to_team"] for x in rs
                if x["from_team"] in names and x["person_id"] and x["to_team"]}
        vin  = sum(val_control(p, names, yr) for p in pids_in)
        vout = sum(val_control(p, {dest}, yr) for p, dest in outs.items())
        net = vin - vout; tr_net += net; ynet[yr] += net
        if abs(net) >= 0.8:
            decs.append(dict(d=d, ch="trade", net=round(net,1), h=(desc or "trade")[:130],
                             vin=round(vin,1), vout=round(vout,1)))
    # draft
    dr_real = dr_exp = 0.0
    for p in drafts[tid]:
        yr = int(p["year"]); pk = int(p["pick_overall"])
        realized = val(p["person_id"], names, yr, END_YEAR, inside=True)
        exp = slot_expectation(pk) * maturity(yr)
        dr_real += realized; dr_exp += exp
        net = realized - exp; ynet[yr] += net
        if abs(net) >= 1.2:
            decs.append(dict(d=f"{yr}-06-15", ch="draft", net=round(net,1),
                             h=f"Drafted {p['person_name']} (#{pk} overall, {yr})"))
    dr_net = dr_real - dr_exp
    total = tr_net + dr_net + wv_net
    w = l = div = 0
    for yr in range(y_start, 2027):
        rec = wl.get((tid, yr))
        if rec: w += rec[0]; l += rec[1]; div += rec[2]
    wpct = w / (w + l) if (w + l) else 0.5
    decs.sort(key=lambda x: -abs(x["net"]))
    walk.sort(key=lambda x: x["net"])
    def chbw(ch, n=5):
        pool = [d for d in decs if d["ch"] == ch]
        best = sorted([d for d in pool if d["net"] > 0], key=lambda x: -x["net"])[:n]
        worst = sorted([d for d in pool if d["net"] < 0], key=lambda x: x["net"])[:n]
        return dict(best=best, worst=worst)
    results.append(dict(
        id=reg["abbr"].lower(), teamId=tid, exec=reg["exec"], team=reg["team"], abbr=reg["abbr"],
        start=y_start, seasons=seasons, flags=reg.get("flags", []),
        chan=dict(
            trade=dict(net=round(tr_net,1), g=grade(tr_net/seasons), n=len(trades)),
            draft=dict(net=round(dr_net,1), g=grade(dr_net/seasons), n=len(drafts[tid])),
            waiver=dict(net=round(wv_net,1), g=grade(wv_net/seasons), n=n_wv+n_r5),
            fa=dict(net=round(fa_raw,1), g=None, n=n_fa),
        ),
        total=round(total,1), forGrade=grade_comp(total/seasons),
        success=dict(wpct=f"{wpct:.3f}".lstrip('0'), div=div, g=success_grade(wpct, div), w=w, l=l),
        cum=[round(sum(ynet[y] for y in range(y_start, yy + 1)), 1) for yy in range(y_start, 2027)],
        top=decs[:8],
        led=dict(trade=chbw("trade"), draft=chbw("draft"), waiver=chbw("waiver", 4)),
        walk=walk[:5],
    ))
    print(f"{reg['abbr']}: trades {tr_net:+.1f} | draft {dr_net:+.1f} | waiver {wv_net:+.1f} "
          f"| FA raw {fa_raw:+.1f} (ungraded) | total {total:+.1f} over {seasons} yrs", flush=True)

json.dump(results, open("/home/claude/sweep_results.json", "w"), indent=1)
print("WROTE sweep_results.json", flush=True)
