# Shift-level skater model: each skater's effect on his club's expected goals for and against per hour at
# five on five, with the other nine skaters on the ice held fixed (ridge regression, one season at a time).
# Usage: python3 rapm.py [lambda in hours]   writes rapm.pkl (player, season, off, def, toi)
import sys, numpy as np, pandas as pd, scipy.sparse as sp
def fit(y, lam, target='x'):
    z = np.load(f'stints/{y}.npz'); H, A, dur = z['H'], z['A'], z['dur'].astype(float)
    th, ta = (z['xh'], z['xa']) if target == 'x' else (z['gh'].astype(float), z['ga'].astype(float)) if target == 'g' else (z['ch'].astype(float), z['ca'].astype(float))
    ids = np.unique(np.concatenate([H.ravel(), A.ravel()])); ix = {p: i for i, p in enumerate(ids)}; n, m = len(ids), len(dur)
    hi = np.vectorize(ix.get)(H); ai = np.vectorize(ix.get)(A); r = np.repeat(np.arange(m), 5)
    # rows 0..m-1: home attacking; rows m..2m-1: away attacking. columns: offence, defence, home edge, intercept
    rows = np.concatenate([r, r, r + m, r + m, np.arange(m), np.arange(2 * m)]); cols = np.concatenate([hi.ravel(), n + ai.ravel(), ai.ravel(), n + hi.ravel(), np.full(m, 2 * n), np.full(2 * m, 2 * n + 1)])
    X = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(2 * m, 2 * n + 2)); w = np.concatenate([dur, dur]) / 3600.0
    yv = np.concatenate([th, ta]) / np.maximum(np.concatenate([dur, dur]), 1) * 3600.0
    XtW = X.T.multiply(w).tocsr(); G = (XtW @ X).toarray(); b = XtW @ yv
    pen = np.full(2 * n + 2, lam); pen[-2:] = 1e-6
    beta = np.linalg.solve(G + np.diag(pen), b)
    toi = np.bincount(np.concatenate([hi.ravel(), ai.ravel()]), weights=np.repeat(np.concatenate([dur, dur]), 5), minlength=n)
    return pd.DataFrame({'playerId': ids, 'season': y, 'off': beta[:n], 'def': beta[n:2 * n], 'toi5': toi}), beta[-2:]
if __name__ == '__main__':
    lam = float(sys.argv[1]) if len(sys.argv) > 1 else 100.0; out = []
    for y in range(2010, 2026):
        d, extra = fit(y, lam); out.append(d); print(y, len(d), 'home edge %.3f base %.2f' % tuple(extra), 'sd off %.3f def %.3f' % (d[d.toi5 > 30000].off.std(), d[d.toi5 > 30000]['def'].std()), flush=True)
    pd.concat(out).to_pickle(f'rapm_{int(lam)}.pkl')
