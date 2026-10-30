"""THE SHOPPING FINGERPRINT: what each front office actually buys, in skills.

For every active regime, take every player it ACQUIRED (trades in, major
league FA signings) since 2016 and look up the player's Statcast profile in
the season BEFORE the acquisition (the season the front office evaluated).
Z-score each skill within its season, average across the regime's
acquisitions, and the persistent deviations are the fingerprint: this desk
pays for velocity, that one buys chase-resistant bats.

Data: Baseball Savant custom leaderboards (public, MLB-operated), 2015-2026.
Writes fingerprints.json and merges dna.shop into sweep_results.json
(idempotent: overwrites its own key only).
"""
import json, sqlite3, time, urllib.request, io, csv
from collections import defaultdict
from statistics import mean, pstdev

YEARS = range(2015, 2027)
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

def fetch_season(year, side):
    sel = BAT_SEL if side == "bat" else PIT_SEL
    mn = 100 if side == "bat" else 50
    u = (f"https://baseballsavant.mlb.com/leaderboard/custom?year={year}&type={'batter' if side=='bat' else 'pitcher'}"
         f"&filter=&min={mn}&selections={sel}&chart=false&x=pa&y=pa&r=no&chartType=beeswarm&sort=k_percent&sortDir=desc&csv=true")
    t = get(u)
    if not t or "player_id" not in t.splitlines()[0]:
        return {}
    rows = {}
    for r in csv.DictReader(io.StringIO(t.lstrip("﻿"))):
        pid = r.get("player_id")
        if not pid: continue
        clean = {}
        for k, v in r.items():
            if k in ("last_name, first_name", "player_id", "year"): continue
            try: clean[k] = float(str(v).strip('"'))
            except (ValueError, TypeError): pass
        rows[int(pid)] = clean
    return rows

print("fetching Savant custom leaderboards 2015-2026...", flush=True)
M = {}  # (year, side) -> {pid: {metric: value}}
for y in YEARS:
    for side in ("bat", "pit"):
        M[(y, side)] = fetch_season(y, side)
        print(y, side, len(M[(y, side)]), flush=True)
        time.sleep(0.6)

# z-scores within season/side
Z = {}
for key, players in M.items():
    mets = defaultdict(list)
    for p in players.values():
        for k, v in p.items(): mets[k].append(v)
    stats = {k: (mean(v), pstdev(v)) for k, v in mets.items() if len(v) > 50 and pstdev(v) > 1e-9}
    Z[key] = {pid: {k: (v - stats[k][0]) / stats[k][1] for k, v in p.items() if k in stats}
              for pid, p in players.items()}

cfg = json.load(open("/work/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
con = sqlite3.connect("/work/ledger.sqlite"); con.row_factory = sqlite3.Row
POS = json.load(open("/work/positions.json"))
POS.update(json.load(open("/work/positions2.json")))
PITPOS = {"RHP", "LHP", "SP", "RP", "P"}

acq = defaultdict(lambda: {"bat": [], "pit": []})   # tid -> side -> [zvec]
counts = defaultdict(lambda: {"bat": 0, "pit": 0})
for reg in cfg["regimes"]:
    tid = reg["teamId"]; names = ALIAS.get(tid, {reg["team"]})
    start = max(reg["start"], "2016-01-01")
    seen = set()
    for r in con.execute("""select date, person_id, type_desc, description, to_team from sweep_tx
                            where team_id=? and date>=? and person_id is not null
                            and type_desc in ('Trade','Signed as Free Agent')""", (tid, start)):
        if r["to_team"] not in names: continue
        if r["type_desc"] == "Signed as Free Agent" and "minor league" in (r["description"] or "").lower(): continue
        pid = r["person_id"]; yr = int(r["date"][:4])
        k = (pid, yr)
        if k in seen: continue
        seen.add(k)
        side = "pit" if POS.get(str(pid)) in PITPOS else "bat"
        z = Z.get((yr - 1, side), {}).get(int(pid))
        if z:
            acq[tid][side].append(z)
            counts[tid][side] += 1

# fingerprint labels: metric -> (positive-z phrase, negative-z phrase); sign
# conventions chosen so the phrase describes what the desk PAYS FOR
BAT_LABELS = [
    ("impact", "hard contact", "contact over impact"),
    ("oz_swing_percent", "free swingers", "strike-zone discipline"),
    ("whiff_percent", "power over bat-to-ball", "bat-to-ball skills"),
    ("sprint_speed", "speed and athleticism", "station-to-station bats"),
    ("bb_percent", "walks", None),
]
PIT_LABELS = [
    ("fastball_avg_speed", "velocity", "pitchability over velo"),
    ("whiff_percent", "bat-missers", "contact managers"),
    ("groundballs_percent", "ground-ball arms", "fly-ball arms"),
    ("bb_percent", None, "strike-throwers"),
    ("oz_swing_percent", "chase-inducers", None),
]

def fingerprint(zvecs, labels):
    if len(zvecs) < 8: return None
    agg = defaultdict(list)
    for z in zvecs:
        for k, v in z.items(): agg[k].append(v)
        if "barrel_batted_rate" in z and "hard_hit_percent" in z:
            agg["impact"].append((z["barrel_batted_rate"] + z["hard_hit_percent"]) / 2)
    zz = {k: mean(v) for k, v in agg.items() if len(v) >= 8}
    cands = []
    for key, hi, lo in labels:
        if key not in zz: continue
        v = zz[key]
        if v >= 0.22 and hi: cands.append((abs(v), hi, key, round(v, 2)))
        elif v <= -0.22 and lo: cands.append((abs(v), lo, key, round(v, 2)))
    cands.sort(reverse=True)
    return dict(n=len(zvecs), tags=[c[1] for c in cands[:2]],
                z={c[2]: c[3] for c in cands[:4]},
                all={k: round(v, 2) for k, v in sorted(zz.items())})

res = json.load(open("/work/sweep_results.json"))
print(f"\n{'team':<6}{'bats n':>7}  bats buy{'':<26}{'arms n':>7}  arms buy")
for r in res:
    tid = r["teamId"]
    fb = fingerprint(acq[tid]["bat"], BAT_LABELS)
    fp = fingerprint(acq[tid]["pit"], PIT_LABELS)
    r.setdefault("dna", {})["shop"] = dict(bats=fb, arms=fp)
    bt = ", ".join(fb["tags"]) if fb and fb["tags"] else ("league-typical" if fb else "thin sample")
    at = ", ".join(fp["tags"]) if fp and fp["tags"] else ("league-typical" if fp else "thin sample")
    print(f"{r['abbr']:<6}{(fb or {}).get('n',0):>7}  {bt:<34}{(fp or {}).get('n',0):>7}  {at}")

json.dump(res, open("/work/sweep_results.json", "w"), indent=1)
json.dump({r["abbr"]: r["dna"]["shop"] for r in res}, open("/work/fingerprints.json", "w"), indent=1)
print("\nmerged dna.shop into sweep_results.json; wrote fingerprints.json")
