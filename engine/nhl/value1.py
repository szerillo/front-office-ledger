# v1: the shift-level model replaces the season-line guesses about five-on-five play (2010-11 on).
# Variants are scored on the same tests as v0. Usage: python3 value1.py            (prints the comparison)
import warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from value import compute
from test import evaluate_t
def build(variant='C', lam=50, KF=0.5, DW=1.0):
    sk, go, tm, rr0, grepl, gpw = compute()
    sk = sk[sk.seasonId >= 20102011].copy(); go = go[go.seasonId >= 20102011].copy(); tm = tm[tm.seasonId >= 20102011].copy()
    sk['season'] = sk.seasonId // 10000
    r = pd.read_pickle(f'rapm_{lam}.pkl'); sk = sk.merge(r, on=['playerId', 'season'], how='left')
    share = (sk.t5 / sk.groupby(['playerId', 'season']).t5.transform('sum').clip(lower=1)).fillna(0)
    sk['rOff'] = (sk.off * sk.toi5 / 3600 * share).fillna(0); sk['rDef'] = (-sk['def'] * sk.toi5 / 3600 * share).fillna(0) * DW
    x = pd.read_pickle('xg.pkl'); x = x[(x.own == 5) & (x.oth == 5) & (x.og == 1)]
    x = x.assign(xgn=x.xg * x.season.map(x.groupby('season').goal.sum() / x.groupby('season').xg.sum()))
    f = x.groupby(['shooter', 'season']).agg(ig=('goal', 'sum'), ix=('xgn', 'sum')).reset_index().rename(columns={'shooter': 'playerId'})
    sk = sk.merge(f, on=['playerId', 'season'], how='left'); sk['fin'] = ((sk.ig - sk.ix) * share).fillna(0) * KF
    if variant == 'A': sk['gaa'] = sk.evO + sk.ppO + sk.onD + sk.onO + sk.pen
    if variant == 'B': sk['gaa'] = sk.evO + sk.ppO + sk.rDef + sk.pen
    if variant == 'C': sk['gaa'] = sk.rOff + sk.fin + sk.rDef + sk.ppO + sk.pen
    if variant == 'E': sk['gaa'] = sk.evO + sk.ppO + sk.rDef + sk.onO + sk.pen
    if variant == 'F': sk['gaa'] = sk.evO + sk.ppO + sk.onD + sk.onO + sk.pen + 0.5 * sk.rDef + 0.5 * sk.rOff
    if variant == 'G': sk['gaa'] = sk.evO + sk.ppO + sk.onO + sk.pen + np.where(sk.pos == 'D', 2.0, 1.0) * sk.rDef
    if variant == 'D': sk['gaa'] = 0.5 * sk.evO + 0.5 * (sk.rOff + sk.fin) + sk.rDef + sk.ppO + sk.pen
    elig = sk.gamesPlayed >= 10
    pool = sk[elig & (((sk.pos == 'F') & (sk.rk > 12)) | ((sk.pos == 'D') & (sk.rk > 6)))]
    rr = pool.groupby(['era', 'pos']).apply(lambda d: d.gaa.sum() / d.timeOnIce.sum())
    sk['gar'] = sk.gaa - sk.timeOnIce * sk.set_index(['era', 'pos']).index.map(rr).values; sk['war'] = sk.gar / sk.seasonId.map(gpw)
    return sk, go, tm, rr, grepl, gpw
def movers(sk):
    one = sk[sk.groupby(['playerId', 'seasonId']).teamId.transform('nunique') == 1].copy(); one['n'] = one.season + 1
    m = one.merge(one, left_on=['playerId', 'n'], right_on=['playerId', 'season'], suffixes=('', '2')); m = m[(m.timeOnIce >= 36000) & (m.timeOnIce2 >= 36000) & (m.teamId != m.teamId2)]
    c = lambda d: np.corrcoef(d.gaa / d.timeOnIce, d.gaa2 / d.timeOnIce2)[0, 1]
    return len(m), c(m), c(m[m.pos == 'F']), c(m[m.pos == 'D'])
if __name__ == '__main__':
    for v, kw in (('A', {}), ('E', {}), ('F', {}), ('G', {})):
        t = build(v, **kw); o = evaluate_t(*t); n, mv, mvF, mvD = movers(t[0])
        print(v, kw, 'repeat F %.2f D %.2f | moved n%d all %.2f F %.2f D %.2f | clubs next year %.3f (standings alone %.3f) | D share %.2f G share %.2f club wins %.1f' % (o['Fb'], o['Db'], n, mv, mvF, mvD, o['team_b'], o['base_b'], o['shareD'], o['shareG'], o['clubWAR']), flush=True)
