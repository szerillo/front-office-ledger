# Ledger hockey value, first cut: goals above replacement for every skater and goalie season, in wins.
# Inputs are the league's own season lines only (see fetch.py). Usage: python3 value.py [kd ko kpm]
import sys, numpy as np, pandas as pd
DEF = dict(KD=0.15, KO=0.15, KPM=0.1, PHI=0.7, LT=0.0)
def compute(KD=0.15, KO=0.15, KPM=0.1, PHI=0.7, LT=0.0, KDD=None):
    KDD = 2 * KD if KDD is None else KDD
    sk = pd.read_pickle('sk.pkl'); go = pd.read_pickle('go.pkl'); tm = pd.read_pickle('tm.pkl')
    sk = sk[sk.timeOnIce > 0].copy()
    G = ['seasonId', 'teamId']
    sk['evG'] = sk.goals - sk.ppGoals; sk['evA'] = sk.assists - (sk.ppPoints - sk.ppGoals); sk['ppA'] = sk.ppPoints - sk.ppGoals
    sk['evT'] = sk.timeOnIce - sk.ppTimeOnIce; sk['ppT'] = sk.ppTimeOnIce
    # offence: each club's goals shared among its skaters by goals plus half of assists, even strength and power play apart
    for s in ('ev', 'pp'):
        w = sk[s + 'G' if s == 'ev' else 'ppGoals'] + 0.5 * sk[s + 'A']
        tot = w.groupby([sk.seasonId, sk.teamId]).transform('sum'); tg = sk['evG' if s == 'ev' else 'ppGoals'].groupby([sk.seasonId, sk.teamId]).transform('sum')
        sk[s + 'GC'] = np.where(tot > 0, w / tot * tg, 0.0)
        lg = sk.groupby(['seasonId', 'pos']).agg(gc=(s + 'GC', 'sum'), t=(s + 'T', 'sum')); lg['r'] = lg.gc / lg.t
        sk[s + 'O'] = sk[s + 'GC'] - sk[s + 'T'] * sk.set_index(['seasonId', 'pos']).index.map(lg.r).values
    # goalies and the club's shot suppression
    lgg = go.groupby('seasonId').agg(sa=('shotsAgainst', 'sum'), ga=('goalsAgainst', 'sum')); lgg['sv'] = 1 - lgg.ga / lgg.sa
    go['gsaa0'] = go.shotsAgainst * (1 - go.seasonId.map(lgg.sv)) - go.goalsAgainst
    go['gsaa'] = go.gsaa0 * PHI
    tsa = go.groupby(G).agg(tsa=('shotsAgainst', 'sum'), tg0=('gsaa0', 'sum')).reset_index().merge(tm[['seasonId', 'teamId', 'gamesPlayed', 'goalsFor', 'goalsAgainst', 'points']], on=G)
    lsa = tsa.groupby('seasonId').apply(lambda d: d.tsa.sum() / d.gamesPlayed.sum())
    tsa['shotPart'] = (tsa.seasonId.map(lsa) * tsa.gamesPlayed - tsa.tsa) * (1 - tsa.seasonId.map(lgg.sv)) * LT + tsa.tg0 * (1 - PHI)
    sk = sk.merge(tsa[G + ['shotPart']], on=G, how='left')
    dw = np.where(sk.pos == 'D', 10.0, 5.0) * sk.evT
    sk['defTeam'] = sk.shotPart * dw / pd.Series(dw).groupby([sk.seasonId.values, sk.teamId.values]).transform('sum').values
    # on-ice shot attempts relative to the same club without him (2009-10 on); plus-minus relative to the club before that
    sk['t5'] = sk.timeOnIcePerGame5v5 * sk.gamesPlayed
    has = sk.satFor.fillna(0) > 0
    for c in ('satFor', 'satAgainst', 't5'): sk['T' + c] = sk[c].groupby([sk.seasonId, sk.teamId]).transform('sum') / 5
    gpa = (sk[has].groupby('seasonId').evenStrengthGoalsFor.sum() / sk[has].groupby('seasonId').satFor.sum())
    offT = (sk.Tt5 - sk.t5).clip(lower=1)
    relF = sk.satFor / sk.t5.clip(lower=1) - (sk.TsatFor - sk.satFor) / offT; relA = sk.satAgainst / sk.t5.clip(lower=1) - (sk.TsatAgainst - sk.satAgainst) / offT
    g = sk.seasonId.map(gpa)
    sk['onD'] = np.where(has, -relA * sk.t5 * g * np.where(sk.pos == 'D', KDD, KD), 0.0); sk['onO'] = np.where(has, relF * sk.t5 * g * KO, 0.0)
    tpm = sk.plusMinus.groupby([sk.seasonId, sk.teamId]).transform('sum') / sk.evT.groupby([sk.seasonId, sk.teamId]).transform('sum')
    sk['pmRel'] = sk.plusMinus - tpm * sk.evT
    sk['onPM'] = np.where(has, 0.0, sk.pmRel * KPM)
    # penalties: drawn minus taken where the league counts both, taken only before that
    pv = (sk.groupby('seasonId').ppGoals.sum() - sk.groupby('seasonId').shGoals.sum()) / sk.groupby('seasonId').minorPenalties.sum()
    sk['net'] = np.where(sk.penaltiesDrawn.notna() & has, sk.penaltiesDrawn.fillna(0) - sk.minorPenalties, -sk.minorPenalties)
    ln = sk.groupby(['seasonId', 'pos']).agg(n=('net', 'sum'), t=('timeOnIce', 'sum')); ln['r'] = ln.n / ln.t
    sk['pen'] = (sk.net - sk.timeOnIce * sk.set_index(['seasonId', 'pos']).index.map(ln.r).values) * sk.seasonId.map(pv)
    sk['gaa'] = sk.evO + sk.ppO + sk.defTeam + sk.onD + sk.onO + sk.onPM + sk.pen
    # replacement level: skaters outside a club's top 12 forwards and top 6 defensemen by ice time per game
    sk['tpg'] = sk.timeOnIce / sk.gamesPlayed
    elig = sk.gamesPlayed >= 10
    sk['rk'] = sk[elig].groupby(['seasonId', 'teamId', 'pos']).tpg.rank(ascending=False)
    pool = sk[elig & (((sk.pos == 'F') & (sk.rk > 12)) | ((sk.pos == 'D') & (sk.rk > 6)))]
    sk['era'] = np.where(sk.seasonId >= 20092010, 'b', 'a'); pool = pool.assign(era=np.where(pool.seasonId >= 20092010, 'b', 'a'))
    rr = pool.groupby(['era', 'pos']).apply(lambda d: d.gaa.sum() / d.timeOnIce.sum())
    sk['gar'] = sk.gaa - sk.timeOnIce * sk.set_index(['era', 'pos']).index.map(rr).values
    go['rk'] = go.groupby(G).timeOnIce.rank(ascending=False)
    gp = go[go.rk >= 3]; grepl = gp.gsaa.sum() / gp.shotsAgainst.sum()
    go['gar'] = go.gsaa - go.shotsAgainst * grepl
    # goals per win from the standings, three seasons at a time
    tm = tm.assign(gd=tm.goalsFor - tm.goalsAgainst)
    seasons = sorted(tm.seasonId.unique()); gpw = {}
    for i, s in enumerate(seasons):
        d = tm[tm.seasonId.isin(seasons[max(0, i - 1): i + 2])]; d = d.assign(p=d.points - d.groupby('seasonId').points.transform('mean') * d.gamesPlayed / d.groupby('seasonId').gamesPlayed.transform('mean'))
        gpw[s] = 2 / np.polyfit(d.gd, d.p, 1)[0]
    sk['war'] = sk.gar / sk.seasonId.map(gpw); go['war'] = go.gar / go.seasonId.map(gpw)
    return sk, go, tm, rr, grepl, gpw

if __name__ == '__main__':
    sk, go, tm, rr, grepl, gpw = compute(**DEF); G = ['seasonId', 'teamId']
    sk.to_pickle('sk_val.pkl'); go.to_pickle('go_val.pkl'); pd.Series(gpw).to_pickle('gpw.pkl')
    print('replacement, goals per 60 below average:', {k: round(v * 3600, 3) for k, v in rr.items()}, 'goalie per 1000 shots', round(grepl * 1000, 1))
    print('goals per win:', {str(s)[2:4]: round(v, 2) for s, v in gpw.items()})
    tw = sk.groupby(G).war.sum().add(go.groupby(G).war.sum(), fill_value=0).rename('war').reset_index().merge(tm, on=G)
    print('club wins above replacement: mean %.1f sd %.1f; r with points %.3f; r with goal difference %.3f' % (tw.war.mean(), tw.war.std(), np.corrcoef(tw.war, tw.points / tw.gamesPlayed)[0, 1], np.corrcoef(tw.war / tw.gamesPlayed, tw.gd / tw.gamesPlayed)[0, 1]))
    sh = sk.groupby('pos').war.sum() / (sk.war.sum() + go.war.sum()); print('share of wins: F %.2f D %.2f G %.2f' % (sh['F'], sh['D'], go.war.sum() / (sk.war.sum() + go.war.sum())))
    for s in (20232024, 20152016, 20002001):
        a = sk[sk.seasonId == s].groupby(['playerId', 'skaterFullName', 'pos']).agg(war=('war', 'sum'), gp=('gamesPlayed', 'sum')).reset_index().sort_values('war', ascending=False)
        print(s, 'F:', ', '.join(f"{r.skaterFullName} {r.war:.1f}" for r in a[a.pos == 'F'].head(8).itertuples()))
        print('   D:', ', '.join(f"{r.skaterFullName} {r.war:.1f}" for r in a[a.pos == 'D'].head(6).itertuples()))
        b = go[go.seasonId == s].groupby(['playerId', 'goalieFullName']).war.sum().reset_index().sort_values('war', ascending=False)
        print('   G:', ', '.join(f"{r.goalieFullName} {r.war:.1f}" for r in b.head(5).itertuples()), '| worst', ', '.join(f"{r.goalieFullName} {r.war:.1f}" for r in b.tail(2).itertuples()))
