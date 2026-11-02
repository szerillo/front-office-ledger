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

cfg = json.load(open("/work/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
ABBR2TID = {r["abbr"]: r["teamId"] for r in cfg["regimes"]}
LVM = {k: v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
NAME2PIDS = {}
for pid, rec in LVM.items():
    NAME2PIDS.setdefault(norm(rec.get("name", "")), []).append(pid)
# extension players never touched by a graded transaction are not in the
# sweep cache (homegrown stars: Acuna, Riley, Happ). Resolve ids from the
# full feed name map and value them on demand.
con2 = sqlite3.connect("/work/ledger.sqlite")
FEED2PIDS = {}
for nm, pid in con2.execute("select distinct person_name, person_id from sweep_tx where person_id is not null and person_name is not null"):
    FEED2PIDS.setdefault(norm(nm), []).append(str(pid))
EXTCACHE_P = "/work/ext_lvm_cache.json"
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
ORGS = json.load(open("/work/prospect_orgs.json"))  # debut dates

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

res = json.load(open("/work/sweep_results.json"))
per = defaultdict(lambda: dict(net=0.0, n=0, decs=[]))
MOVE_POP = []   # v5.5: (cost in wins, net) for every graded extension
skipped = []

# v5.7: graded against expectation AND investment. Pass 1 prices every
# extension in the book (all clubs, all regimes) and measures what a typical
# club got back per win of class-market cost; pass 2 grades each regime's
# deals against that typical return, so the expectation scales with the money.
EVAL = []
CB = json.load(open("/work/contract_book.json"))
CB_DPW = {int(k): v for k, v in CB["dpw"].items()}; LMIN = CB.get("league_min", 0.75)
for c in CB["book"]:
    if c["kind"] != "ext": continue
    sign, player, ab, yrs, tot = c["sign"], c["name"], c["club"], c["yrs"], c["tot"]
    if ab not in ABBR2TID: continue
    tid = ABBR2TID[ab]; reg = REG[tid]
    sign_date = sign + "-15"
    pid = str(c["pid"])
    sy = int(sign[:4])
    dy = debut_year(pid) if pid else None
    if dy is None or dy > sy: cls = "pre-debut"
    elif sy - dy <= 2: cls = "early"
    elif sy - dy <= 5: cls = "arb"
    else: cls = "veteran"
    # v5.8: the seasons this deal owns (a later contract owns its own), held
    # by the club until it trades him (the trade carries the rest, salary
    # included); a release keeps the dead money. Wander Franco's deal stops
    # at 2023 (restricted list, unpaid).
    held = [h for h in c.get("held", []) if h[1] <= (2023 if player == "Wander Franco" else 2026)]
    seasons = [h[1] for h in held]
    realized = sum(h[2] for h in held)
    costs = [(h[0], max(0.0, c["aav"] - LMIN) / (DISC[cls] * CB_DPW.get(h[1], 9.7)) * h[3]) for h in held]
    implied = sum(x for _, x in costs)
    EVAL.append(dict(sign=sign, player=player, tid=tid, reg=reg, sign_date=sign_date, pid=pid, cls=cls,
                     yrs=yrs, tot=tot, cbt=None, use_tot=tot, seasons=seasons, realized=realized, implied=implied,
                     held=held, costs=costs))
# typical return by contract year, pooled over every priced extension
_acc = defaultdict(lambda: [0.0, 0.0])
for e in EVAL:
    for (k, cst), h in zip(e["costs"], e["held"]):
        a_ = _acc[min(k, 5)]; a_[0] += h[2]; a_[1] += cst
TYP_EXT = {k: round(a_[0] / a_[1], 3) for k, a_ in sorted(_acc.items()) if a_[1] > 0}
TYPICAL = round(sum(a_[0] for a_ in _acc.values()) / max(sum(a_[1] for a_ in _acc.values()), 1e-9), 3)
for e in EVAL:
    e["expected"] = sum(cst * TYP_EXT.get(min(k, 5), TYPICAL) for k, cst in e["costs"])
print(f"typical extension return by contract year {TYP_EXT} (pooled {TYPICAL}) over {len(EVAL)} book extensions")

for e in EVAL:
    sign, player, tid, reg, sign_date, pid, cls = e["sign"], e["player"], e["tid"], e["reg"], e["sign_date"], e["pid"], e["cls"]
    yrs, tot, cbt, use_tot, seasons, realized, implied = e["yrs"], e["tot"], e["cbt"], e["use_tot"], e["seasons"], e["realized"], e["implied"]
    if sign_date < reg["start"]:
        skipped.append((player, reg.get("abbr"), "predates regime")); continue
    expected = e["expected"]
    n = realized - expected
    if not seasons:                  # freshly signed, nothing elapsed
        per[tid]["decs"].append(dict(d=sign_date, ch="ext", net=0.0,
            h=f"Extended {player} · {yrs} yr / ${tot:.1f}M ({cls}) · no seasons elapsed, OPEN"))
        per[tid]["n"] += 1
        continue
    per[tid]["net"] += n; per[tid]["n"] += 1
    cbtnote = f", CBT ${use_tot:.0f}M" if cbt else ""
    MOVE_POP.append([round(implied, 2), round(n, 2)])
    per[tid]["decs"].append(dict(d=sign_date, ch="ext", net=round(n, 1), st=round(implied, 2),
        h=f"Extended {player} · {yrs} yr / ${tot:.1f}M ({cls} market{cbtnote})",
        sides=[["Production (Ledger WAR on club, covered seasons)", [[player, f"{realized:+.1f}"]]],
               [f"What a typical club gets for this money", [[f"${use_tot:.0f}M over {yrs} yr at {int(DISC[cls]*100)}% of market $/win: {implied:.1f} wins of class-market cost x the typical return for those contract years", f"{-expected:+.1f}"]]]],
        pids=[pid] if pid else []))

print(f"{'team':<6}{'EXT net':>9}{'n':>4}   deals")
for r in res:
    tid = r["teamId"]; p = per.get(tid, dict(net=0.0, n=0, decs=[]))
    scored = [d for d in p["decs"] if "OPEN" not in d["h"]]
    covered = len(scored) >= 2        # v5.8: two PRICED deals with seasons played, not two signatures
    r["chan"]["ext"] = dict(net=round(p["net"], 1) if covered else 0, typical=round(TYPICAL, 3),
                            g=grade(p["net"] / r["seasons"]) if covered and scored else None,
                            n=p["n"])
    if covered and scored:
        r["total"] = round(r["total"] + p["net"], 1)
        r["forGrade"] = grade_comp(r["total"] / r["seasons"])
    p["decs"].sort(key=lambda d: -abs(d["net"]))
    r["ext_tops"] = p["decs"][:4]
    r["allx_ext"] = [[d["d"], d["h"], d["net"], d.get("st")] for d in sorted(p["decs"], key=lambda d: d["d"])]
    names = ", ".join(d["h"][9:].split(" ·")[0] for d in p["decs"][:3]) or "-"
    print(f"{r['abbr']:<6}{(p['net'] if covered else 0):>+9.1f}{p['n']:>4}   {names}")

json.dump(res, open("/work/sweep_results.json", "w"), indent=1)
json.dump({"ext": MOVE_POP}, open("/work/move_pop_ext.json", "w"))
print("\nmerged chan.ext into sweep_results.json")
for s in skipped: print("  skipped (outside regime):", s)
