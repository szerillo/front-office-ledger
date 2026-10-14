"""
HISTORICAL REGIME SWEEP ("Archive era"): score past MLB front offices
2005-2024 with the same engine as the active 30-regime sweep, generalized
to regime windows with END DATES.

Rules, identical to sweep v2 where applicable:
  TRADE   control windows, win-curve leverage, 10%/yr discounting; only
          deals dated inside [start, end] count. Value realized after the
          regime ends still credits the decision (credit follows the
          decision-maker, same philosophy as DEV's traded-prospect rule).
  DRAFT   rounds 1-5, slot expectation x maturity(asof=2026): realized value
          on the drafting org through 2026 credits the drafting regime.
  WAIVER/RULE 5  claims/losses dated inside the window, 3-yr value.
  SUCCESS W%, division titles over seasons the regime held the seat.
  FA      raw captured value, UNGRADED for archive regimes (the graded FA
          book covers the current-regime contract universe); disclosed.
  DEV/EXT not scored for archive regimes (Pipeline-archive DEV and the
          extension book are built around active windows); disclosed.

Data floor is 2005-01-01 (transaction feed reliability); regimes that
started earlier are truncated and flagged, with trueStart shown.
Writes hist_results.json.
"""
import json, math, os, sqlite3
from collections import defaultdict
from ledger_war import get, API
from lvm15 import player_team_seasons_v15

DB = "/home/claude/ledger.sqlite"
END_YEAR = 2026

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
def maturity(dy, asof=END_YEAR):
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

hcfg = json.load(open("/home/claude/regimes_hist.json"))
cfg = json.load(open("/home/claude/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
con = sqlite3.connect(DB); con.row_factory = sqlite3.Row

REGS = hcfg["regimes"]

# ---- universe ----
universe = set()
regime_rows = {}
drafts = {}
for i, reg in enumerate(REGS):
    tid = reg["teamId"]; start = max(reg["start"], "2005-01-01"); end = reg["end"]
    rows = [dict(r) for r in con.execute(
        "select * from sweep_tx where team_id=? and date>=? and date<=? and type_desc in "
        "('Trade','Claimed Off Waivers','Rule 5 Selection','Signed as Free Agent','Declared Free Agency')",
        (tid, start, end))]
    regime_rows[i] = rows
    for r in rows:
        if r["person_id"]: universe.add(int(r["person_id"]))
    names = ALIAS.get(tid, {reg["team"]})
    picks = []
    for yr in range(max(int(start[:4]), 2005), int(end[:4]) + 1):
        marker = f"{yr}-06-01"
        if start <= marker <= end:
            q = "select * from draft_picks where cast(year as int)=? and cast(round as int)<=5 and team in (%s)" % \
                ",".join("?"*len(names))
            picks += [dict(r) for r in con.execute(q, (yr, *names))]
    drafts[i] = picks
    for p in picks:
        if p["person_id"]: universe.add(int(p["person_id"]))
print(f"archive universe: {len(universe)} persons", flush=True)
REDRAFT = {}
for pid, yy in con.execute("select person_id, cast(year as int) from draft_picks where person_id is not null"):
    REDRAFT.setdefault(str(pid), set()).add(yy)
REDRAFT = {k: v for k, v in REDRAFT.items() if len(v) > 1}

_raw = json.load(open("/home/claude/lvm_cache.json"))
_meta = {k: v for k, v in _raw.items() if k.startswith("__")}
LVM = {int(k): v for k, v in _raw.items() if not k.startswith("__")}
missing = sorted(universe - set(LVM))
print(f"missing from cache: {len(missing)}", flush=True)
if missing:
    LVM.update(player_team_seasons_v15(missing))
    _dump = {str(k): v for k, v in LVM.items()}
    _dump.update(_meta)
    json.dump(_dump, open("/home/claude/lvm_cache.json", "w"))
print(f"LVM ready: {len(LVM)}", flush=True)

def val(pid, teams, y0, y1, inside=True):
    rec = LVM.get(int(pid)) if pid else None
    if not rec: return 0.0
    tot = 0.0
    for yr, tm, v in rec["rows"]:
        if y0 <= yr <= y1 and ((tm in teams) == inside):
            tot += v
    return tot

wl = defaultdict(lambda: [0, 0, 0])
for yr in range(2005, 2027):
    try:
        d = get(f"{API}/standings?leagueId=103,104&season={yr}&standingsTypes=regularSeason")
    except Exception: continue
    for recgrp in d.get("records", []):
        for t in recgrp.get("teamRecords", []):
            wl[(t["team"]["id"], yr)] = [t.get("wins",0), t.get("losses",0), 1 if str(t.get("divisionRank"))=="1" else 0]
print("standings loaded", flush=True)

POS = json.load(open("/home/claude/positions.json"))
PITPOS = {"RHP", "LHP", "SP", "RP"}
def ptype(pid):
    return "pit" if POS.get(str(pid)) in PITPOS else "bat"

NAME2TID = {}
for _reg in cfg["regimes"]:
    NAME2TID[_reg["team"]] = _reg["teamId"]
    for _al in ALIAS.get(_reg["teamId"], set()):
        NAME2TID[_al] = _reg["teamId"]

def lev(team_name_or_names, yr):
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
            break
        if here:
            wgt = (lev(teams, yr) * (0.9 ** (yr - y0))) if weight else 1.0
            tot += sum(here) * wgt
    return tot

def frac_year(ds):
    return int(ds[:4]) + (int(ds[5:7]) - 1) / 12.0

results = []
for i, reg in enumerate(REGS):
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    start = max(reg["start"], "2005-01-01"); end = reg["end"]
    y_start, y_end = int(start[:4]), int(end[:4])
    seasons = max(0.7, round(frac_year(end) - frac_year(start), 1))
    # seasons the regime held the seat (for success record)
    s_first = y_start + (1 if start[5:7] > "07" else 0)
    s_last = y_end - (1 if end[5:7] < "04" else 0)
    decs = []
    ynet = defaultdict(float)
    trades = defaultdict(list)
    seen_fa = set(); fa_raw = 0.0; n_fa = 0; walk = []
    n_wv = n_r5 = 0; wv_net = 0.0
    for r in regime_rows[i]:
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
                                 h=(r["description"] or "waiver claim")[:110],
                                 sides=[[("Claimed · 3-yr value on club" if claim else "Lost on waivers · 3-yr value elsewhere"),
                                         [[r["person_name"] or "?", f"{net:+.1f}"]]],
                                        ["Baseline", [["waiver channel expectation", "0.0"]]]],
                                 pids=[r["person_id"]]))
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
                            h=f"Let {r['person_name']} walk as a free agent · {lost:.1f} LVM elsewhere over the next 3 seasons",
                            sides=[["Production lost (next 3 seasons, other clubs)", [[r["person_name"], f"{-lost:+.1f}"]]],
                                   ["Received", [["nothing (no compensation modeled)", "0.0"]]]],
                            pids=[r["person_id"]]))
        elif t == "Signed as Free Agent":
            key = (r["date"], r["person_id"])
            if key in seen_fa or "minor league" in (r["description"] or "").lower(): continue
            seen_fa.add(key); n_fa += 1
            fa_raw += val(r["person_id"], names, yr, yr+3, inside=True)
    tr_net = 0.0
    pname = {}
    for x in regime_rows[i]:
        if x["person_id"]: pname[x["person_id"]] = x["person_name"]
    for (d, desc), rs in trades.items():
        yr = int(d[:4])
        pids_in  = {x["person_id"] for x in rs if x["to_team"] in names and x["person_id"]}
        outs = {x["person_id"]: x["to_team"] for x in rs
                if x["from_team"] in names and x["person_id"] and x["to_team"]}
        ins_det = [(p, pname.get(p, "?"), val_control(p, names, yr)) for p in pids_in]
        out_det = [(p, pname.get(p, "?"), dest, val_control(p, {dest}, yr)) for p, dest in outs.items()]
        vin  = sum(v for (_, _, v) in ins_det)
        vout = sum(v for (_, _, _, v) in out_det)
        net = vin - vout; tr_net += net; ynet[yr] += net
        if abs(net) >= 1.2:
            dests = sorted({dest for (_, _, dest, _) in out_det})
            sides = [["Acquired (control-window value, leverage-weighted)",
                      [[nm, f"{v:+.1f}"] for (_, nm, v) in sorted(ins_det, key=lambda t: -t[2])] or [["(no valued players)", "0.0"]]],
                     ["Surrendered · value realized on " + (", ".join(dests) if dests else "counterparty"),
                      [[nm, f"{-v:+.1f}"] for (_, nm, _, v) in sorted(out_det, key=lambda t: -t[3])] or [["(no valued players)", "0.0"]]]]
            decs.append(dict(d=d, ch="trade", net=round(net,1), h=(desc or "trade")[:130],
                             vin=round(vin,1), vout=round(vout,1), sides=sides,
                             pids=[p for (p, _, _) in ins_det] + [p for (p, _, _, _) in out_det]))
    dr_real = dr_exp = 0.0
    for p in drafts[i]:
        yr = int(p["year"]); pk = int(p["pick_overall"])
        later = REDRAFT.get(str(p["person_id"]), ())
        unsigned = any(y2 > yr for y2 in later)
        realized = 0.0 if unsigned else val(p["person_id"], names, yr, END_YEAR, inside=True)
        exp = slot_expectation(pk) * maturity(yr) * (0.5 if unsigned else 1.0)
        dr_real += realized; dr_exp += exp
        net = realized - exp; ynet[yr] += net
        if abs(net) >= 1.5:
            decs.append(dict(d=f"{yr}-06-15", ch="draft", net=round(net,1),
                             h=f"Drafted {p['person_name']} (#{pk} overall, {yr})",
                             sides=[["Realized on club", [[p["person_name"], f"{realized:+.1f}"]]],
                                    ["Slot expectation", [[f"pick #{pk}, maturity-adjusted", f"{-exp:+.1f}"]]]],
                             pids=[p["person_id"]]))
    dr_net = dr_real - dr_exp
    total = tr_net + dr_net + wv_net
    w = l = div = 0
    for yr in range(s_first, s_last + 1):
        rec = wl.get((tid, yr))
        if rec: w += rec[0]; l += rec[1]; div += rec[2]
    wpct = w / (w + l) if (w + l) else 0.5
    decs.sort(key=lambda x: -abs(x["net"]))
    walk.sort(key=lambda x: x["net"])
    def chbw(ch, n=4):
        pool = [d for d in decs if d["ch"] == ch]
        best = sorted([d for d in pool if d["net"] > 0], key=lambda x: -x["net"])[:n]
        worst = sorted([d for d in pool if d["net"] < 0], key=lambda x: x["net"])[:n]
        return dict(best=best, worst=worst)
    slug = (reg["abbr"] + "-" + reg["exec"]).lower().replace(" ", "-").replace(".", "")
    results.append(dict(
        id=slug, teamId=tid, exec=reg["exec"], team=reg["team"], abbr=reg["abbr"],
        start=y_start, end=y_end, startDate=reg["start"], endDate=end,
        trueStart=reg.get("trueStart"), seasons=seasons, flags=reg.get("flags", []),
        chan=dict(
            trade=dict(net=round(tr_net,1), g=grade(tr_net/seasons), n=len(trades)),
            draft=dict(net=round(dr_net,1), g=grade(dr_net/seasons), n=len(drafts[i])),
            waiver=dict(net=round(wv_net,1), g=grade(wv_net/seasons), n=n_wv+n_r5),
            fa=dict(net=round(fa_raw,1), g=None, n=n_fa),
        ),
        total=round(total,1), forGrade=grade_comp(total/seasons),
        success=dict(wpct=f"{wpct:.3f}".lstrip('0'), div=div, g=success_grade(wpct, div), w=w, l=l),
        cum=[round(sum(ynet[y] for y in range(y_start, yy + 1)), 1) for yy in range(y_start, y_end + 1)],
        top=decs[:8],
        led=dict(trade=chbw("trade"), draft=chbw("draft"), waiver=chbw("waiver", 3)),
        walk=walk[:4],
    ))
    print(f"{reg['abbr']} {reg['exec']}: trades {tr_net:+.1f} | draft {dr_net:+.1f} | waiver {wv_net:+.1f} "
          f"| total {total:+.1f} over {seasons} yrs | {w}-{l}", flush=True)

json.dump(results, open("/home/claude/hist_results.json", "w"), indent=1)
print("WROTE hist_results.json", flush=True)
