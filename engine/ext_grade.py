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
HIST = json.load(open("/work/hist_results.json"))
MOVE_POP = []   # v5.5: (cost in wins, net) for every graded extension
skipped = []

# v5.9: an extension is graded against the path it replaced.
#   * In his controlled seasons the value already belongs to the decision
#     that acquired him (draft, trade, international signing: an extension
#     no longer cuts those windows short). The extension changes only what
#     the club PAYS there: credit the estimated arbitration salary it
#     replaced (pre-arbitration seasons at the minimum), charge the
#     extension's salary.
#   * In the free-agent seasons it buys, it is a free-agent deal: production
#     against the cost at market $/win times the typical free-agent return
#     for that year of free agency and deal size.
#   * Then each class (pre-debut, early, arbitration, veteran) is centered:
#     the league's average result per win of cost for that class is the
#     expectation, so a club is judged on WHICH players it locked up and at
#     what price, not on which kind of extension it favors (the v5.7-5.8
#     fixed class discounts left early extensions at 1.39x expectation and
#     veteran ones at 0.84x, so the letter mostly read class mix).
import sys as _sys
_sys.path.insert(0, "/work")
import asset_rules as AR
CB = json.load(open("/work/contract_book.json"))
CB_DPW = {int(k): v for k, v in CB["dpw"].items()}; LMIN = CB.get("league_min", 0.75)
def wins_of(m, y): return max(0.0, m - LMIN) / CB_DPW.get(y, AR.dpw(y))
EVAL = []
for c in CB["book"]:
    if c["kind"] != "ext": continue
    sign, player, ab, yrs, tot = c["sign"], c["name"], c["club"], c["yrs"], c["tot"]
    if ab not in ABBR2TID: continue
    tid = ABBR2TID[ab]
    pid = str(c["pid"]); sy = int(sign[:4])
    dy = debut_year(pid) if pid else None
    if dy is None or dy > sy: cls = "pre-debut"
    elif sy - dy <= 2: cls = "early"
    elif sy - dy <= 5: cls = "arb"
    else: cls = "veteran"
    ce = AR.control_end(int(pid))
    held = [h for h in c.get("held", []) if h[1] <= (2023 if player == "Wander Franco" else 2026)]
    ctrl_save = 0.0; fa_prod = 0.0; fa_exp = 0.0; cost = 0.0; ctrl_n = fa_n = 0; inc = {}; cst = {}
    for k, y, w, sh in held:
        ext_c = wins_of(c["aav"], y) * sh
        if ce is not None and y <= ce:
            arb = AR.arb_salary(int(pid), y) or LMIN
            v_ = (wins_of(arb, y) - ext_c) * AR.money_unit(y)
            ctrl_save += v_; ctrl_n += 1
        else:
            kk = y - ce if ce is not None else k
            e_ = ext_c * AR.typical_fa(kk, y, c.get("band"))
            v_ = w - e_
            fa_prod += w; fa_exp += e_; fa_n += 1
        cost += ext_c; inc[y] = inc.get(y, 0.0) + v_; cst[y] = cst.get(y, 0.0) + ext_c
    raw = ctrl_save + fa_prod - fa_exp
    EVAL.append(dict(sign=sign, player=player, tid=tid, ab=ab, sign_date=sign + "-15", pid=pid, cls=cls, yrs=yrs, tot=tot,
                     seasons=[h[1] for h in held], raw=raw, cost=cost, ctrl_save=ctrl_save, fa_prod=fa_prod, fa_exp=fa_exp,
                     ctrl_n=ctrl_n, fa_n=fa_n, inc=inc, cst=cst))
_acc = defaultdict(lambda: [0.0, 0.0, 0])
for e in EVAL:
    if e["seasons"]: a_ = _acc[e["cls"]]; a_[0] += e["raw"]; a_[1] += e["cost"]; a_[2] += 1
CLASS_RATE = {k: round(a_[0] / a_[1], 3) for k, a_ in _acc.items() if a_[1] > 0}
for e in EVAL:
    e["expected"] = CLASS_RATE.get(e["cls"], 0.0) * e["cost"]
    e["net"] = e["raw"] - e["expected"]
print("typical extension result per win of cost, by class:", CLASS_RATE, {k: a_[2] for k, a_ in _acc.items()})
TYPICAL = CLASS_RATE
json.dump(CLASS_RATE, open("/work/ext_class_rate.json", "w"))

def grade_ext(results, archive=False):
    per = defaultdict(lambda: dict(net=0.0, n=0, decs=[]))
    for r in results:
        tid = r["teamId"]
        st = max(r["startDate"], "1998-01-01")
        en = (r.get("endDate") or "9999-12-31") if archive else "9999-12-31"
        for e in EVAL:
            if e["tid"] != tid or not (st <= e["sign_date"] <= en): continue
            p = per[r["id"]]
            if not e["seasons"]:
                p["decs"].append(dict(d=e["sign_date"], ch="ext", net=0.0,
                    h=f"Extended {e['player']} · {e['yrs']} yr / ${e['tot']:.1f}M ({e['cls']}) · no seasons elapsed, OPEN"))
                p["n"] += 1; continue
            n = e["net"]; p["net"] += n; p["n"] += 1
            rate = CLASS_RATE.get(e["cls"], 0.0)
            for _y, _v in e["inc"].items():
                p.setdefault("inc", {}); p["inc"][_y] = p["inc"].get(_y, 0.0) + _v - rate * e["cst"].get(_y, 0.0)
            MOVE_POP.append([round(e["cost"], 2), round(n, 2)])
            sides = []
            if e["ctrl_n"]: sides.append(["Controlled seasons: arbitration path minus extension salary", [[f"{e['ctrl_n']} season(s)", f"{e['ctrl_save']:+.1f}"]]])
            if e["fa_n"]: sides.append(["Bought-out free-agent seasons: production vs a typical free-agent return on the money",
                                        [[e["player"], f"{e['fa_prod']:+.1f}"], ["typical return on that money", f"{-e['fa_exp']:+.1f}"]]])
            sides.append([f"Typical {e['cls']} extension of this size", [[f"{e['cost']:.1f} wins of cost x the class average", f"{-e['expected']:+.1f}"]]])
            p["decs"].append(dict(d=e["sign_date"], ch="ext", net=round(n, 1), st=round(e["cost"], 2),
                h=f"Extended {e['player']} · {e['yrs']} yr / ${e['tot']:.1f}M ({e['cls']})", sides=sides, pids=[e["pid"]]))
    for r in results:
        p = per.get(r["id"], dict(net=0.0, n=0, decs=[]))
        scored = [d for d in p["decs"] if "OPEN" not in d["h"]]
        covered = len(scored) >= 2
        # v5.9: the net always counts (an extension's free-agent seasons are graded
        # nowhere else); a letter needs two priced deals
        r["chan"]["ext"] = dict(net=round(p["net"], 1), typical=CLASS_RATE,
                                g=grade(p["net"] / r["seasons"]) if covered else None, n=p["n"], scored=len(scored))
        if scored:
            r["total"] = round(r["total"] + p["net"], 1)
            r["forGrade"] = grade_comp(r["total"] / r["seasons"])
            if r.get("cum") and p.get("inc"):
                y0c = r["start"]
                r["cum"] = [round(v + sum(x for yy, x in p["inc"].items() if yy <= y0c + i), 1) for i, v in enumerate(r["cum"])]
        p["decs"].sort(key=lambda d: -abs(d["net"]))
        r["ext_tops"] = p["decs"][:4]
        r["allx_ext"] = [[d["d"], d["h"], d["net"], d.get("st")] for d in sorted(p["decs"], key=lambda d: d["d"])]
        if not archive:
            names = ", ".join(d["h"][9:].split(" ·")[0] for d in p["decs"][:3]) or "-"
            print(f"{r['abbr']:<6}{(p['net'] if covered else 0):>+9.1f}{p['n']:>4}   {names}")
grade_ext(res)
grade_ext(HIST, archive=True)     # v5.9: archive regimes are graded on extensions too
json.dump(res, open("/work/sweep_results.json", "w"), indent=1)
json.dump(HIST, open("/work/hist_results.json", "w"), indent=1)
json.dump({"ext": MOVE_POP}, open("/work/move_pop_ext.json", "w"))
print("\nmerged chan.ext into sweep_results.json and hist_results.json")
