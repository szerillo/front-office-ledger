# Draft channel, first cut: every pick since 1998 against what its slot usually returns while the club
# controls the player, in v0 wins. Needs player_seasons.csv (value.py) and draft/*.json (records.nhl.com).
import json, glob, numpy as np, pandas as pd
import sys
ps = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else 'player_seasons.csv'); bio = pd.read_pickle('bio.pkl')
picks = pd.DataFrame([r for f in sorted(glob.glob('draft/d*.json')) for r in json.load(open(f))['data']])
picks = picks[(picks.draftYear >= 1998) & (picks.supplementalDraft != 'Y')].copy()
picks['posg'] = picks.position.map(lambda p: 'G' if p == 'G' else 'D' if p == 'D' else 'F')
# seasons a club controls a pick: through age 26 on the June 30 that ends the season, or seven full seasons
ps['y0'] = ps.seasonId // 10000
s = ps.groupby(['playerId', 'y0']).agg(war=('war', 'sum'), gp=('gp', 'sum'), pos=('pos', 'first')).reset_index()
s = s.merge(picks[['playerId', 'draftYear', 'birthDate']].dropna(subset=['playerId']), on='playerId')
s['age'] = (s.y0 + 1) - pd.to_datetime(s.birthDate).dt.year - (pd.to_datetime(s.birthDate).dt.month > 6).astype(int)
s = s.sort_values(['playerId', 'y0']); s['full'] = (s.gp >= np.where(s.pos == 'G', 30, 40)).astype(int)
s['acc'] = s.groupby('playerId').full.cumsum() - s.full
ctl = s[(s.age <= 26) & (s.acc < 7) & (s.y0 >= s.draftYear)]
v = ctl.groupby('playerId').agg(cw=('war', 'sum'), cgp=('gp', 'sum')).reset_index()
car = s.groupby('playerId').agg(career=('war', 'sum'), gp=('gp', 'sum')).reset_index()
picks = picks.merge(v, on='playerId', how='left').merge(car, on='playerId', how='left')
for c in ('cw', 'cgp', 'career', 'gp'): picks[c] = picks[c].fillna(0)
done = picks[picks.draftYear <= 2017]
# what a slot returns: binned means, forced to fall with the pick, read off on a log scale
edges = [1, 2, 3, 4, 5, 6, 8, 11, 16, 21, 31, 46, 61, 91, 121, 161, 211, 400]
b = done.assign(bin=pd.cut(done.overallPickNumber, edges, right=False)).groupby('bin', observed=True).agg(m=('cw', 'mean'), x=('overallPickNumber', 'mean'), n=('cw', 'size'), played=('cgp', lambda g: (g >= 100).mean())).reset_index()
m = b.m.values.copy(); w = b.n.values.astype(float)
i = 0
blocks = [[m[k], w[k], 1] for k in range(len(m))]
out = []
for blk in blocks:
    out.append(blk)
    while len(out) > 1 and out[-2][0] < out[-1][0]:
        a, c = out[-2], out[-1]; out[-2:] = [[(a[0] * a[1] + c[0] * c[1]) / (a[1] + c[1]), a[1] + c[1], a[2] + c[2]]]
iso = np.concatenate([[blk[0]] * blk[2] for blk in out]); b['iso'] = iso
slot = lambda p: np.interp(np.log(p), np.log(b.x.values), b.iso.values)
picks['exp0'] = slot(picks.overallPickNumber.clip(upper=b.x.max()))
# v0 runs low on defensemen, so a pick is held to what its own position returns at that part of the draft
picks['tier'] = pd.cut(picks.overallPickNumber, [0, 10, 30, 90, 400], labels=['1-10', '11-30', '31-90', '91+'])
dn = picks[picks.draftYear <= 2017]
pf = (dn.groupby(['tier', 'posg'], observed=True).cw.sum() / dn.groupby(['tier', 'posg'], observed=True).exp0.sum()).rename('pf')
picks = picks.join(pf, on=['tier', 'posg']); picks['exp'] = picks.exp0 * picks.pf; picks['net'] = picks.cw - picks.exp
# who was in the chair on draft day
gm = pd.DataFrame(json.load(open('draft/gm_general-manager-franchise-records.json'))['data']); gm = gm[gm.gameTypeId == 2]
def chair(r):
    g = gm[(gm.teamId == r.draftedByTeamId) & (gm.startDate <= r.draftDate) & (gm.endDate >= r.draftDate)] if isinstance(r.draftDate, str) else gm.iloc[0:0]
    if not len(g): g = gm[(gm.teamId == r.draftedByTeamId) & (gm.startDate <= f'{r.draftYear}-06-30') & (gm.endDate >= f'{r.draftYear}-06-01')]
    return g.sort_values('startDate').fullName.iloc[-1] if len(g) else None
ch = picks.drop_duplicates(['draftYear', 'draftedByTeamId']).assign(gm=lambda d: d.apply(chair, axis=1))[['draftYear', 'draftedByTeamId', 'gm']]
picks = picks.merge(ch, on=['draftYear', 'draftedByTeamId'])
picks.to_pickle('draft_picks.pkl')
if __name__ == '__main__':
    pd.set_option('display.width', 220)
    print('slot table (drafts 1998-2017):'); print(b.assign(m=b.m.round(2), iso=b.iso.round(2), x=b.x.round(0), played=b.played.round(2))[['bin', 'n', 'm', 'iso', 'played']].to_string(index=False))
    d = picks[picks.draftYear <= 2017]
    print('\nposition factors:', pf.round(2).to_dict())
    print('\nno chair found for', int(d.gm.isna().sum()), 'of', len(d), 'picks')
    f = lambda r: f"{r.playerName} ({r.draftYear} #{r.overallPickNumber} {r.triCode}) {r.net:+.1f}"
    print('\nbest picks:', '; '.join(f(r) for r in d.sort_values('net', ascending=False).head(12).itertuples()))
    print('\nworst picks:', '; '.join(f(r) for r in d.sort_values('net').head(8).itertuples()))
    cy = d.groupby(['triCode', 'draftYear']).agg(net=('net', 'sum'), n=('net', 'size')).reset_index()
    print('\nbest classes:', '; '.join(f"{r.triCode} {r.draftYear} {r.net:+.1f}" for r in cy.sort_values('net', ascending=False).head(8).itertuples()))
    print('worst classes:', '; '.join(f"{r.triCode} {r.draftYear} {r.net:+.1f}" for r in cy.sort_values('net').head(6).itertuples()))
    g = d.groupby('gm').agg(net=('net', 'sum'), exp=('exp', 'sum'), n=('net', 'size'), drafts=('draftYear', 'nunique')).reset_index(); g = g[g.drafts >= 4]; g['per'] = g.net / g.drafts
    print('\nchairs, 4+ drafts, net wins per draft, top:', '; '.join(f"{r.gm} {r.per:+.1f} ({r.drafts})" for r in g.sort_values('per', ascending=False).head(10).itertuples()))
    print('bottom:', '; '.join(f"{r.gm} {r.per:+.1f} ({r.drafts})" for r in g.sort_values('per').head(8).itertuples()))
    # does drafting repeat? first half of a chair's drafts against the second half
    h = d.dropna(subset=['gm']).groupby(['gm', 'draftYear']).net.sum().reset_index().sort_values(['gm', 'draftYear'])
    rows = []
    for nme, x in h.groupby('gm'):
        if len(x) >= 6: k = len(x) // 2; rows.append((x.net.iloc[:k].mean(), x.net.iloc[k:].mean()))
    rows = np.array(rows); print('\nchairs with 6+ drafts:', len(rows), 'first half vs second half r = %.2f' % np.corrcoef(rows[:, 0], rows[:, 1])[0, 1])
    print('share of net by position drafted: ', d.groupby('posg').net.sum().round(0).to_dict(), '| picks', d.posg.value_counts().to_dict())
