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
