# Two checks on the value stat: does a player's value repeat, and do last year's values, carried to this
# year's clubs with this year's ice time, predict the clubs' goal difference.
import sys, warnings, itertools, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from value import compute
def evaluate(**kw):
    sk, go, tm, rr, grepl, gpw = compute(**kw)
    seasons = sorted(tm.seasonId.unique()); nxt = dict(zip(seasons[:-1], seasons[1:]))
    ps = sk.groupby(['playerId', 'seasonId', 'pos', 'era']).agg(gaa=('gaa', 'sum'), gar=('gar', 'sum'), t=('timeOnIce', 'sum')).reset_index()
    ps['n'] = ps.seasonId.map(nxt); m = ps.merge(ps, left_on=['playerId', 'n'], right_on=['playerId', 'seasonId'], suffixes=('', '2'))
    m = m[(m.t >= 36000) & (m.t2 >= 36000)]
    rep = {p + e: np.corrcoef(d.gar / d.t, d.gar2 / d.t2)[0, 1] for (p, e), d in m.groupby(['pos', 'era'])}
    gs = go.groupby(['playerId', 'seasonId']).agg(g=('gsaa', 'sum'), sa=('shotsAgainst', 'sum')).reset_index(); gs['n'] = gs.seasonId.map(nxt)
    gm = gs.merge(gs, left_on=['playerId', 'n'], right_on=['playerId', 'seasonId'], suffixes=('', '2')); gm = gm[(gm.sa >= 1000) & (gm.sa2 >= 1000)]
    rep['G'] = np.corrcoef(gm.g / gm.sa, gm.g2 / gm.sa2)[0, 1]
    # carry last year's rates forward
    prev = {v: k for k, v in nxt.items()}
    pr = ps.assign(seasonId=ps.n)[['playerId', 'seasonId', 'gaa', 't']].rename(columns={'gaa': 'pg', 't': 'pt'})
    cur = sk.merge(pr, on=['playerId', 'seasonId'], how='left')
    C = 30000.0
    rrate = cur.set_index(['era', 'pos']).index.map(rr).values
    rate = np.where(cur.pt.notna(), (cur.pg / cur.pt.clip(lower=1)) * cur.pt / (cur.pt + C) + rrate * C / (cur.pt.fillna(0) + C), rrate)
    cur['pred'] = rate * cur.timeOnIce
    gp = gs.assign(seasonId=gs.n)[['playerId', 'seasonId', 'g', 'sa']].rename(columns={'g': 'pg', 'sa': 'psa'})
    gc = go.merge(gp, on=['playerId', 'seasonId'], how='left'); CG = 1500.0
    grate = np.where(gc.psa.notna(), (gc.pg / gc.psa.clip(lower=1)) * gc.psa / (gc.psa + CG) + grepl * CG / (gc.psa.fillna(0) + CG), grepl)
    gc['pred'] = grate * gc.shotsAgainst
    G = ['seasonId', 'teamId']
    t = tm.merge(cur.groupby(G).pred.sum().rename('sp').reset_index(), on=G).merge(gc.groupby(G).pred.sum().rename('gp_').reset_index(), on=G)
    t['pgd'] = t.seasonId.map(prev).map(lambda s: 0) ; t = t[t.seasonId != seasons[0]]
    pm = tm.assign(seasonId=tm.seasonId.map(nxt))[['seasonId', 'teamId', 'gd', 'gamesPlayed']].rename(columns={'gd': 'pgd0', 'gamesPlayed': 'pgp'})
    t = t.merge(pm, on=G, how='left')
    out = {}
    for era, d in (('a', t[t.seasonId < 20092010]), ('b', t[t.seasonId >= 20102011])):
        y = d.gd / d.gamesPlayed
        out['team_' + era] = np.corrcoef((d.sp + d.gp_) / d.gamesPlayed, y)[0, 1]; out['sk_' + era] = np.corrcoef(d.sp / d.gamesPlayed, y)[0, 1]
        dd = d.dropna(subset=['pgd0']); out['base_' + era] = np.corrcoef(dd.pgd0 / dd.pgp, dd.gd / dd.gamesPlayed)[0, 1]
    tw = sk.groupby(G).war.sum().add(go.groupby(G).war.sum(), fill_value=0)
    tot = sk.war.sum() + go.war.sum()
    out.update(rep); out['shareD'] = sk[sk.pos == 'D'].war.sum() / tot; out['shareG'] = go.war.sum() / tot; out['clubWAR'] = tw.mean()
    return out
if __name__ == '__main__':
    grid = [dict(), dict(KDD=0.3), dict(KDD=1.0), dict(KD=0.4, KO=0.4), dict(KD=0.2, KO=0.2), dict(PHI=1.0), dict(PHI=0.5), dict(LT=0.25), dict(KPM=0), dict(KPM=0.2)]
    for kw in grid:
        o = evaluate(**kw); print(str(kw).ljust(40), ' '.join(f"{k}={v:.3f}" for k, v in o.items()), flush=True)
