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
DRAFT_K = 1.309
DRAFT_SHAPE = {0: 0.0, 1: 0.0, 2: 0.12, 3: 0.23, 4: 0.32, 5: 0.47, 6: 0.64, 7: 0.80, 8: 0.92, 9: 0.97}

def draft_maturity(draft_year, asof=2026):
    return DRAFT_K * DRAFT_SHAPE.get(max(0, asof - int(draft_year)), 1.0)

def control_years(rec):
    """the six seasons starting with his MLB debut season"""
    if not rec or not rec.get("rows"): return set()
    y0 = min(y for y, _, _ in rec["rows"])
    return set(range(y0, y0 + 6))

def control_value(rec, teams=None):
    """value in the control years; anywhere (teams=None) or on `teams`"""
    if not rec: return 0.0
    cy = control_years(rec)
    return sum(v for y, tm, v in rec["rows"] if y in cy and (teams is None or tm in teams))

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
}
import json as _json, os as _os
_COST = None
def _cost_table():
    global _COST
    if _COST is not None: return _COST
    _COST = {}
    p = "/work/desk_data.json"
    if not _os.path.exists(p): return _COST
    D = _json.load(open(p))
    dpw = {int(k): v for k, v in D["market"]["dpwHist"].items()}
    for c in sorted(D["book"], key=lambda c: c[1]):       # later deals overwrite earlier ones
        pid, off, yrs, tot = c[11], c[1], c[3], c[4]
        if not pid or not yrs: continue
        aav = tot / yrs
        for y in range(off + 1, off + yrs + 1):
            _COST.setdefault(int(pid), {})[y] = max(0.0, aav - 0.75) / dpw.get(min(y, 2026), 9.7)
    for pid, ys in NET_PAID.items():
        for y, m in ys.items():
            _COST.setdefault(int(pid), {})[y] = max(0.0, m - 0.75) / dpw.get(min(y, 2026), 9.7)
    return _COST

def contract_cost(pid, yr):
    """guaranteed salary above the minimum for that season, in wins"""
    try: return _cost_table().get(int(pid), {}).get(int(yr), 0.0)
    except Exception: return 0.0
