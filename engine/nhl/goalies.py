# Goalies on expected goals: goals saved above expected per unblocked attempt faced, against the plain
# save-percentage version, for repeatability and for whether it follows a goalie to a new club.
import numpy as np, pandas as pd
u = pd.read_pickle('xg.pkl'); u = u[(u.og == 1) & (u.goalie > 0)].copy()
u['xgn'] = u.xg * u.season.map(u.groupby('season').goal.sum() / u.groupby('season').xg.sum())
u['sog'] = (u.type != 'm').astype(int); lg = u.groupby('season').apply(lambda d: d.goal.sum() / d.sog.sum())
g = u.groupby(['goalie', 'season', 'opp']).agg(att=('xg', 'size'), sog=('sog', 'sum'), ga=('goal', 'sum'), xg=('xgn', 'sum')).reset_index().rename(columns={'opp': 'team'})
g['gsax'] = g.xg - g.ga; g['gsaa'] = g.sog * g.season.map(lg) - g.ga
g.to_pickle('goalie_xg.pkl')
s = g.groupby(['goalie', 'season']).agg(att=('att', 'sum'), sog=('sog', 'sum'), gsax=('gsax', 'sum'), gsaa=('gsaa', 'sum'), nteam=('team', 'nunique'), team=('team', 'first')).reset_index()
s['n'] = s.season + 1; m = s.merge(s, left_on=['goalie', 'n'], right_on=['goalie', 'season'], suffixes=('', '2')); m = m[(m.sog >= 1000) & (m.sog2 >= 1000)]
r = lambda d, c: np.corrcoef(d[c] / d.sog, d[c + '2'] / d.sog2)[0, 1]
print('goalie seasons paired (1,000 shots both years):', len(m))
print('year to year, above expected: %.2f   plain save percentage: %.2f' % (r(m, 'gsax'), r(m, 'gsaa')))
one = m[(m.nteam == 1) & (m.nteam2 == 1)]; st, mv = one[one.team == one.team2], one[one.team != one.team2]
print('stayed n%d: above expected %.2f, plain %.2f | moved n%d: above expected %.2f, plain %.2f' % (len(st), r(st, 'gsax'), r(st, 'gsaa'), len(mv), r(mv, 'gsax'), r(mv, 'gsaa')))
t = g.groupby(['season', 'team']).agg(tx=('gsax', 'sum'), ta=('gsaa', 'sum'), ts=('sog', 'sum')).reset_index(); x = g.merge(t, on=['season', 'team']); x = x[(x.sog >= 600) & (x.ts - x.sog >= 600)]
print('two goalies on one club the same season (club effect), n%d: above expected %.2f, plain %.2f' % (len(x), np.corrcoef(x.gsax / x.sog, (x.tx - x.gsax) / (x.ts - x.sog))[0, 1], np.corrcoef(x.gsaa / x.sog, (x.ta - x.gsaa) / (x.ts - x.sog))[0, 1]))
print('spread per 1,000 shots (sd, 1,000+ shots): above expected %.1f, plain %.1f' % ((s[s.sog >= 1000].gsax / s[s.sog >= 1000].sog).std() * 1000, (s[s.sog >= 1000].gsaa / s[s.sog >= 1000].sog).std() * 1000))
go = pd.read_pickle('go.pkl'); nm = go.drop_duplicates('playerId').set_index('playerId').goalieFullName
for yr in (2023, 2025): print(yr, ', '.join(f"{nm.get(r.goalie, r.goalie)} {r.gsax:+.0f}" for r in s[s.season == yr].sort_values('gsax', ascending=False).head(6).itertuples()))
print('share of unblocked attempts with a goalie id:', round(len(u) / len(pd.read_pickle('xg.pkl').query('og == 1')), 3))
