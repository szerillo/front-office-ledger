"""
EXTENSIONS CHANNEL v1: contract extensions graded as their own decision type.

Why a separate channel: an extension is not a free-agent signing. The club
already controls the player's near seasons, and the market it shops is the
extension market for that service class, which trades at a deep and
well-documented discount to open-market $/win. Grading Acuna 8/100 against
FA prices would call every pre-arb extension an A+; grading it against what
pre-arb extensions typically pay isolates the skill (picking WHICH player to
lock up, and at what price) from the structural discount every club enjoys.

Class discounts of open-market $-per-win (documented assumptions, tunable
when the extension book is big enough to fit them empirically):
  pre-debut  0.35   signed before MLB debut (Chourio, Emerson, Pratt, Griffin)
  early      0.45   0-2 calendar years since debut (Acuna, Julio, Witt)
  arb        0.60   3-5 years since debut (Riley, Raleigh, Greene)
  veteran    0.90   6+ years since debut (Machado '23, Altuve '24, Wheeler)
Implied wins for a season = class-discounted AAV / $-per-win(season), using
the CBT/present-value total where deferrals diverge (Betts). Realized = LVM
on the club over elapsed covered seasons (sign year + 1 onward, 2025 cap,
matching the FA convention; 2026 in progress). Net = realized - implied.
Retention framing per methodology v0.2: the option value of locking the
player's prime is what the discount buys; the channel grades the price paid
for it. Wander Franco's seasons cap at 2023 (deal effectively voided).

Regime attribution: sign date inside the regime window, else excluded.
Channel letter needs >= 2 matched deals; below that pending.
"""
import json, os, sqlite3
from collections import defaultdict
from contracts_ext import EXT
from fa_grade_lib import norm, DPW   # shared helpers
from ledger_war import player_seasons

DISC = {"pre-debut": 0.35, "early": 0.45, "arb": 0.60, "veteran": 0.90}

cfg = json.load(open("/home/claude/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
ABBR2TID = {r["abbr"]: r["teamId"] for r in cfg["regimes"]}
LVM = {k: v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}
NAME2PIDS = {}
for pid, rec in LVM.items():
    NAME2PIDS.setdefault(norm(rec.get("name", "")), []).append(pid)
# extension players never touched by a graded transaction are not in the
# sweep cache (homegrown stars: Acuna, Riley, Happ). Resolve ids from the
# full feed name map and value them on demand.
con2 = sqlite3.connect("/home/claude/ledger.sqlite")
FEED2PIDS = {}
for nm, pid in con2.execute("select distinct person_name, person_id from sweep_tx where person_id is not null and person_name is not null"):
    FEED2PIDS.setdefault(norm(nm), []).append(str(pid))
EXTCACHE_P = "/home/claude/ext_lvm_cache.json"
EXTCACHE = {k: v for k, v in (json.load(open(EXTCACHE_P)) if os.path.exists(EXTCACHE_P) else {}).items() if not str(k).startswith("__")}

def resolve(player, tid, sy, yrs):
    """Same-name players exist (two Jose Ramirezes, two Will Smiths):
    among candidates, pick the one who actually produced for the signing
    club around the deal window."""
    pn = norm(player)
    cands = list(dict.fromkeys((NAME2PIDS.get(pn) or []) + (FEED2PIDS.get(pn) or [])))
    if not cands: return None
    if len(cands) == 1: return cands[0]
    names = ALIAS.get(tid, {REG[tid]["team"]})
    def fit(pid):
        rows = lvm_rows(pid)   # fetches + caches unvalued candidates
        return sum(abs(v) for (y, tm, v) in rows
                   if any(al in tm for al in names) and sy - 1 <= y <= sy + yrs)
    return max(cands, key=fit)

def lvm_rows(pid):
    if pid in LVM: return LVM[pid]["rows"]
    if pid in EXTCACHE: return EXTCACHE[pid]["rows"]
    ps = player_seasons([pid]).get(int(pid)) or player_seasons([pid]).get(pid)
    rows = []
    if ps:
        for y, rec in sorted(ps["seasons"].items()):
            rows.append([int(y), rec["team"], rec["bat"] + rec["pit"]])
    EXTCACHE[pid] = dict(name=player_seasons.__name__ and "", rows=rows)
    json.dump(EXTCACHE, open(EXTCACHE_P, "w"))
    return rows
ORGS = json.load(open("/home/claude/prospect_orgs.json"))  # debut dates

def debut_year(pid):
    d = (ORGS.get(pid) or {}).get("debut")
    if d: return int(d[:4])
    rows = lvm_rows(pid)
    if rows: return min(y for (y, tm, v) in rows)
    return None

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

res = json.load(open("/home/claude/sweep_results.json"))
per = defaultdict(lambda: dict(net=0.0, n=0, decs=[]))
skipped = []

for sign, player, ab, yrs, tot, cbt in EXT:
    tid = ABBR2TID[ab]; reg = REG[tid]
    sign_date = sign + "-15"
    if sign_date < reg["start"]:
        skipped.append((player, ab, "predates regime")); continue
    pid = resolve(player, tid, int(sign[:4]), yrs)
    sy = int(sign[:4])
    dy = debut_year(pid) if pid else None
    if pid is None and dy is None:
        cls = "pre-debut"           # never played MLB yet, not in LVM
    elif dy is None or dy > sy:
        cls = "pre-debut"
    elif sy - dy <= 2: cls = "early"
    elif sy - dy <= 5: cls = "arb"
    else: cls = "veteran"
    use_tot = cbt if cbt else tot
    aav = use_tot / yrs
    start = sy if int(sign[5:7]) <= 3 else sy + 1   # spring deals replace the current season (approx)
    end_cap = 2023 if player == "Wander Franco" else 2025
    seasons = [y for y in range(start, min(start + yrs - 1, end_cap) + 1)]
    names = ALIAS.get(tid, {reg["team"]})
    rows = lvm_rows(pid) if pid else []
    realized = sum(v for (y, tm, v) in rows
                   if any(al in tm for al in names) and y in seasons)
    implied = sum(aav / (DISC[cls] * DPW[min(y, 2026)]) for y in seasons)
    n = realized - implied
    if not seasons:                  # freshly signed, nothing elapsed
        per[tid]["decs"].append(dict(d=sign_date, ch="ext", net=0.0,
            h=f"Extended {player} · {yrs} yr / ${tot:.1f}M ({cls}) · no seasons elapsed, OPEN"))
        per[tid]["n"] += 1
        continue
    per[tid]["net"] += n; per[tid]["n"] += 1
    cbtnote = f", CBT ${use_tot:.0f}M" if cbt else ""
    per[tid]["decs"].append(dict(d=sign_date, ch="ext", net=round(n, 1),
        h=f"Extended {player} · {yrs} yr / ${tot:.1f}M ({cls} market{cbtnote})",
        sides=[["Production (LVM on club, covered seasons)", [[player, f"{realized:+.1f}"]]],
               [f"Cost vs {cls} extension market", [[f"${use_tot:.0f}M over {yrs} yr at {int(DISC[cls]*100)}% of market $/win", f"{-implied:+.1f}"]]]],
        pids=[pid] if pid else []))

print(f"{'team':<6}{'EXT net':>9}{'n':>4}   deals")
for r in res:
    tid = r["teamId"]; p = per.get(tid, dict(net=0.0, n=0, decs=[]))
    covered = p["n"] >= 2
    scored = [d for d in p["decs"] if "OPEN" not in d["h"]]
    r["chan"]["ext"] = dict(net=round(p["net"], 1) if covered else 0,
                            g=grade(p["net"] / r["seasons"]) if covered and scored else None,
                            n=p["n"])
    if covered and scored:
        r["total"] = round(r["total"] + p["net"], 1)
        r["forGrade"] = grade_comp(r["total"] / r["seasons"])
    p["decs"].sort(key=lambda d: -abs(d["net"]))
    r["ext_tops"] = p["decs"][:4]
    names = ", ".join(d["h"][9:].split(" ·")[0] for d in p["decs"][:3]) or "-"
    print(f"{r['abbr']:<6}{(p['net'] if covered else 0):>+9.1f}{p['n']:>4}   {names}")

json.dump(res, open("/home/claude/sweep_results.json", "w"), indent=1)
print("\nmerged chan.ext into sweep_results.json")
for s in skipped: print("  skipped (outside regime):", s)
