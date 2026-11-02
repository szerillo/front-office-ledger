"""Asset accounting for player acquisition channels (v5.5).

A drafted (or internationally signed) player is an ASSET the club created.
His value is what he produced in his first six MLB seasons, the control
years, wherever he played them. If the club later trades him, the trade
channel charges what he produced for his new club and credits what came
back. The two entries net to "what the club turned the pick into", which is
the only consistent reading:

  * the old reading credited the draft only while the player stayed, so a
    traded draftee read as a draft miss AND a trade loss (CJ Abrams and
    MacKenzie Gore were charged twice to San Diego);
  * it also credited the draft with a homegrown star's extension years,
    which the extension channel already grades net of their cost.

Slot expectation is re-calibrated on this definition: across every round
1-5 pick 1998-2016 (ten or more years matured), first-six-season value ran
1.309x the published slot curve, and DRAFT_SHAPE is the share of that value
realized N years after the draft (pooled 1998-2024 classes). With both, the
league's draft net is about zero by construction (pooled ratio 0.985).
"""
# v5.8: re-calibrated with the ownership rule (control years stop where an
# extension or a later contract owns the seasons): across 3,211 round 1-5
# picks 1998-2016, capped control value ran 1.058x the slot curve (1.305x
# uncapped, the v5.5 figure); DRAFT_SHAPE is the share of capped value
# realized by N seasons after the draft season, same pool.
DRAFT_K = 1.058
DRAFT_SHAPE = {0: 0.0, 1: 0.01, 2: 0.05, 3: 0.14, 4: 0.27, 5: 0.45, 6: 0.63, 7: 0.79, 8: 0.91, 9: 0.96, 10: 0.99}

def draft_maturity(draft_year, asof=2026):
    return DRAFT_K * DRAFT_SHAPE.get(max(0, asof - int(draft_year)), 1.0)

def control_years(rec):
    """the six seasons starting with his MLB debut season"""
    if not rec or not rec.get("rows"): return set()
    y0 = min(y for y, _, _ in rec["rows"])
    return set(range(y0, y0 + 6))

def control_value(rec, teams=None, pid=None, after=None, series=False):
    """value in the control years; anywhere (teams=None) or on `teams`.
    v5.8: stops before the first season owned by a contract signed after
    `after` (an extension or a free-agent deal owns its seasons)."""
    if not rec: return ({} if series else 0.0)
    cy = control_years(rec)
    cap = control_cap(pid, after) if (pid and after) else 9999
    out = _dd(float)
    for y, tm, v in rec["rows"]:
        if y in cy and y <= cap and (teams is None or tm in teams): out[y] += v
    return dict(out) if series else sum(out.values())

# ---- v5.7: trades are graded net of the salary that moves with the player ----
# A player arrives with his contract. Before, trades counted only wins, so a
# salary dump read as a pure giveaway (the Cardinals sending Arenado's
# contract to Arizona) and a club that paid a player in the free-agent or
# extension channel was charged his salary there AND his full value again
# when it traded him. The acquiring club now pays the guaranteed salary it
# takes on, above the league minimum, converted to wins at that season's
# $/win; the selling club is relieved of it. Arbitration salaries and cash
# sent in the deal are not in the book and are not charged (disclosed),
# except where a public report gives the cash by season: NET_PAID holds what
# the acquiring club actually paid in those seasons.
NET_PAID = {
    # Nolan Arenado, STL to ARI 2026-01-13: owed $27M (2026) and $15M (2027);
    # STL sends $22M toward 2026 and $9M on Nov 1 2027 (AP, Jan 13 2026)
    571448: {2026: 5.0, 2027: 6.0},
    # David Price, BOS to LAD 2020-02-10: $32M a year; Boston sent $48M,
    # $16M toward each of 2020-22 (Boston Globe, Feb 2020); he opted out of 2020
    456034: {2020: 0.0, 2021: 16.0, 2022: 16.0},
}
import json as _json, os as _os, sqlite3 as _sq
from collections import defaultdict as _dd

# ---- v5.8: one contract book, one ownership rule, one money unit ----
# contract_book.py (chain step 0) resolves every known guaranteed contract
# to a player and marks the seasons it OWNS: a later contract (extension,
# re-signing, deal elsewhere) owns its seasons, and no earlier decision's
# value window runs into them. Money is charged in one unit everywhere:
# salary above the league minimum, at that season's $/win, times what a
# typical club gets back for free-agent money (the opportunity cost of a
# payroll dollar). Taking on a typical contract is therefore neutral.
_BOOK = None
def _book():
    global _BOOK
    if _BOOK is not None: return _BOOK
    p = "/work/contract_book.json"
    _BOOK = _json.load(open(p)) if _os.path.exists(p) else dict(book=[], dpw={}, typical_fa_all=1.0, era_adj_pre2006=1.0, league_min=0.75)
    own = {}; signs = _dd(list)
    for c in _BOOK["book"]:
        for y in c.get("own", []):
            own.setdefault(int(c["pid"]), {})[y] = c
        signs[int(c["pid"])].append(c)
    _BOOK["_own"] = own; _BOOK["_signs"] = signs
    _BOOK["_dpw"] = {int(k): v for k, v in _BOOK["dpw"].items()}
    return _BOOK
def dpw(y):
    d = _book()["_dpw"]
    return d.get(y) or d.get(min(max(y, min(d)), max(d)), 9.7) if d else 9.7
def money_unit(y):
    """wins a typical club gets back per win of market cost, season y"""
    B = _book()
    return B.get("typical_fa_all", 1.0) * (B.get("era_adj_pre2006", 1.0) if y < 2006 else 1.0)
_COST = None
def _cost_table():
    global _COST
    if _COST is not None: return _COST
    _COST = {}
    B = _book(); mn = B.get("league_min", 0.75)
    for pid, ys in B["_own"].items():
        for y, c in ys.items():
            _COST.setdefault(pid, {})[y] = max(0.0, c["aav"] - mn) / dpw(y) * money_unit(y)
    for pid, ys in NET_PAID.items():
        for y, m in ys.items():
            _COST.setdefault(int(pid), {})[y] = max(0.0, m - mn) / dpw(y) * money_unit(y)
    return _COST

def contract_cost(pid, yr):
    """guaranteed salary above the minimum for that season, in wins, at the
    typical return on payroll money"""
    try: return _cost_table().get(int(pid), {}).get(int(yr), 0.0)
    except Exception: return 0.0

def new_contract_season(pid, after):
    """first season owned by a contract signed after `after` (YYYY-MM[-DD]),
    or None: from that season on, the new decision owns the value"""
    try: cs = _book()["_signs"].get(int(pid), [])
    except Exception: return None
    a = str(after)[:7]
    ss = [min(c["own"]) for c in cs if c["sign"] > a and c.get("own")]
    return min(ss) if ss else None

_EVENTS = None
def _events():
    """free-agent filings and releases, per player (sweep_tx)"""
    global _EVENTS
    if _EVENTS is not None: return _EVENTS
    _EVENTS = _dd(list)
    con = _sq.connect("/work/ledger.sqlite")
    for pid, d, ty, ft in con.execute("select person_id, date, type_desc, from_team from sweep_tx where person_id is not null "
                                      "and type_desc in ('Declared Free Agency','Released')"):
        _EVENTS[int(pid)].append((d, ty, ft))
    return _EVENTS

_LVM = None
def _lvm():
    global _LVM
    if _LVM is None:
        _LVM = {int(k): v for k, v in _json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
    return _LVM

def trade_window(pid, teams, date, lev=None, cap=6, weight=True, sender=None):
    """v5.8 asset accounting for a traded player: what the acquiring club
    received is the player's control window from the trade, WHEREVER he
    plays it (a quick flip is graded in the flip, not lost), net of the
    salary that travels with him, until the first of: a new contract signed
    after the trade (that decision owns its seasons), his free-agent filing,
    or his release, capped at six seasons. Trade season: his production on
    the acquiring club only. Each season weighted by the acquiring club's
    leverage and 0.9^years. Returns (total, {season: value})."""
    rec = _lvm().get(int(pid)) if pid else None
    if not rec: return 0.0, {}
    y0 = int(str(date)[:4])
    end = y0 + cap - 1
    nc = new_contract_season(pid, date)
    if nc is not None: end = min(end, nc - 1)
    for d, ty, ft in _events().get(int(pid), []):
        if d <= str(date): continue
        yy = int(d[:4])
        if ty == "Declared Free Agency": end = min(end, yy if int(d[5:7]) >= 9 else yy - 1)
        elif ty == "Released" and ft in teams: end = min(end, yy); break
    byyear = _dd(list)
    for yr, tm, v in rec["rows"]:
        byyear[yr].append((tm, v))
    series = {}
    for yr in range(y0, end + 1):
        rows = byyear.get(yr, [])
        if not rows: continue
        if yr == y0:
            # the trade season: what he produced after leaving the sending club
            # (with the acquirer, and with anyone the acquirer flipped him to)
            if sender:
                last = max([i for i, (tm, v) in enumerate(rows) if tm in sender], default=None)
                if last is not None: use = [v for tm, v in rows[last + 1:]]
                elif int(str(date)[5:7] or 7) >= 10: use = []            # an offseason deal: that season was already played
                else: use = [v for tm, v in rows if tm in teams]
            else:
                use = [v for tm, v in rows if tm in teams]
            share = len([1 for tm, v in rows if tm in teams]) / len(rows)
        else:
            use = [v for tm, v in rows]; share = 1.0
        if not use: continue
        disc = (0.9 ** (yr - y0)) if weight else 1.0
        # leverage of the club the wins were produced for (a flipped player's
        # wins for a contender count as a contender's wins)
        if lev and weight:
            here_tm = [tm for tm, v in rows if tm in teams]
            tm_now = here_tm[-1] if here_tm else rows[-1][0]
            lv = lev({tm_now}, yr) if yr > y0 else lev(teams, yr)
        else:
            lv = 1.0
        val = sum(use) * lv * disc - contract_cost(pid, yr) * share * disc
        series[yr] = val
    return sum(series.values()), series

def control_cap(pid, after):
    """last season a draft or international asset's control window can
    reach before a later contract owns the seasons"""
    nc = new_contract_season(pid, after) if pid else None
    return (nc - 1) if nc is not None else 9999

