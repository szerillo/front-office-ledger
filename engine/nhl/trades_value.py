# Trade channel, first cut. Each side of each trade is worth what its players produced for the acquiring club
# from the trade until they left it (v1 wins, seven seasons at most), plus each pick at what its slot usually
# returns. A side's net is what it got minus what the other side got. Attributed to the general manager in
# the chair that day. Needs trades.json, player_seasons_v1.csv, draft_picks.pkl and the tenure file.
import json, numpy as np, pandas as pd
T = json.load(open('trades.json')); ps = pd.read_csv('player_seasons_v1.csv'); ps['y'] = ps.seasonId // 10000
W = {(r.playerId, r.y, r.teamId): r.war for r in ps.groupby(['playerId', 'y', 'teamId']).war.sum().reset_index().itertuples()}
dp = pd.read_pickle('draft_picks.pkl'); dp['orig'] = dp.teamPickHistory.fillna(dp.triCode).str.split('-').str[0]
tri = {(r.draftYear, r.draftedByTeamId): r.triCode for r in dp.itertuples()}
PK = {}
for r in dp.itertuples(): PK.setdefault((r.draftYear, r.roundNumber, r.orig), []).append((r.exp0, str(r.teamPickHistory or r.triCode)))
SLOT = dp.groupby('overallPickNumber').exp0.mean().to_dict()
rd_avg = dp[(dp.draftYear >= 2005) & (dp.draftYear <= 2017)].groupby('roundNumber').exp0.mean().to_dict()
gm = pd.DataFrame(json.load(open('draft/gm_general-manager-franchise-records.json'))['data']); gm = gm[gm.gameTypeId == 2]
def chair(team, date):
    g = gm[(gm.teamId == team) & (gm.startDate <= date) & (gm.endDate >= date)]
    return g.sort_values('startDate').fullName.iloc[-1] if len(g) else None
def tri_of(team, year):
    for y in (year, year - 1, year + 1, year - 2, year + 2):
        if (y, team) in tri: return tri[(y, team)]
def player_val(pid, team, date):
    y0 = int(date[:4]) if int(date[5:7]) >= 6 else int(date[:4]) - 1; v = 0.0; seen = False
    for y in range(y0, y0 + 7):
        w = W.get((pid, y, team))
        if w is None:
            if seen: break
            if y > y0 + 1: break
            continue
        seen = True; v += w
    return v
def pick_val(a, team, other, date):
    # a conditional pick, or one we cannot place, is worth what its round usually returns
    avg = rd_avg.get(min(a['round'], 7), 0.1)
    if a.get('cond') or not a['year'] or a['round'] > 7: return avg, False
    if a.get('ov') and a['ov'] in SLOT: return float(SLOT[a['ov']]), True
    mine = tri_of(team, a['year'])
    if a['orig']:
        c = PK.get((a['year'], a['round'], tri_of(a['orig'], a['year'])))
        if c: return float(np.mean([x[0] for x in c])), True
        return avg, False
    # no owner given: the sender's own pick, but only if the record shows it passed through the acquiring club
    c = [x for x in PK.get((a['year'], a['round'], tri_of(other, a['year'])), []) if mine and mine in x[1].split('-')]
    if c: return float(np.mean([x[0] for x in c])), True
    return avg, False
rows = []; res = tot = 0
for t in T:
    s = t['sides']
    if not s[0]['team'] or not s[1]['team']: continue
    vals = []
    for i in (0, 1):
        v = 0.0; names = []
        for a in s[i]['gets']:
            if a['k'] == 'player' and a['id']: x = player_val(a['id'], s[i]['team'], t['date']); v += x; names.append((a['name'], x))
            elif a['k'] == 'pick':
                x, ok = pick_val(a, s[i]['team'], s[1 - i]['team'], t['date']); v += x; tot += 1; res += ok
        vals.append((v, names))
    for i in (0, 1):
        best = max(vals[i][1], key=lambda z: z[1], default=('picks', 0))[0]
        rows.append({'date': t['date'], 'season': t['season'], 'team': s[i]['team'], 'club': s[i]['teamName'], 'other': s[1 - i]['teamName'], 'got': vals[i][0], 'gave': vals[1 - i][0], 'net': vals[i][0] - vals[1 - i][0], 'star': best, 'gm': chair(s[i]['team'], t['date'])})
d = pd.DataFrame(rows); d.to_pickle('trade_sides.pkl')
if __name__ == '__main__':
    print('trades valued', len(d) // 2, '| picks tied to an actual selection', res, 'of', tot, '| sides with no chair found', int(d.gm.isna().sum()))
    done = d[d.date <= '2022-06-30']; f = lambda r: f"{r.club} from {r.other} {r.date[:7]} ({r.star}) {r.net:+.1f}"
    print('\nbiggest wins:', '; '.join(f(r) for r in done.sort_values('net', ascending=False).head(12).itertuples()))
    g = done.dropna(subset=['gm']).groupby('gm').agg(net=('net', 'sum'), n=('net', 'size')).reset_index(); g = g[g.n >= 25]; g['per'] = g.net / g.n
    print('\ngeneral managers, 25+ trades, net wins in total (per trade): top:', '; '.join(f"{r.gm} {r.net:+.0f} ({r.per:+.2f}, {r.n})" for r in g.sort_values('net', ascending=False).head(8).itertuples()))
    print('bottom:', '; '.join(f"{r.gm} {r.net:+.0f} ({r.per:+.2f}, {r.n})" for r in g.sort_values('net').head(8).itertuples()))
    h = done.dropna(subset=['gm']).sort_values('date'); pairs = []
    for nme, x in h.groupby('gm'):
        if len(x) >= 30: k = len(x) // 2; pairs.append((x.net.iloc[:k].mean(), x.net.iloc[k:].mean()))
    pairs = np.array(pairs); print('\ndo trade results repeat? general managers with 30+ trades: n%d, first half against second half r = %.2f' % (len(pairs), np.corrcoef(pairs[:, 0], pairs[:, 1])[0, 1]))
    odd = [(x.net.iloc[::2].mean(), x.net.iloc[1::2].mean()) for _, x in h.groupby('gm') if len(x) >= 30]; odd = np.array(odd); print('alternating trades (same years, different deals): r = %.2f' % np.corrcoef(odd[:, 0], odd[:, 1])[0, 1])
    print('spread of a single side: sd %.1f wins; share of sides within one win: %.2f' % (done.net.std(), (done.net.abs() < 1).mean()))
