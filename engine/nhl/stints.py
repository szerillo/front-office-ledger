# Five-on-five stints: every stretch of a game with the same ten skaters on the ice, with what each side
# generated in it (expected goals, shot attempts, goals). One npz per season under stints/. Resumable.
import gzip, json, os, sys, time, numpy as np, pandas as pd
T0 = time.time(); BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 540
os.makedirs('stints', exist_ok=True)
goalies = set(pd.read_pickle('go.pkl').playerId.unique())
sh = pd.read_pickle('shots.pkl')[['game', 'season', 'per', 'sec', 'team', 'type']]
xg = pd.read_pickle('xg.pkl')[['xg']]; sh = sh.join(xg); sh['xg'] = sh.xg.fillna(0.0)
for y in range(2010, 2026):
    fn = f'stints/{y}.npz'
    if os.path.exists(fn): continue
    ev = {k: v for k, v in sh[sh.season == y].groupby('game')}
    out = {k: [] for k in ('game', 'dur', 'H', 'A', 'xh', 'xa', 'ch', 'ca', 'gh', 'ga')}
    with gzip.open(f'pbp/{y}.jsonl.gz', 'rt') as f:
        for line in f:
            g = json.loads(line)
            if g.get('none') or len(g['sh']) < 300: continue
            S = np.array([s for s in g['sh'] if s[3] is not None and s[4] is not None and s[4] > s[3] and s[2] <= 3], dtype=np.int64)
            if not len(S): continue
            e = ev.get(g['id']); isg = np.isin(S[:, 0], list(goalies)); home = S[:, 1] == g['home']
            for per in (1, 2, 3):
                m = S[:, 2] == per; s = S[m]; gk = isg[m]; hm = home[m]
                if not len(s): continue
                times = np.unique(np.concatenate([s[:, 3], s[:, 4]])); a, b = times[:-1], times[1:]; mid = (a + b) / 2.0
                on = (s[None, :, 3] < mid[:, None]) & (s[None, :, 4] > mid[:, None])
                nh, na = (on & (hm & ~gk)[None]).sum(1), (on & (~hm & ~gk)[None]).sum(1); ngh, nga = (on & (hm & gk)[None]).sum(1), (on & (~hm & gk)[None]).sum(1)
                ok = np.where((nh == 5) & (na == 5) & (ngh == 1) & (nga == 1))[0]
                if not len(ok): continue
                xh = np.zeros(len(a)); xa = np.zeros(len(a)); ch = np.zeros(len(a), int); ca = np.zeros(len(a), int); gh = np.zeros(len(a), int); ga = np.zeros(len(a), int)
                if e is not None:
                    ep = e[e.per == per]
                    if len(ep):
                        idx = np.clip(np.searchsorted(times, ep.sec.values, side='left') - 1, 0, len(a) - 1); ish = (ep.team.values == g['home'])
                        np.add.at(xh, idx[ish], ep.xg.values[ish]); np.add.at(xa, idx[~ish], ep.xg.values[~ish]); np.add.at(ch, idx[ish], 1); np.add.at(ca, idx[~ish], 1)
                        gl = ep.type.values == 'g'; np.add.at(gh, idx[ish & gl], 1); np.add.at(ga, idx[~ish & gl], 1)
                ids = s[:, 0]
                for i in ok:
                    o = on[i]; out['H'].append(np.sort(ids[o & hm & ~gk])); out['A'].append(np.sort(ids[o & ~hm & ~gk]))
                out['game'] += [g['id']] * len(ok); out['dur'] += list(b[ok] - a[ok])
                for k, v in (('xh', xh), ('xa', xa), ('ch', ch), ('ca', ca), ('gh', gh), ('ga', ga)): out[k] += list(v[ok])
    np.savez_compressed(fn, game=np.array(out['game']), dur=np.array(out['dur'], dtype=np.int16), H=np.array(out['H'], dtype=np.int32), A=np.array(out['A'], dtype=np.int32),
                        xh=np.array(out['xh'], dtype=np.float32), xa=np.array(out['xa'], dtype=np.float32), ch=np.array(out['ch'], dtype=np.int16), ca=np.array(out['ca'], dtype=np.int16), gh=np.array(out['gh'], dtype=np.int8), ga=np.array(out['ga'], dtype=np.int8))
    d = np.array(out['dur']); print(y, 'stints', len(d), 'hours of 5v5 %.0f' % (d.sum() / 3600), 'xG per 60: %.2f' % ((np.sum(out['xh']) + np.sum(out['xa'])) / d.sum() * 3600 / 2), 'goals per 60 %.2f' % ((np.sum(out['gh']) + np.sum(out['ga'])) / d.sum() * 3600 / 2), int(time.time() - T0), flush=True)
    if time.time() - T0 > BUDGET: break
