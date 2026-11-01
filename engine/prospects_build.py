"""Organizational prospects beyond the Top 100 (v5.2).

MLB Pipeline's team Top 30 lists are offline between seasons (the data feed
returns empty lists until the winter re-rank), so the Ledger builds its own
org depth from the minor-league record and prices it empirically:

1. Calibration (2014-2019 minor-league seasons, every MLB affiliate at
   Single-A through Triple-A): each player-season is placed at his highest
   level with a real sample (120 PA / 30 IP), scored by age against the
   level and by production against the level-season average (OPS for
   hitters; strikeouts minus walks per batter faced for pitchers), and
   bucketed: level x age band x production tercile. Excluded: anyone with an
   MLB season before that year and anyone on that winter's Top 100 (they
   are priced by rank). Outcome = the player's actual Ledger WAR over the
   next six seasons (the same span the Top 100 rank curve prices) and in the
   next season alone (the rookie-year figure the depth chart uses).
   Buckets are shrunk toward their level mean (n / (n + 40)).
2. Current: the 2026 minor-league season, same placement and scoring; each
   prospect's bucket value is his expectation. Top 100 prospects get the
   same rookie-year treatment by rank band and level, from the same years.

Writes pros.json: {"org": {pid: [name, org, pit, age2026, level, ev6, y1,
pos, line]}, "rookie": {rank band: {level: y1}}, "calib": {...}}.
"""
import json, os, time, urllib.request
from collections import defaultdict

ROOT = "/work"
CACHE = f"{ROOT}/milb_cache"; os.makedirs(CACHE, exist_ok=True)
LVM = {int(k): v for k, v in json.load(open(f"{ROOT}/lvm_cache.json")).items() if not k.startswith("__")}
AFF = json.load(open(f"{ROOT}/affiliates.json"))
cfg = json.load(open(f"{ROOT}/regimes.json"))
ABBR = {}
for r in cfg["regimes"]:
    ABBR[r["team"]] = r["abbr"]
    for al in cfg["aliases"].get(str(r["teamId"]), []): ABBR[al] = r["abbr"]
RANKS = defaultdict(dict)
for x in json.load(open(f"{ROOT}/prospect_ranks.json")):
    if x["pid"]: RANKS[x["year"]][int(x["pid"])] = x["rank"]

LEVELS = {11: "AAA", 12: "AA", 13: "A+", 14: "A"}
ORDER = {"AAA": 4, "AA": 3, "A+": 2, "A": 1}
TYPICAL = {"AAA": 25.0, "AA": 23.5, "A+": 22.0, "A": 21.0}

def get(u, fn):
    if os.path.exists(fn): return json.load(open(fn))
    for a in range(4):
        try:
            x = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=90))
            json.dump(x, open(fn, "w")); time.sleep(0.3); return x
        except Exception:
            time.sleep(2 + 3 * a)
    return {}

def parent(team, yr):
    yrs = AFF.get(team)
    if not yrs: return None
    if str(yr) in yrs: return ABBR.get(yrs[str(yr)])
    best = min(yrs, key=lambda y: abs(int(y) - yr))
    return ABBR.get(yrs[best])

def ipf(s):
    s = str(s); i, _, f = s.partition("."); return int(i or 0) + (int(f or 0) / 3)

def season_rows(yr):
    """{pid: best row} for one season: highest level with a real sample"""
    rows = {}
    for sid, lvl in LEVELS.items():
        for grp in ("hitting", "pitching"):
            x = get(f"https://statsapi.mlb.com/api/v1/stats?stats=season&group={grp}&sportId={sid}&season={yr}&playerPool=ALL&limit=6000",
                    f"{CACHE}/{yr}_{sid}_{grp}.json")
            for sp in ((x.get("stats") or [{}])[0].get("splits") or []):
                st = sp.get("stat", {}); pl = sp.get("player") or {}; pid = pl.get("id")
                if not pid: continue
                org = parent((sp.get("team") or {}).get("name"), yr)
                if not org: continue          # unaffiliated (e.g. the Mexican League)
                pos = (sp.get("position") or {}).get("abbreviation") or ""
                if grp == "hitting":
                    pa = st.get("plateAppearances", 0) or 0
                    if pa < 120 or pos == "P": continue
                    try: ops = float(st.get("ops") or 0)
                    except ValueError: continue
                    rec = dict(pid=pid, name=pl.get("fullName"), org=org, lvl=lvl, age=st.get("age"), pit=0, n=pa, perf=ops,
                               pos=pos, line=f'{st.get("avg")}/{st.get("obp")}/{st.get("slg")}, {st.get("homeRuns")} HR in {pa} PA')
                else:
                    ip = ipf(st.get("inningsPitched", 0)); bf = st.get("battersFaced", 0) or 0
                    if ip < 30 or bf <= 0: continue
                    kbb = ((st.get("strikeOuts") or 0) - (st.get("baseOnBalls") or 0)) / bf
                    gs, g = st.get("gamesStarted", 0) or 0, st.get("gamesPlayed", 1) or 1
                    rec = dict(pid=pid, name=pl.get("fullName"), org=org, lvl=lvl, age=st.get("age"), pit=1, n=bf, perf=kbb,
                               pos="SP" if gs / g >= 0.5 else "RP",
                               line=f'{st.get("inningsPitched")} IP, {st.get("era")} ERA, {st.get("strikeOuts")} K, {st.get("baseOnBalls")} BB')
                if rec["age"] is None: continue
                cur = rows.get((pid, rec["pit"]))
                if not cur or ORDER[lvl] > ORDER[cur["lvl"]] or (lvl == cur["lvl"] and rec["n"] > cur["n"]):
                    rows[(pid, rec["pit"])] = rec
    # one row per player (two-way: the larger sample)
    out = {}
    for (pid, _), r in rows.items():
        if pid not in out or r["n"] > out[pid]["n"]: out[pid] = r
    # production relative to the level-season mean
    agg = defaultdict(lambda: [0.0, 0])
    for r in out.values():
        k = (r["lvl"], r["pit"]); agg[k][0] += r["perf"] * r["n"]; agg[k][1] += r["n"]
    for r in out.values():
        m = agg[(r["lvl"], r["pit"])]; r["rel"] = r["perf"] - m[0] / max(m[1], 1)
    return out

def mlb_by_year(pid):
    rec = LVM.get(int(pid)); by = defaultdict(float)
    for y, t, v in (rec["rows"] if rec else []): by[y] += v
    return by

def age_band(r):
    d = r["age"] - TYPICAL[r["lvl"]]
    return "young" if d <= -2 else "mid" if d <= 0 else "old"

# ---------- calibration ----------
TERC = {}
cells = defaultdict(list); lvl_all = defaultdict(list); rook = defaultdict(list)
for yr in range(2014, 2020):
    rows = season_rows(yr)
    # tercile cut points per level and type
    by = defaultdict(list)
    for r in rows.values(): by[(r["lvl"], r["pit"])].append(r["rel"])
    cuts = {k: (sorted(v)[len(v) // 3], sorted(v)[2 * len(v) // 3]) for k, v in by.items() if len(v) >= 9}
    TERC[yr] = cuts
    ranked = set(RANKS.get(yr, {})) | set(RANKS.get(yr + 1, {}))
    for pid, r in rows.items():
        by_y = mlb_by_year(pid)
        if any(y < yr for y in by_y): continue          # already an MLB player
        c = cuts.get((r["lvl"], r["pit"]))
        if not c: continue
        t = 0 if r["rel"] < c[0] else 1 if r["rel"] < c[1] else 2
        ev6 = sum(by_y.get(yr + k, 0.0) for k in range(1, 7))
        y1 = by_y.get(yr + 1, 0.0)
        if pid in ranked:
            rk = RANKS.get(yr + 1, {}).get(pid) or RANKS.get(yr, {}).get(pid)
            band = "1-25" if rk <= 25 else "26-50" if rk <= 50 else "51-100"
            rook[(band, r["lvl"])].append(y1)
            continue
        key = (r["lvl"], r["pit"], age_band(r), t)
        cells[key].append((ev6, y1)); lvl_all[(r["lvl"], r["pit"])].append((ev6, y1))
    print("calibration season", yr, "rows", len(rows))

def shrunk(key):
    xs = cells.get(key, []); base = lvl_all.get(key[:2], [(0, 0)])
    m6 = sum(a for a, _ in base) / len(base); m1 = sum(b for _, b in base) / len(base)
    n = len(xs)
    if not n: return m6, m1, 0
    a6 = sum(a for a, _ in xs) / n; a1 = sum(b for _, b in xs) / n
    w = n / (n + 40)
    return w * a6 + (1 - w) * m6, w * a1 + (1 - w) * m1, n
CAL = {f"{k[0]}|{'P' if k[1] else 'H'}|{k[2]}|{k[3]}": [round(v, 2) for v in shrunk(k)[:2]] + [shrunk(k)[2]]
       for k in sorted(set(cells) | {(l, p, a, t) for (l, p) in lvl_all for a in ("young", "mid", "old") for t in (0, 1, 2)})}
ROOK = {}
for (band, lvl), xs in rook.items():
    ROOK.setdefault(band, {})[lvl] = [round(sum(xs) / len(xs), 2), len(xs)]
print("calibration cells (ev6, y1, n):")
for k, v in CAL.items():
    if k.startswith(("AAA", "AA|")): print("  ", k, v)
print("rookie-year by rank band:", ROOK)

# ---------- current: the 2026 season ----------
cur = season_rows(2026)
by = defaultdict(list)
for r in cur.values(): by[(r["lvl"], r["pit"])].append(r["rel"])
cuts = {k: (sorted(v)[len(v) // 3], sorted(v)[2 * len(v) // 3]) for k, v in by.items() if len(v) >= 9}
top100 = set(RANKS.get(2026, {}))
org = {}
for pid, r in cur.items():
    by_y = mlb_by_year(pid)
    if sum(abs(v) for y, v in by_y.items() if y < 2026) >= 0.6: continue
    if pid in top100 or r["age"] > 27: continue
    c = cuts.get((r["lvl"], r["pit"]))
    if not c: continue
    t = 0 if r["rel"] < c[0] else 1 if r["rel"] < c[1] else 2
    ev6, y1, n = shrunk((r["lvl"], r["pit"], age_band(r), t))
    org[pid] = [r["name"], r["org"], r["pit"], r["age"], r["lvl"], round(ev6, 2), round(y1, 2), r["pos"], r["line"], t]
# keep each club's 25 best by expectation (an org list, not the whole system)
keep = {}
byorg = defaultdict(list)
for pid, v in org.items(): byorg[v[1]].append((v[5], pid))
for ab, xs in byorg.items():
    for k, (_, pid) in enumerate(sorted(xs, reverse=True)[:25]):
        keep[str(pid)] = org[pid] + [k + 1]
cur_top = {}
for pid, rk in RANKS.get(2026, {}).items():
    r = cur.get(pid)
    cur_top[str(pid)] = r["lvl"] if r else ""
json.dump(dict(org=keep, rookie=ROOK, calib=CAL, top100Level=cur_top), open(f"{ROOT}/pros.json", "w"), ensure_ascii=False)
print("org prospects kept:", len(keep), "| clubs:", len(byorg))
