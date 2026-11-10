# Write the v1 player-season file: v0 plus half of the shift-level effects from 2010-11 on, v0 before that.
import warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from value1 import build
sk, go, tm, rr, grepl, gpw = build('F')
old = pd.read_csv('player_seasons.csv'); old = old[old.seasonId < 20102011]
ps = sk.groupby(['playerId', 'seasonId', 'teamId']).agg(name=('skaterFullName', 'first'), pos=('pos', 'first'), gp=('gamesPlayed', 'sum'), toi=('timeOnIce', 'sum'), war=('war', 'sum')).reset_index()
gs = go.groupby(['playerId', 'seasonId', 'teamId']).agg(name=('goalieFullName', 'first'), gp=('gamesPlayed', 'sum'), toi=('timeOnIce', 'sum'), war=('war', 'sum')).reset_index(); gs['pos'] = 'G'
al = pd.concat([old, ps, gs]); al['war'] = al.war.round(2); al.to_csv('player_seasons_v1.csv', index=False)
v0 = pd.read_csv('player_seasons.csv'); m = ps.merge(v0, on=['playerId', 'seasonId', 'teamId'], suffixes=('', '0'))
print('rows', len(al), '| v1 against v0, skater seasons 2010-11 on: r = %.3f' % np.corrcoef(m.war, m.war0)[0, 1])
a = ps[ps.seasonId == 20232024].groupby(['playerId', 'name', 'pos']).war.sum().reset_index().sort_values('war', ascending=False)
print('2023-24 F:', ', '.join(f"{r.name} {r.war:.1f}" for r in a[a.pos == 'F'].head(6).itertuples())); print('2023-24 D:', ', '.join(f"{r.name} {r.war:.1f}" for r in a[a.pos == 'D'].head(8).itertuples()))
m['d'] = m.war - m.war0; mm = m[m.gp >= 60]
print('biggest gains from the shift-level part:', ', '.join(f"{r.name} {str(r.seasonId)[2:4]} {r.d:+.1f}" for r in mm.sort_values('d', ascending=False).head(8).itertuples()))
print('biggest losses:', ', '.join(f"{r.name} {str(r.seasonId)[2:4]} {r.d:+.1f}" for r in mm.sort_values('d').head(8).itertuples()))
c = ps.groupby(['playerId', 'name', 'pos']).war.sum().reset_index().sort_values('war', ascending=False); print('careers 2010-11 on, D:', ', '.join(f"{r.name} {r.war:.0f}" for r in c[c.pos == 'D'].head(10).itertuples()))
