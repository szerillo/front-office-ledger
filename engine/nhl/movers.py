# Which parts of the stat follow a player to a new club? Year-to-year correlation of each part's rate,
# for players who stayed with one club against players who played for a different club the next year.
import warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from value import compute
sk, go, tm, rr, grepl, gpw = compute(KD=1, KO=1, KPM=1, PHI=1, LT=1)
seasons = sorted(tm.seasonId.unique()); nxt = dict(zip(seasons[:-1], seasons[1:]))
one = sk.groupby(['playerId', 'seasonId']).teamId.transform('nunique') == 1
s1 = sk[one].copy(); s1['n'] = s1.seasonId.map(nxt)
m = s1.merge(s1, left_on=['playerId', 'n'], right_on=['playerId', 'seasonId'], suffixes=('', '2'))
m = m[(m.timeOnIce >= 36000) & (m.timeOnIce2 >= 36000)]
print('part      era  stayed(n, r)      moved(n, r)')
for c, den in (('evO', 'evT'), ('ppO', 'ppT'), ('defTeam', 'evT'), ('onD', 't5'), ('onO', 't5'), ('onPM', 'evT'), ('pen', 'timeOnIce'), ('gaa', 'timeOnIce')):
    for era in ('a', 'b'):
        d = m[(m.era == era) & (m[den] > (6000 if den == 'ppT' else 30000)) & (m[den + '2'] > (6000 if den == 'ppT' else 30000))]
        if c in ('onD', 'onO') and era == 'a': continue
        if c == 'onPM' and era == 'b': continue
        st, mv = d[d.teamId == d.teamId2], d[d.teamId != d.teamId2]
        f = lambda x: np.corrcoef(x[c] / x[den], x[c + '2'] / x[den + '2'])[0, 1]
        print(f"{c:9s} {era}    {len(st):5d} {f(st):.2f}        {len(mv):5d} {f(mv):.2f}")
g1 = go[go.groupby(['playerId', 'seasonId']).teamId.transform('nunique') == 1].copy(); g1['n'] = g1.seasonId.map(nxt)
gm = g1.merge(g1, left_on=['playerId', 'n'], right_on=['playerId', 'seasonId'], suffixes=('', '2')); gm = gm[(gm.shotsAgainst >= 800) & (gm.shotsAgainst2 >= 800)]
for nm, d in (('stayed', gm[gm.teamId == gm.teamId2]), ('moved', gm[gm.teamId != gm.teamId2])):
    print('goalie saves above average per shot,', nm, len(d), round(np.corrcoef(d.gsaa0 / d.shotsAgainst, d.gsaa02 / d.shotsAgainst2)[0, 1], 2))
# does a goalie's new club's other goalies' save rate tell us about him? (club effect on save percentage)
tg = go.groupby(['seasonId', 'teamId']).agg(tg=('gsaa0', 'sum'), ts=('shotsAgainst', 'sum')).reset_index()
x = go.merge(tg, on=['seasonId', 'teamId']); x = x[(x.shotsAgainst >= 600) & (x.ts - x.shotsAgainst >= 600)]
print('goalie vs his club mates the same season (club effect), n', len(x), 'r', round(np.corrcoef(x.gsaa0 / x.shotsAgainst, (x.tg - x.gsaa0) / (x.ts - x.shotsAgainst))[0, 1], 2))
