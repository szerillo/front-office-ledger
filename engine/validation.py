"""
VALIDATION + PREDICTIVE POWER: the two questions a front office asks first.

1. ACCOUNTING VALIDATION: WAR-class metrics must sum to team record.
   For every team-season 2015-2025, sum Ledger WAR v1 across the roster and
   compare to actual wins above a 48-win replacement baseline (scaled to
   games played). Reports correlation, R^2, slope, and MAE in wins. This is
   internal and fully reproducible: no proprietary metric is consulted.

2. PREDICTIVE POWER: does decision quality (FOR) carry information about
   FUTURE on-field results beyond the current record? Pooled regime-year
   design: for every regime-year t with >= 2 seasons in office and >= 2
   seasons remaining, predict W% over t+1..t+2 from (a) W% through t alone,
   and (b) W% through t plus cumulative net decision value per season
   through t. Reports the coefficient on decision value, the correlation of
   decision value with future W% after partialling out current W%, and the
   out-of-sample-ish R^2 gain. ~150 pooled observations; standard errors are
   optimistic because regime-years overlap, disclosed.

Writes validation.json for the methodology page.
"""
import json, math, time, urllib.request
from collections import defaultdict

def get(u, tries=3):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception: time.sleep(2 + 2*a)
    return {}

LVM = {k: v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}

# ---- 1. accounting validation ----
team_season = defaultdict(float)
for pid, rec in LVM.items():
    for (y, tm, v) in rec.get("rows", []):
        if 2015 <= y <= 2025:
            team_season[(tm, y)] += v

wl = {}
API = "https://statsapi.mlb.com/api/v1"
for yr in range(2015, 2026):
    d = get(f"{API}/standings?leagueId=103,104&season={yr}&standingsTypes=regularSeason")
    for g in d.get("records", []):
        for t in g.get("teamRecords", []):
            wl[(t["team"]["name"], yr)] = (t.get("wins", 0), t.get("losses", 0))

def find_wl(tm, y):
    if (tm, y) in wl: return wl[(tm, y)]
    for (nm, yy), v in wl.items():
        if yy == y and tm.endswith(nm): return v
    return None

xs, ys = [], []
for (tm, y), lvm in team_season.items():
    hit = find_wl(tm, y)
    if not hit: continue
    w, l = hit
    if w + l < 50: continue
    war_truth = w - 48.0 * (w + l) / 162.0
    xs.append(lvm); ys.append(war_truth)

n = len(xs)
mx, my = sum(xs)/n, sum(ys)/n
cov = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / n
vx = sum((a-mx)**2 for a in xs) / n
vy = sum((b-my)**2 for b in ys) / n
r = cov / math.sqrt(vx * vy)
slope = cov / vx
mae = sum(abs(a - b) for a, b in zip(xs, ys)) / n
acct = dict(n=n, r=round(r, 3), r2=round(r*r, 3), slope=round(slope, 3),
            mae=round(mae, 2), mean_lvm=round(mx, 1), mean_truth=round(my, 1))
print("ACCOUNTING:", acct)

# ---- 2. predictive power (v2: pooled active + archive, grouped CV, cluster bootstrap) ----
"""
Design: every regime-year t with >= 2 seasons in office and >= 2 observable
future seasons UNDER THE SAME REGIME, pooled across the 30 active and the
archive regimes (1998-2024). Predict W% over t+1..t+2 from (a) W% through t,
and (b) W% through t plus net decision value per season through t. Rigor:
  - grouped 5-fold cross-validation (folds split by REGIME, never by year,
    so no regime appears in both train and test): out-of-sample R2 gain.
  - cluster bootstrap (resample regimes with replacement, B = 2000): 95%
    percentile CI on the partial correlation. Overlapping regime-years make
    naive p-values optimistic; the cluster bootstrap is the honest interval.
"""
import random
res = json.load(open("/home/claude/sweep_results.json"))
hres = json.load(open("/home/claude/hist_results.json"))
cfg = json.load(open("/home/claude/regimes.json"))
NAME_BY_TID = {}
for yr in range(1998, 2027):
    d = get(f"{API}/standings?leagueId=103,104&season={yr}&standingsTypes=regularSeason")
    for g in d.get("records", []):
        for t in g.get("teamRecords", []):
            NAME_BY_TID[(t["team"]["id"], yr)] = (t.get("wins", 0), t.get("losses", 0))

obs = []
def add_obs(reg, gid, end_year):
    tid = reg["teamId"]; y0 = reg["start"]
    cum = reg.get("cum") or []
    years = list(range(y0, y0 + len(cum)))
    for i, t in enumerate(years):
        k = t - y0 + 1
        if k < 2: continue
        if t + 2 > end_year: continue          # future must stay inside the regime
        fut = [NAME_BY_TID.get((tid, yy)) for yy in (t+1, t+2)]
        fut = [f for f in fut if f and f[0] + f[1] >= 50]
        if len(fut) < 2: continue
        cur = [NAME_BY_TID.get((tid, yy)) for yy in range(y0, t+1)]
        cur = [c for c in cur if c and c[0] + c[1] >= 50]
        if not cur: continue
        wpct_now = sum(c[0] for c in cur) / sum(c[0] + c[1] for c in cur)
        wpct_fut = sum(f[0] for f in fut) / sum(f[0] + f[1] for f in fut)
        nps = cum[i] / k
        obs.append((wpct_now, nps, wpct_fut, gid))
for reg in res:
    add_obs(reg, "act-" + str(reg["teamId"]), 2026)
for reg in hres:
    add_obs(reg, reg["id"], reg["end"])

n2 = len(obs)
gids = sorted({o[3] for o in obs})
print(f"pooled regime-years: {n2} across {len(gids)} regimes")

def fit_full(data):
    X = [[1, a, b] for (a, b, _, _) in data]; Y = [c for (_, _, c, _) in data]
    M = [[0.0]*3 for _ in range(3)]; V = [0.0]*3
    for row, y in zip(X, Y):
        for i in range(3):
            V[i] += row[i]*y
            for j in range(3): M[i][j] += row[i]*row[j]
    for i in range(3):
        p = M[i][i]
        if abs(p) < 1e-12: return None
        for j in range(3): M[i][j] /= p
        V[i] /= p
        for k2 in range(3):
            if k2 == i: continue
            f = M[k2][i]
            for j in range(3): M[k2][j] -= f*M[i][j]
            V[k2] -= f*V[i]
    return V
def fit_base(data):
    A = [a for (a, _, _, _) in data]; Y = [c for (_, _, c, _) in data]
    n = len(data); ma, mY = sum(A)/n, sum(Y)/n
    vA = sum((a-ma)**2 for a in A)/n
    if vA < 1e-12: return (mY, 0.0)
    bb = sum((a-ma)*(y-mY) for a, y in zip(A, Y))/n/vA
    return (mY - bb*ma, bb)
def sse(preds, Y): return sum((p-y)**2 for p, y in zip(preds, Y))

# full-sample stats
bf = fit_full(obs); b0, b1, b2 = bf
Y = [c for (_, _, c, _) in obs]
mY = sum(Y)/n2; sst = sum((y-mY)**2 for y in Y)
pred_full = [b0 + b1*a + b2*b for (a, b, _, _) in obs]
aa, bb = fit_base(obs)
pred_base = [aa + bb*a for (a, _, _, _) in obs]
r2_full = 1 - sse(pred_full, Y)/sst
r2_base = 1 - sse(pred_base, Y)/sst

def partial_r_of(data):
    n = len(data)
    A = [a for (a,_,_,_) in data]; B = [b for (_,b,_,_) in data]; Yv = [c for (_,_,c,_) in data]
    ma, mb, my_ = sum(A)/n, sum(B)/n, sum(Yv)/n
    vA = sum((a-ma)**2 for a in A)/n
    if vA < 1e-12: return 0.0
    bya = sum((a-ma)*(y-my_) for a, y in zip(A, Yv))/n/vA
    bba = sum((a-ma)*(b-mb) for a, b in zip(A, B))/n/vA
    ry = [y - (my_ + bya*(a-ma)) for a, y in zip(A, Yv)]
    rb = [b - (mb + bba*(a-ma)) for a, b in zip(A, B)]
    mry, mrb = sum(ry)/n, sum(rb)/n
    num = sum((x-mrb)*(y-mry) for x, y in zip(rb, ry))
    den = math.sqrt(sum((x-mrb)**2 for x in rb) * sum((y-mry)**2 for y in ry))
    return num/den if den else 0.0
partial_r = partial_r_of(obs)

# grouped 5-fold CV (folds by regime)
random.seed(14)
gshuf = gids[:]; random.shuffle(gshuf)
folds = [set(gshuf[i::5]) for i in range(5)]
sse_b = sse_f = 0.0; sst_cv = 0.0; held = 0
for f in folds:
    train = [o for o in obs if o[3] not in f]
    test = [o for o in obs if o[3] in f]
    if not test or len(train) < 20: continue
    bfit = fit_base(train); ffit = fit_full(train)
    if ffit is None: continue
    Yt = [c for (_,_,c,_) in test]
    myt = sum(y for (_,_,y,_) in train)/len(train)
    sse_b += sse([bfit[0] + bfit[1]*a for (a,_,_,_) in test], Yt)
    sse_f += sse([ffit[0] + ffit[1]*a + ffit[2]*b for (a,b,_,_) in test], Yt)
    sst_cv += sum((y-myt)**2 for y in Yt); held += len(test)
oos_r2_base = 1 - sse_b/sst_cv
oos_r2_full = 1 - sse_f/sst_cv

# cluster bootstrap on partial r (resample regimes)
bygid = defaultdict(list)
for o in obs: bygid[o[3]].append(o)
B = 2000; prs = []
for _ in range(B):
    samp = []
    for g in random.choices(gids, k=len(gids)):
        samp.extend(bygid[g])
    prs.append(partial_r_of(samp))
prs.sort()
ci_lo, ci_hi = prs[int(0.025*B)], prs[int(0.975*B)]

pred = dict(n=n2, regimes=len(gids), coef_decision_value=round(b2, 5), coef_wpct=round(b1, 3),
            r2_base=round(r2_base, 3), r2_full=round(r2_full, 3),
            r2_gain=round(r2_full - r2_base, 3), partial_r=round(partial_r, 3),
            partial_r_ci=[round(ci_lo, 3), round(ci_hi, 3)], boot_B=B,
            oos_r2_base=round(oos_r2_base, 3), oos_r2_full=round(oos_r2_full, 3),
            oos_gain=round(oos_r2_full - oos_r2_base, 3), cv="grouped 5-fold by regime")
print("PREDICTIVE v2:", pred)

json.dump(dict(accounting=acct, predictive=pred), open("/home/claude/validation.json", "w"), indent=1)
print("wrote validation.json")
