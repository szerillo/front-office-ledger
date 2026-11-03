"""Skill profiles for the 2026-27 free-agent class, used by the simulator's
league market: each club bids more for the kind of player its acquisitions
have favored (Org DNA fingerprints) and less for a poor fit.

Batters: Statcast plate-discipline and contact quality, z-scored within
season (2025 and 2026, weighted by playing time). Pitchers: the same for
arms. Defense: runs per full season (DRS at 1B/2B/3B/SS, Fielding Run Value
at C and in the outfield), 2025-26.
Output: fa_skills.json {pid: {"s": "b"|"p", "z": {...}, "d": runs or null}}
"""
import csv, io, json, time, urllib.request
from statistics import mean, pstdev

BAT_SEL = "pa,k_percent,bb_percent,xwoba,barrel_batted_rate,hard_hit_percent,oz_swing_percent,whiff_percent,sprint_speed"
PIT_SEL = "p_formatted_ip,k_percent,bb_percent,xwoba,oz_swing_percent,whiff_percent,groundballs_percent,fastball_avg_speed"

def get(u, tries=3):
    for a in range(tries):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(3 + 3 * a)
    return ""

def season(year, side):
    sel = BAT_SEL if side == "bat" else PIT_SEL
    mn = 50 if side == "bat" else 20
    u = (f"https://baseballsavant.mlb.com/leaderboard/custom?year={year}&type={'batter' if side=='bat' else 'pitcher'}"
         f"&filter=&min={mn}&selections={sel}&chart=false&x=pa&y=pa&r=no&chartType=beeswarm&sort=k_percent&sortDir=desc&csv=true")
    t = get(u)
    rows = {}
    if not t or "player_id" not in t.splitlines()[0]: return rows
    for r in csv.DictReader(io.StringIO(t.lstrip("﻿"))):
        pid = r.get("player_id")
        if not pid: continue
        c = {}
        for k, v in r.items():
            if k in ("last_name, first_name", "player_id", "year"): continue
            try: c[k] = float(str(v).strip('"'))
            except (ValueError, TypeError): pass
        rows[int(pid)] = c
    return rows

def zscore(rows, wkey):
    mets = {}
    for p in rows.values():
        for k, v in p.items():
            if k != wkey: mets.setdefault(k, []).append(v)
    st = {k: (mean(v), pstdev(v)) for k, v in mets.items() if len(v) > 50 and pstdev(v) > 1e-9}
    return {pid: ({k: (v - st[k][0]) / st[k][1] for k, v in p.items() if k in st}, p.get(wkey, 0)) for pid, p in rows.items()}

D = json.load(open("/work/desk_data.json"))
want = set(D.get("fa27", [])) | {p[1] for p in D["players"] if (D.get("status", {}).get(str(p[1])) or [None])[0] in ("fa", "pendfa", "posted")}
out = {}
for side, wkey, tag in (("bat", "pa", "b"), ("pit", "p_formatted_ip", "p")):
    acc = {}
    for y, yw in ((2025, 3), (2026, 5)):
        for pid, (z, n) in zscore(season(y, side), wkey).items():
            if pid not in want: continue
            w = yw * max(n, 1)
            a = acc.setdefault(pid, [{}, 0.0])
            for k, v in z.items(): a[0][k] = a[0].get(k, 0) + v * w
            a[1] += w
        time.sleep(0.6)
    for pid, (zs, w) in acc.items():
        if w <= 0: continue
        prev = out.get(str(pid))
        rec = {"s": tag, "z": {k: round(v / w, 2) for k, v in zs.items()}}
        # two-way or position change: keep the side with more playing time
        if prev is None or (tag == "b" and prev["s"] == "p"):
            out[str(pid)] = rec

# defense: DRS for infield innings, FRV for catchers and outfielders, 2025-26
DRS = json.load(open("/work/drs_runs.json")); FRV = json.load(open("/work/frv_runs.json"))
for pid in list(out):
    if out[pid]["s"] != "b": continue
    runs = inn = 0.0
    for y in ("2025", "2026"):
        d = (DRS.get(pid) or {}).get(y) or {}
        for pos, r in (d.get("pos") or {}).items():
            if pos in ("3", "4", "5", "6"): runs += r; inn += (d.get("inn") or {}).get(pos, 0)
        f = (FRV.get(pid) or {}).get(y) or {}
        for pos, r in (f.get("pos") or {}).items():
            if pos in ("2", "7", "8", "9"): runs += r; inn += (f.get("outs") or {}).get(pos, 0) / 3.0
    out[pid]["d"] = round(runs * 1200 / inn, 1) if inn >= 300 else None
json.dump(out, open("/work/fa_skills.json", "w"), separators=(",", ":"))
print("fa_skills.json:", len(out), "players;", sum(1 for v in out.values() if v.get("d") is not None), "with defense")
