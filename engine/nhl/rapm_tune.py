# Pick the ridge strength by what carries to the next season, for players who changed clubs and for all.
import sys, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
from rapm import fit
sk = pd.read_pickle('sk.pkl'); one = sk.groupby(['playerId', 'seasonId']).teamId.agg(['nunique', 'first']).reset_index(); one['season'] = one.seasonId // 10000
pos = sk.drop_duplicates('playerId').set_index('playerId').pos
for lam in [float(a) for a in sys.argv[1:]] or [25, 50, 100, 200, 400]:
    d = pd.concat([fit(y, lam)[0] for y in range(2014, 2020)]).merge(one[['playerId', 'season', 'nunique', 'first']], on=['playerId', 'season'])
    d['n'] = d.season + 1; m = d.merge(d, left_on=['playerId', 'n'], right_on=['playerId', 'season'], suffixes=('', '2')); m = m[(m.toi5 >= 30000) & (m.toi52 >= 30000)]; m['net'] = m.off - m['def']; m['net2'] = m.off2 - m.def2
    mv = m[(m['nunique'] == 1) & (m.nunique2 == 1) & (m['first'] != m.first2)]; c = lambda x, k: np.corrcoef(x[k], x[k + '2'])[0, 1]
    mD = m[m.playerId.map(pos) == 'D']
    print(f"lambda {lam:5.0f}: all n{len(m)} off {c(m, 'off'):.2f} def {c(m, 'def'):.2f} net {c(m, 'net'):.2f} | moved n{len(mv)} off {c(mv, 'off'):.2f} def {c(mv, 'def'):.2f} net {c(mv, 'net'):.2f} | defensemen def {c(mD, 'def'):.2f}", flush=True)
