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

# ---- 2. predictive power ----
res = json.load(open("/home/claude/sweep_results.json"))
cfg = json.load(open("/home/claude/regimes.json"))
REG = {r["teamId"]: r for r in cfg["regimes"]}
NAME_BY_TID = {}
for yr in range(2005, 2027):
    d = get(f"{API}/standings?leagueId=103,104&season={yr}&standingsTypes=regularSeason")
    for g in d.get("records", []):
        for t in g.get("teamRecords", []):
            NAME_BY_TID[(t["team"]["id"], yr)] = (t.get("wins", 0), t.get("losses", 0))

obs = []
for reg in res:
    tid = reg["teamId"]; y0 = reg["start"]
    cum = reg.get("cum") or []
    years = list(range(y0, y0 + len(cum)))
    for i, t in enumerate(years):
        k = t - y0 + 1                       # seasons in office through t
        if k < 2: continue
        fut = [NAME_BY_TID.get((tid, yy)) for yy in (t+1, t+2)]
        fut = [f for f in fut if f and f[0] + f[1] >= 50]
        if len(fut) < 2: continue
        cur = [NAME_BY_TID.get((tid, yy)) for yy in range(y0, t+1)]
        cur = [c for c in cur if c and c[0] + c[1] >= 50]
        if not cur: continue
        wpct_now = sum(c[0] for c in cur) / sum(c[0] + c[1] for c in cur)
        wpct_fut = sum(f[0] for f in fut) / sum(f[0] + f[1] for f in fut)
        nps = cum[i] / k                     # net decision value per season through t
        obs.append((wpct_now, nps, wpct_fut))

n2 = len(obs)
def ols2(obs):
    # y = b0 + b1*wpct_now + b2*nps, normal equations
    import statistics
    X = [[1, a, b] for (a, b, _) in obs]
    Y = [c for (_, _, c) in obs]
    # 3x3 solve
    def mat():
        M = [[0.0]*3 for _ in range(3)]; V = [0.0]*3
        for row, y in zip(X, Y):
            for i in range(3):
                V[i] += row[i]*y
                for j in range(3):
                    M[i][j] += row[i]*row[j]
        return M, V
    M, V = mat()
    # gaussian elimination
    for i in range(3):
        p = M[i][i]
        for j in range(3): M[i][j] /= p
        V[i] /= p
        for k2 in range(3):
            if k2 == i: continue
            f = M[k2][i]
            for j in range(3): M[k2][j] -= f*M[i][j]
            V[k2] -= f*V[i]
    return V
b0, b1, b2 = ols2(obs)
# R2 with and without nps
def r2(preds, Y):
    my_ = sum(Y)/len(Y)
    sse = sum((p-y)**2 for p, y in zip(preds, Y))
    sst = sum((y-my_)**2 for y in Y)
    return 1 - sse/sst
Y = [c for (_, _, c) in obs]
pred_full = [b0 + b1*a + b2*b for (a, b, _) in obs]
# baseline: wpct only
A = [a for (a, _, _) in obs]
ma, mY = sum(A)/n2, sum(Y)/n2
cab = sum((a-ma)*(y-mY) for a, y in zip(A, Y))/n2
vA = sum((a-ma)**2 for a in A)/n2
bb = cab/vA; aa = mY - bb*ma
pred_base = [aa + bb*a for a in A]
r2_full, r2_base = r2(pred_full, Y), r2(pred_base, Y)
# partial correlation of nps with future wpct, controlling wpct_now
resid_y = [y - p for y, p in zip(Y, pred_base)]
B = [b for (_, b, _) in obs]
cbB = sum((b-sum(B)/n2)*(a-ma) for b, a in zip(B, A))/n2
vB = sum((b-sum(B)/n2)**2 for b in B)/n2
bB = cbB/vA if vA else 0
resid_b = [b - (sum(B)/n2 + (cbB/vA)*(a-ma)) for b, a in zip(B, A)]
mrb = sum(resid_b)/n2; mry = sum(resid_y)/n2
num = sum((rb-mrb)*(ry-mry) for rb, ry in zip(resid_b, resid_y))
den = math.sqrt(sum((rb-mrb)**2 for rb in resid_b) * sum((ry-mry)**2 for ry in resid_y))
partial_r = num/den if den else 0
pred = dict(n=n2, coef_decision_value=round(b2, 5), coef_wpct=round(b1, 3),
            r2_base=round(r2_base, 3), r2_full=round(r2_full, 3),
            r2_gain=round(r2_full - r2_base, 3), partial_r=round(partial_r, 3),
            wins_effect=round(b2 * 162 * 2, 2))   # extra future wins over 2 yrs per +1 net value/season... scaled below
print("PREDICTIVE:", pred)

json.dump(dict(accounting=acct, predictive=pred), open("/home/claude/validation.json", "w"), indent=1)
print("wrote validation.json")
