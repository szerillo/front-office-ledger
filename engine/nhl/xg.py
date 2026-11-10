# Expected goals for every unblocked shot attempt, fitted out of sample: seasons are split into four groups
# and each group is scored by a model that never saw it.
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, log_loss
d = pd.read_pickle('shots.pkl'); u = d[d.type != 'b'].copy()
u['goal'] = (u.type == 'g').astype(int); u['ay'] = u.y.abs()
for c in ('stype', 'prev'): u[c + '_c'] = u[c].astype('category').cat.codes
u['sc'] = u.score.clip(-3, 3)
F = ['dist', 'ang', 'x', 'ay', 'stype_c', 'own', 'oth', 'og', 'gap', 'sameTeam', 'prev_c', 'sc', 'per', 'home']
cat = [F.index('stype_c'), F.index('prev_c')]
u['xg'] = 0.0; fold = (u.season - 2010) % 4
for k in range(4):
    tr, te = u[fold != k], u[fold == k]
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=200, l2_regularization=1.0, categorical_features=cat, random_state=0).fit(tr[F], tr.goal)
    u.loc[te.index, 'xg'] = m.predict_proba(te[F])[:, 1]; print('fold', k, len(te), flush=True)
u[['game', 'season', 'per', 'sec', 'team', 'opp', 'shooter', 'goalie', 'type', 'og', 'own', 'oth', 'xg', 'goal', 'dist']].to_pickle('xg.pkl')
print('unblocked attempts', len(u), 'goals', int(u.goal.sum()), 'expected', round(u.xg.sum()))
print('AUC %.3f  log loss %.4f  (no-model log loss %.4f)' % (roc_auc_score(u.goal, u.xg), log_loss(u.goal, u.xg), log_loss(u.goal, np.full(len(u), u.goal.mean()))))
dist_only = HistGradientBoostingClassifier(max_iter=100).fit(u[fold != 0][['dist']], u[fold != 0].goal); t0 = u[fold == 0]
print('distance alone AUC %.3f on one fold; full model there %.3f' % (roc_auc_score(t0.goal, dist_only.predict_proba(t0[['dist']])[:, 1]), roc_auc_score(t0.goal, t0.xg)))
q = pd.qcut(u.xg, 10, duplicates='drop'); cal = u.groupby(q, observed=True).agg(n=('goal', 'size'), exp=('xg', 'mean'), act=('goal', 'mean'))
print('calibration by tenth (expected, actual):', ' '.join(f"{r.exp:.3f}/{r.act:.3f}" for r in cal.itertuples()))
s = u.groupby('season').agg(exp=('xg', 'sum'), act=('goal', 'sum')); print('by season, actual over expected:', ' '.join(f"{i % 100}:{r.act / r.exp:.3f}" for i, r in s.iterrows()))
