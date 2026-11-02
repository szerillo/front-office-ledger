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

# v5.9: control now runs debut through the end of club control (control_span)
# and an extension no longer cuts it short, so the curve is re-fit
# (draft_calib.py, chain step): DRAFT_SHAPE pooled over the matured 1998-2013
# classes, and the scale K fit PER CLASS (shrunk toward the pool), so every
# pick is judged against what the league got from that slot in that draft.
import json as _jdc, os as _odc
if _odc.path.exists("/work/draft_calib.json"):
    _DC = _jdc.load(open("/work/draft_calib.json"))
    DRAFT_K = _DC["k_pooled"]
    DRAFT_SHAPE = {int(k): v for k, v in _DC["shape"].items()}
    DRAFT_K_CLASS = {int(k): v for k, v in _DC["k_class"].items()}
else:
    DRAFT_K_CLASS = {}
def draft_k(draft_year):
    return DRAFT_K_CLASS.get(int(draft_year), DRAFT_K)
def draft_maturity(draft_year, asof=2026):
    return draft_k(draft_year) * DRAFT_SHAPE.get(max(0, asof - int(draft_year)), 1.0)

_DEBUT = None
def _debuts():
    global _DEBUT
    if _DEBUT is None:
        import json as _j, os as _o
        p = "/work/debuts.json"
        _DEBUT = {int(k): v for k, v in _j.load(open(p)).items() if v} if _o.path.exists(p) else {}
    return _DEBUT
def control_span(rec, pid=None):
    """v5.9: (first, last) season of his original club control. Six years of
    service: a player who debuts after mid-April does not bank a full year
    that season, so his control runs through the sixth season AFTER his
    debut season; an opening-week debut ends it a season sooner (MLB Stats
    API debut dates; options and Super Two are not modeled)"""
    if not rec or not rec.get("rows"): return None
    y0 = min(r[0] for r in rec["rows"])
    d = _debuts().get(int(pid)) if pid else None
    if d and int(d[:4]) == y0 and d[5:] <= "04-15": return (y0, y0 + 5)
    if d and int(d[:4]) < y0: y0 = int(d[:4])
    return (y0, y0 + 6) if d else (y0, y0 + 5)
def control_years(rec, pid=None):
    """the seasons of his original club control (control_span)"""
    sp = control_span(rec, pid)
    return set(range(sp[0], sp[1] + 1)) if sp else set()

def control_value(rec, teams=None, pid=None, after=None, series=False):
    """value in the control years; anywhere (teams=None) or on `teams`.
    v5.8: stops before the first season owned by a contract signed after
    `after` (a free-agent deal owns its seasons).
    v5.9: an EXTENSION owns only the seasons beyond his original control
    (control_end); the controlled seasons stay with the decision that
    acquired him, and the extension channel grades their salary against the
    arbitration path. The asset also ends when he is released or files for
    free agency (a non-tender, a minor-league free agency): what he does
    after that was another club's decision."""
    if not rec: return ({} if series else 0.0)
    cy = control_years(rec, pid)
    cap = control_cap(pid, after) if (pid and after) else 9999
    if pid and after: cap = min(cap, asset_end(pid, after))
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
    """wins a typical club gets back per win of market cost, season y
    (pooled over contract years and sizes): the opportunity cost of a
    payroll dollar that is not a free-agent contract (arbitration salaries,
    the controlled seasons of an extension)"""
    B = _book()
    return B.get("typical_fa_all", 1.0) * (B.get("era_adj_pre2006", 1.0) if y < 2006 else 1.0)
def typical_fa(k, y, band=None):
    """v5.9: typical return on free-agent money in contract year k of a deal
    of size band `band`, season y (contract_book.py)"""
    B = _book()
    r = B.get("typical_fa", {}).get(str(min(max(int(k), 1), 5)), B.get("typical_fa_all", 1.0))
    if band is not None: r *= B.get("band_mult", {}).get(str(band), 1.0)
    return r * (B.get("era_adj_pre2006", 1.0) if y < 2006 else 1.0)

def control_end(pid):
    """v5.9: last season of his original club control (six seasons from his
    MLB debut season, the same definition the draft uses)"""
    rec = _lvm().get(int(pid)) if pid else None
    sp = control_span(rec, pid)
    return sp[1] if sp else None

def season_war(pid):
    rec = _lvm().get(int(pid)) if pid else None
    out = _dd(float)
    for y, tm, v in (rec or {}).get("rows", []): out[y] += v
    return out

def arb_salary(pid, y):
    """v5.9: estimated arbitration salary ($M) for an arbitration season
    (the last three control seasons), the page's calibrated award model:
    (0.6 + basis) x class step (1.0 / 1.5 / 3.1) x $/win drift, basis = the
    better of the prior season and the two-season average"""
    ce = control_end(pid)
    if ce is None or not (ce - 2 <= y <= ce): return None
    w = season_war(pid)
    basis = max(w.get(y - 1, 0.0), 0.5 * (w.get(y - 1, 0.0) + w.get(y - 2, 0.0)), 0.0)
    step = {1: 1.0, 2: 1.5, 3: 3.1}[y - ce + 3]
    return max(0.75, (0.6 + basis) * step * dpw(y) / 9.7)

_EXTSAL = {}
def ext_salary(c, y):
    """v5.9 (Nov 2): an extension's salary by season. Extensions are paid on a
    rising schedule (a few million in the pre-arbitration years, arbitration-
    like money next, the bulk in the free-agent years they buy), so charging
    the average salary every season front-loaded the cost and graded every
    young-player extension as a loss in its early years. The guaranteed total
    is spread over the contract's seasons in proportion to what each season
    would have cost on the path it replaced: the minimum in pre-arbitration
    seasons (doubled: these deals pay a premium for the security), the award
    model's arbitration salary (on his level when he signed, at least that
    of a 3-win regular, the kind of player clubs extend), and the average
    salary in free-agent seasons (never below his last arbitration season). Fixed at signing: later play never moves
    it. Corbin Carroll's 8/$111M comes out about $3M a season through 2026
    and $28M in 2029-30, close to the deal's actual schedule."""
    key = (c["pid"], c["start"], c["yrs"], c["sign"])
    sch = _EXTSAL.get(key)
    if sch is None:
        yrs = list(range(c["start"], c["start"] + c["yrs"]))
        ce = control_end(c["pid"])
        if ce is None:
            sch = {yy: c["aav"] for yy in yrs}
        else:
            w = season_war(c["pid"]); sy = int(str(c["sign"])[:4])
            basis = max(3.0, w.get(sy - 1, 0.0), 0.5 * (w.get(sy - 1, 0.0) + w.get(sy - 2, 0.0)))
            wt = {}
            for yy in yrs:
                if yy > ce: wt[yy] = None
                elif yy >= ce - 2: wt[yy] = max(0.75, (0.6 + basis) * {1: 1.0, 2: 1.5, 3: 3.1}[yy - ce + 3] * dpw(yy) / 9.7)
                else: wt[yy] = 1.5
            top = max([v for v in wt.values() if v is not None] + [c["aav"]])
            wt = {yy: (top if v is None else v) for yy, v in wt.items()}
            s = sum(wt.values())
            sc = c["tot"] / s if s > 0 else 1.0
            sch = {yy: v * sc for yy, v in wt.items()}
        _EXTSAL[key] = sch
    return sch.get(y, c["aav"])

def contract_unit(c, y):
    """money unit for a season of contract c: a free-agent contract (and an
    extension's bought-out free-agent seasons) at the typical return for that
    contract year and deal size, so taking on or shedding a typical contract
    is neutral in expectation; other salary at the pooled unit"""
    if c["kind"] == "fa":
        return typical_fa(y - c["start"] + 1, y, c.get("band"))
    ce = control_end(c["pid"])
    if ce is not None and y > ce:
        return typical_fa(y - ce, y, c.get("band"))
    return money_unit(y)

_COST = None
def _cost_table():
    global _COST
    if _COST is not None: return _COST
    _COST = {}
    B = _book(); mn = B.get("league_min", 0.75)
    for pid, ys in B["_own"].items():
        for y, c in ys.items():
            m = ext_salary(c, y) if c["kind"] == "ext" else c["aav"]
            _COST.setdefault(pid, {})[y] = max(0.0, m - mn) / dpw(y) * contract_unit(c, y)
    for pid, ys in NET_PAID.items():
        for y, m in ys.items():
            _COST.setdefault(int(pid), {})[y] = max(0.0, m - mn) / dpw(y) * money_unit(y)
    return _COST

_AB2N = None
def _ab_names():
    global _AB2N
    if _AB2N is None:
        cfg = _json.load(open("/work/regimes.json"))
        _AB2N = {r["abbr"]: set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in cfg["regimes"]}
    return _AB2N
def _signed_after(c, after, acq=None):
    """a contract counts as signed after the decision if signed in a later
    month, or in the same month by the acquiring club (Olson: traded Mar 14,
    extended by Atlanta Mar 15 2022)"""
    a = str(after)[:7]
    if c["sign"] > a: return True
    return bool(acq) and c["sign"] == a and bool(_ab_names().get(c["club"], set()) & set(acq))

def contract_cost(pid, yr, after=None, acq=None, played=True):
    """salary above the minimum for that season, in wins at the typical return
    on that money. v5.9: in his controlled seasons an extension signed after
    the decision is charged at the arbitration path it replaced (the
    extension channel grades the difference); an arbitration season with no
    contract is charged the estimated award (before, arbitration salaries
    were free in trades)"""
    try:
        pid = int(pid); yr = int(yr)
        if pid in NET_PAID and yr in NET_PAID[pid]: return _cost_table()[pid][yr]
        c = _book()["_own"].get(pid, {}).get(yr)
        ce = control_end(pid)
        if c is not None:
            if c["kind"] == "ext" and after and ce is not None and yr <= ce and _signed_after(c, after, acq):
                a = arb_salary(pid, yr)
                return (max(0.0, a - 0.75) / dpw(yr) * money_unit(yr)) if (a and played) else 0.0
            return _cost_table().get(pid, {}).get(yr, 0.0)
        if played and ce is not None:
            a = arb_salary(pid, yr)
            if a: return max(0.0, a - 0.75) / dpw(yr) * money_unit(yr)
        return 0.0
    except Exception:
        return 0.0

def new_contract_season(pid, after, acq=None):
    """first season owned by a contract signed after `after` (YYYY-MM[-DD]),
    or None: from that season on, the new decision owns the value.
    v5.9: an extension owns only the seasons beyond his original control."""
    try: cs = _book()["_signs"].get(int(pid), [])
    except Exception: return None
    ce = control_end(pid)
    ss = []
    for c in cs:
        if not c.get("own") or not _signed_after(c, after, acq): continue
        own = c["own"]
        if c["kind"] == "ext" and ce is not None: own = [y for y in own if y > ce]
        if own: ss.append(min(own))
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

USE_LEVERAGE = False   # v5.9: grades are unweighted (see trade_window)

def asset_end(pid, after):
    """last season an asset's value can run after `after`: a release (by any
    club) ends it that season, a free-agent filing ends it with that season
    (a filing before September closes the prior one)"""
    end = 9999
    for d, ty, ft in _events().get(int(pid), []):
        if d <= str(after): continue
        yy = int(d[:4])
        if ty == "Declared Free Agency": end = min(end, yy if int(d[5:7]) >= 9 else yy - 1)
        elif ty == "Released": end = min(end, yy)
    return end

# ---- v5.9: an open trade carries the expected value of the prospects in it ----
# A prospect who has not reached the majors produces nothing for years, while
# the veteran sent for him produces at once, so a deal graded on realized
# value only reads every recent seller as a loser and every recent buyer as a
# winner. A prospect received now carries his expected control value (the
# prospect-rank curve at the time of the deal, or the unranked average)
# times the share not yet realized, which fades to zero as his real seasons
# replace it. Calibrated on prospects traded 2011-2018 (trade_calib.py):
# K_TR scales the rank curve to realized discounted window value, M_TR is the
# share realized N seasons after the deal.
_TC = None
def _trade_calib():
    global _TC
    if _TC is None:
        p = "/work/trade_calib.json"
        _TC = _json.load(open(p)) if _os.path.exists(p) else dict(k_ranked=0.6, unranked=0.15,
              m={"0": 0, "1": .06, "2": .18, "3": .34, "4": .52, "5": .68, "6": .80, "7": .89, "8": .95, "9": .98})
    return _TC
_V_ANCHOR = [(1, 8.0), (3, 7.0), (5, 6.5), (10, 5.5), (15, 4.8), (25, 4.0), (40, 3.2), (50, 2.8), (75, 2.0), (100, 1.5)]
def vrank(rank):
    import math
    a = _V_ANCHOR
    if rank <= a[0][0]: return a[0][1]
    if rank >= a[-1][0]: return a[-1][1]
    for (x0, y0), (x1, y1) in zip(a, a[1:]):
        if x0 <= rank <= x1:
            f = (math.log(rank) - math.log(x0)) / (math.log(x1) - math.log(x0))
            return y0 + f * (y1 - y0)
_PRANK = None
def rank_at(pid, date):
    """his preseason top-100 rank at the deal (offseason deals read the next list)"""
    global _PRANK
    if _PRANK is None:
        _PRANK = {}
        p = "/work/prospect_ranks.json"
        if _os.path.exists(p):
            for r in _json.load(open(p)): _PRANK.setdefault(int(r["pid"]), {})[r["year"]] = r["rank"]
    rk = _PRANK.get(int(pid)) if pid else None
    if not rk: return None
    y, m = int(str(date)[:4]), int(str(date)[5:7])
    ly = y + 1 if m >= 10 else y
    for c in (ly, ly - 1):
        if c in rk: return rk[c]
    return None
def is_prospect(pid, date):
    """no major-league season before the deal"""
    rec = _lvm().get(int(pid)) if pid else None
    y, m = int(str(date)[:4]), int(str(date)[5:7])
    lim = y if m >= 10 else y - 1
    return not rec or not any(r[0] <= lim for r in rec.get("rows", []))
def open_expectation(pid, date, asof=2026):
    """expected value still to come from a prospect received in a trade"""
    if not pid or not is_prospect(pid, date): return 0.0
    tc = _trade_calib()
    rk = rank_at(pid, date)
    ev = tc["k_ranked"] * vrank(rk) if rk else tc["unranked"]
    y, m = int(str(date)[:4]), int(str(date)[5:7])
    t = asof - (y + 1 if m >= 10 else y)
    mt = tc["m"].get(str(max(t, 0)), 1.0)
    return ev * (1.0 - mt)

def trade_window(pid, teams, date, lev=None, cap=6, weight=True, sender=None, open_exp=True, to_control=True):
    """v5.9 asset accounting for a traded player. What the acquiring club
    received is the player's window from the trade, WHEREVER he plays it (a
    quick flip is graded in the flip, not lost), net of the salary that
    travels with him:
      * it runs six seasons, or to the end of his original club control if
        that is later (a prospect traded years before his debut: before,
        the draft credited those seasons and no trade charged them);
      * it ends at the first of: a new contract signed after the trade that
        owns the seasons (an extension owns only the seasons beyond his
        original control; inside control the acquirer keeps the value and
        pays the arbitration path), a free-agent filing, a release;
      * an October-December deal starts with the next season (the trade
        season was already played; before, it lost a season and took an
        extra year of discount);
      * a season he spent on the injured list still charges his salary;
      * each season discounted 0.9^years from the first season;
      * no leverage weight: the v5.2-5.8 win-curve weight charged the
        selling club at the buying club's leverage, moving value from bad
        clubs to good ones by construction (lev is ignored unless
        USE_LEVERAGE);
      * plus the expected value still to come from a prospect (open_expectation).
    Returns (total, {season: realized value}); total includes the open part."""
    rec = _lvm().get(int(pid)) if pid else None
    opn = open_expectation(pid, date) if (open_exp and pid) else 0.0
    if not rec: return opn, {}
    yd, md = int(str(date)[:4]), int(str(date)[5:7] or 7)
    off = md >= 10
    y0 = yd + 1 if off else yd
    end = y0 + cap - 1
    ce = control_end(pid)
    if to_control and ce is not None and ce >= y0: end = max(end, ce)
    nc = new_contract_season(pid, date, acq=teams)
    if nc is not None: end = min(end, nc - 1)
    end = min(end, asset_end(pid, date), 2026)
    byyear = _dd(list)
    for yr, tm, v in rec["rows"]:
        byyear[yr].append((tm, v))
    series = {}
    for yr in range(y0, end + 1):
        rows = byyear.get(yr, [])
        if yr == yd and not off:
            if not rows: continue
            # the trade season: what he produced after leaving the sending club
            # (with the acquirer, and with anyone the acquirer flipped him to)
            if sender:
                last = max([i for i, (tm, v) in enumerate(rows) if tm in sender], default=None)
                use = [v for tm, v in rows[last + 1:]] if last is not None else [v for tm, v in rows if tm in teams]
            else:
                use = [v for tm, v in rows if tm in teams]
            share = len([1 for tm, v in rows if tm in teams]) / len(rows)
        else:
            use = [v for tm, v in rows]; share = 1.0
        disc = (0.9 ** (yr - y0)) if weight else 1.0
        lv = 1.0
        if USE_LEVERAGE and lev and weight and rows:
            here_tm = [tm for tm, v in rows if tm in teams]
            tm_now = here_tm[-1] if here_tm else rows[-1][0]
            lv = lev({tm_now}, yr) if yr > yd else lev(teams, yr)
        cost = contract_cost(pid, yr, after=date, acq=teams, played=bool(rows)) * share
        if not use and cost == 0: continue
        series[yr] = sum(use) * lv * disc - cost * disc
    return sum(series.values()) + opn, series

def control_cap(pid, after):
    """last season a draft or international asset's control window can
    reach before a later contract owns the seasons"""
    nc = new_contract_season(pid, after) if pid else None
    return (nc - 1) if nc is not None else 9999



def waiver_window(pid, teams, date):
    """v5.9: a waiver claim or Rule 5 pick: the player's next four seasons
    (claim season on the claiming club only), undiscounted as before, now
    ending where a later contract owns the seasons, at a release or a
    free-agent filing, and net of the salary the claiming club takes on
    (a claim moves the contract: Alex Rios to the White Sox, 2009).
    Returns (total, {season: value})."""
    return trade_window(pid, teams, date, cap=4, weight=False, open_exp=False, to_control=False)
