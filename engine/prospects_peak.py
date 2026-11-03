"""Prospect peak projections, Phase II (v5.3).

A self-built system on the frameworks the public projection systems
describe, from public MLB Stats API data only:

1. Minor-league translations (Davenport/ZiPS style). Every component is
   first expressed relative to its level-season average (so run environment
   and ball changes wash out), then carried up the ladder by level factors
   learned from players who played at two adjacent levels in the same season
   (A -> A+ -> AA -> AAA -> MLB), weighted by the smaller of the two samples.
   Hitters: strikeout rate, walk rate, isolated power, batting average on
   balls in play, stolen bases per time on base. Pitchers: strikeout rate,
   walk rate, home runs per batter faced.
2. Recent seasons weighted (the current season 5, the prior 3), translated.
3. Comparables (the ZiPS long-term idea): each prospect is matched to his 25
   nearest 2012-2019 prospect-seasons on age, age against level, highest
   level, translated rates, position group (catcher / premium defensive
   spot / corner), and pedigree (draft slot, Top 100 rank at the time).
4. What the comps became is the projection: PEAK = the average of their two
   best MLB seasons of Ledger WAR within eight years (missing seasons count
   zero, so bust risk is inside the number), the odds of a 2-win and a
   4-win peak, the next-season figure, and SIX-SEASON VALUE = their real
   six-season Ledger WAR, the trade currency.
5. Backtest: leave-one-cohort-out over 2013-2019 against the v5.2 level/age/
   production buckets and against Top 100 rank alone.
6. v5.4 Top 100 anchoring (prospect audit, Nov 2026): for a RANKED prospect
   the 100-comp average regressed the elite toward the ranked mean (#1-5 shown
   ~2.8 vs 3.9 realized) and pulled #51-100 toward the unranked pool (0.8 vs
   1.4). Peak / 2-win / 4-win odds for ranked prospects are now
   0.7 x a rank prior (fitted on the ranked history, hitters and pitchers
   apart, x = ln(max(rank, 2)): linear for peak, logistic for the odds)
   + 0.3 x the 25 nearest RANKED comparables. A ranked prospect with no
   minor-league line to match on gets the prior alone. Six-season value,
   next-season WAR and the trajectory still come from the 100 comps (Top 100
   VALUE is the hitter/pitcher rank curve, VR_H / VR_P below).

Writes pros_peak.json.
"""
import json, os, time, math, urllib.request, csv
from collections import defaultdict

ROOT = "/work"
CACHE = f"{ROOT}/milb_cache"; os.makedirs(CACHE, exist_ok=True)
LVM = {int(k): v for k, v in json.load(open(f"{ROOT}/lvm_cache.json")).items() if not k.startswith("__")}
AFF = json.load(open(f"{ROOT}/affiliates.json"))
cfg = json.load(open(f"{ROOT}/regimes.json"))
ABBR = {}
for r in cfg["regimes"]:
    ABBR[r["team"]] = r["abbr"]
    for al in cfg["aliases"].get(str(r["teamId"]), []): ABBR[al] = r["abbr"]
RANKS = defaultdict(dict)
RANK_ROWS = {}                         # v5.4: (year, pid) -> list row (pos, birth date) for prior-only entries
for x in json.load(open(f"{ROOT}/prospect_ranks.json")):
    if x["pid"]: RANKS[x["year"]][int(x["pid"])] = x["rank"]; RANK_ROWS[(x["year"], int(x["pid"]))] = x

SPORT = {1: "MLB", 11: "AAA", 12: "AA", 13: "A+", 14: "A", 15: "A-", 16: "R"}
# v5.3.1: the low minors (complex leagues, the DSL, and pre-2021 short-season A)
LADDER = ["R", "A-", "A", "A+", "AA", "AAA", "MLB"]
TYPICAL = {"R": 19.0, "A-": 20.5, "A": 21.0, "A+": 22.0, "AA": 23.5, "AAA": 25.0, "MLB": 27.0}
LV = {l: i for i, l in enumerate(LADDER)}
YEARS = [y for y in range(2011, 2027) if y != 2020]

def get(u, fn):
    if os.path.exists(fn): return json.load(open(fn))
    for a in range(4):
        try:
            x = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=90))
            json.dump(x, open(fn, "w")); time.sleep(0.3); return x
        except Exception:
            time.sleep(2 + 3 * a)
    return {}

NICK = {}
for r in cfg["regimes"]:
    for nm in {r["team"]} | set(cfg["aliases"].get(str(r["teamId"]), [])):
        for two in ("Red Sox", "White Sox", "Blue Jays"):
            if nm.endswith(two): NICK[two] = r["abbr"]; break
        else: NICK[nm.split()[-1]] = r["abbr"]
NICK["D-backs"] = NICK.get("Diamondbacks"); NICK["Dbacks"] = NICK.get("Diamondbacks")
def parent(team, yr):
    yrs = AFF.get(team)
    if not yrs and team and team.split()[0] in ("DSL", "ACL", "FCL", "GCL", "AZL", "DOSL", "VSL"):
        for k_, v_ in NICK.items():           # complex-league clubs are named for their parent
            if v_ and k_ in team: return v_
        return None
    if not yrs: return None
    if str(yr) in yrs: return ABBR.get(yrs[str(yr)])
    return ABBR.get(yrs[min(yrs, key=lambda y: abs(int(y) - yr))])

def ipf(s):
    s = str(s); i, _, f = s.partition("."); return int(i or 0) + (int(f or 0) / 3)

# ---------- draft pedigree ----------
DRAFT = {}
for yr in range(2005, 2027):
    x = get(f"https://statsapi.mlb.com/api/v1/draft/{yr}", f"{CACHE}/draft_{yr}.json")
    for rd in ((x.get("drafts") or {}).get("rounds") or []):
        for pk in rd.get("picks") or []:
            pid = (pk.get("person") or {}).get("id")
            if pid and pid not in DRAFT: DRAFT[pid] = pk.get("pickNumber") or 999
print("draft picks indexed:", len(DRAFT))

# ---------- raw season lines ----------
def pull(yr):
    """{(pid, kind): {level: aggregated counts}} plus meta"""
    agg = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    meta = {}
    for sid, lvl in SPORT.items():
        for grp in ("hitting", "pitching"):
            x = get(f"https://statsapi.mlb.com/api/v1/stats?stats=season&group={grp}&sportId={sid}&season={yr}&playerPool=ALL&limit=8000",
                    f"{CACHE}/{yr}_{sid}_{grp}.json")
            for sp in ((x.get("stats") or [{}])[0].get("splits") or []):
                st = sp.get("stat", {}); pl = sp.get("player") or {}; pid = pl.get("id")
                if not pid: continue
                team = (sp.get("team") or {}).get("name")
                org = ABBR.get(team) if sid == 1 else parent(team, yr)
                if sid != 1 and not org: continue
                pos = (sp.get("position") or {}).get("abbreviation") or ""
                if grp == "hitting":
                    if pos == "P": continue
                    pa = st.get("plateAppearances", 0) or 0
                    if pa <= 0: continue
                    a = agg[(pid, "H")][lvl]
                    for k_, f_ in (("pa", "plateAppearances"), ("ab", "atBats"), ("h", "hits"), ("d", "doubles"), ("t", "triples"),
                                   ("hr", "homeRuns"), ("bb", "baseOnBalls"), ("hbp", "hitByPitch"), ("so", "strikeOuts"),
                                   ("sf", "sacFlies"), ("sb", "stolenBases")):
                        a[k_] += st.get(f_, 0) or 0
                else:
                    bf = st.get("battersFaced", 0) or 0
                    if bf <= 0: continue
                    a = agg[(pid, "P")][lvl]
                    for k_, f_ in (("bf", "battersFaced"), ("so", "strikeOuts"), ("bb", "baseOnBalls"), ("hr", "homeRuns"),
                                   ("g", "gamesPlayed"), ("gs", "gamesStarted"), ("er", "earnedRuns")):
                        a[k_] += st.get(f_, 0) or 0
                    a["ip"] += ipf(st.get("inningsPitched", 0))
                m = meta.setdefault((pid, "H" if grp == "hitting" else "P"), {})
                m["name"] = pl.get("fullName"); m.setdefault("age", {})[lvl] = st.get("age")
                if sid != 1: m.setdefault("org", {})[lvl] = org
                if grp == "hitting" and pos and pos not in ("P", "PH", "PR"):
                    m.setdefault("pos", defaultdict(float))[pos] += st.get("plateAppearances", 0) or 0
    return agg, meta

def comps_h(a):
    pa = a["pa"]; bip = a["ab"] - a["so"] - a["hr"] + a["sf"]
    tb = a["h"] + a["d"] + 2 * a["t"] + 3 * a["hr"]
    onb = a["h"] + a["bb"] + a["hbp"]
    return dict(k=a["so"] / pa, bb=(a["bb"] + a["hbp"]) / pa, iso=(tb - a["h"]) / max(a["ab"], 1),
                babip=(a["h"] - a["hr"]) / max(bip, 1), sb=a["sb"] / max(onb, 1)), pa
def comps_p(a):
    bf = a["bf"]
    return dict(k=a["so"] / bf, bb=a["bb"] / bf, hr=a["hr"] / bf), bf

DATA = {}
for yr in YEARS:
    DATA[yr] = pull(yr)
    print("pulled", yr, len(DATA[yr][0]), flush=True)

# level-season means, then every line relative to its level-season
REL = {}   # (yr, pid, kind, lvl) -> (rel dict, n)
for yr in YEARS:
    agg, _ = DATA[yr]
    sums = defaultdict(lambda: defaultdict(float))
    for (pid, kind), lv in agg.items():
        for lvl, a in lv.items():
            c, n = (comps_h if kind == "H" else comps_p)(a)
            if n < 30: continue
            for k_, v in c.items(): sums[(kind, lvl)][k_] += v * n
            sums[(kind, lvl)]["_n"] += n
    means = {key: {k_: v / s["_n"] for k_, v in s.items() if k_ != "_n"} for key, s in sums.items()}
    for (pid, kind), lv in agg.items():
        for lvl, a in lv.items():
            c, n = (comps_h if kind == "H" else comps_p)(a)
            m = means.get((kind, lvl))
            if not m or n < 1: continue
            REL[(yr, pid, kind, lvl)] = ({k_: (c[k_] / m[k_] if m[k_] else 1.0) for k_ in c}, n)

# translation factors from same-season pairs at adjacent levels
STEP = {}
for kind in ("H", "P"):
    for i in range(len(LADDER) - 1):
        lo, hi = LADDER[i], LADDER[i + 1]
        num = defaultdict(float); den = defaultdict(float)
        for (yr, pid, k2, lvl), (rel, n) in REL.items():
            if k2 != kind or lvl != lo: continue
            up = REL.get((yr, pid, kind, hi))
            if not up: continue
            w = min(n, up[1])
            if w < 40: continue
            for c in rel:
                if rel[c] > 0 and up[0][c] > 0:
                    num[c] += w * math.log(up[0][c] / rel[c]); den[c] += w
        STEP[(kind, lo)] = {c: math.exp(num[c] / den[c]) if den[c] else 1.0 for c in num}
FACT = {}
for kind in ("H", "P"):
    for lvl in LADDER:
        f = defaultdict(lambda: 1.0)
        for j in range(LV[lvl], len(LADDER) - 1):
            for c, v in STEP.get((kind, LADDER[j]), {}).items(): f[c] *= v
        FACT[(kind, lvl)] = dict(f)
print("translation to MLB (multiplier on level-relative rate):")
for k_, v in FACT.items(): print("  ", k_, {c: round(x, 2) for c, x in v.items()})

def translated(yr, pid, kind):
    """PA-weighted translated line for one season across levels (MiLB only), and the top level"""
    tot = defaultdict(float); n_tot = 0; top = None; ages = []
    for lvl in ("R", "A-", "A", "A+", "AA", "AAA"):
        r = REL.get((yr, pid, kind, lvl))
        if not r: continue
        rel, n = r
        for c, v in rel.items(): tot[c] += v * FACT[(kind, lvl)].get(c, 1.0) * n
        n_tot += n
        if n >= 60 and (top is None or LV[lvl] > LV[top]): top = lvl
    if n_tot == 0: return None
    if top is None:
        top = max((l for l in ("R", "A-", "A", "A+", "AA", "AAA") if REL.get((yr, pid, kind, l))), key=lambda l: LV[l])
    return {c: v / n_tot for c, v in tot.items()}, n_tot, top

def mlb_war(pid):
    rec = LVM.get(int(pid)); by = defaultdict(float)
    for y, t, v in (rec["rows"] if rec else []): by[y] += v
    return by

def pos_group(meta):
    p = meta.get("pos")
    if not p: return 2
    top = max(p, key=p.get)
    return 0 if top == "C" else 1 if top in ("SS", "2B", "3B", "CF") else 2

def prospect_rows(yr):
    agg, meta = DATA[yr]
    prev = DATA.get(yr - 1) or DATA.get(yr - 2)
    out = []
    for (pid, kind), lv in agg.items():
        if "MLB" in lv and ((kind == "H" and lv["MLB"]["pa"] >= 130) or (kind == "P" and lv["MLB"]["ip"] >= 50)): continue
        t = translated(yr, pid, kind)
        if not t: continue
        rel, n, top = t
        if n < (150 if kind == "H" else 120): continue
        m = meta[(pid, kind)]
        age = m["age"].get(top) or next(iter(m["age"].values()))
        if not age or age > 27: continue
        by = mlb_war(pid)
        if sum(abs(v) for y, v in by.items() if y < yr) >= 0.6: continue     # already an MLB player
        # prior season, translated, weight 3 vs 5
        py = yr - 1 if (yr - 1) in DATA else yr - 2
        tp = translated(py, pid, kind) if py in DATA else None
        if tp:
            w1, w0 = 5 * n, 3 * tp[1]
            rel = {c: (rel[c] * w1 + tp[0].get(c, rel[c]) * w0) / (w1 + w0) for c in rel}
        gs = 0
        if kind == "P":
            g = sum(a["g"] for l, a in lv.items() if l != "MLB"); gs = sum(a["gs"] for l, a in lv.items() if l != "MLB")
            gs = gs / g if g else 0
        rk = RANKS.get(yr + 1, {}).get(pid) or RANKS.get(yr, {}).get(pid)
        pick = DRAFT.get(pid)
        a_ = lv[top]
        if kind == "H":
            ab_ = max(a_["ab"], 1); tb_ = a_["h"] + a_["d"] + 2 * a_["t"] + 3 * a_["hr"]
            line = f'{a_["h"]/ab_:.3f}/{(a_["h"]+a_["bb"]+a_["hbp"])/max(a_["ab"]+a_["bb"]+a_["hbp"]+a_["sf"],1):.3f}/{tb_/ab_:.3f}, {int(a_["hr"])} HR, {int(a_["sb"])} SB in {int(a_["pa"])} PA at {top}'.replace("0.", ".")
            pp = m.get("pos") or {}
            ppos = max(pp, key=pp.get) if pp else "OF"
        else:
            line = f'{a_["ip"]:.0f} IP, {9*a_["er"]/max(a_["ip"],1):.2f} ERA, {100*a_["so"]/a_["bf"]:.1f}% K, {100*a_["bb"]/a_["bf"]:.1f}% BB at {top}'
            ppos = "SP" if gs >= 0.5 else "RP"
        out.append(dict(pid=pid, kind=kind, yr=yr, name=m["name"], age=age, lvl=top, n=n, rel=rel, line=line, ppos=ppos,
                        pos=pos_group(m) if kind == "H" else (0 if gs >= 0.5 else 1),
                        rank=rk or 0, pick=pick or 0, org=(m.get("org") or {}).get(top),
                        by=by))
    return out

def feats(r):
    rel = r["rel"]
    lv = LV[r["lvl"]]
    ped_rank = (101 - r["rank"]) / 100 if r["rank"] else 0.0
    ped_pick = max(0.0, 1 - math.log(r["pick"]) / math.log(400)) if r["pick"] else 0.0
    base = [r["age"], r["age"] - TYPICAL[r["lvl"]], lv]
    if r["kind"] == "H":
        return base + [rel["k"], rel["bb"], rel["iso"], rel["babip"], rel.get("sb", 1.0), ped_rank, ped_pick]
    return base + [rel["k"], rel["bb"], rel["hr"], ped_rank, ped_pick]
# feature scales (one unit of distance)
SC_H = [1.5, 1.5, 0.8, 0.12, 0.18, 0.18, 0.09, 0.45, 0.08, 0.12]   # pedigree weighted 3x (backtest)
SC_P = [1.5, 1.5, 0.8, 0.12, 0.15, 0.30, 0.08, 0.12]

def outcome(r):
    by = r["by"]; y0 = r["yr"]
    seasons = [by.get(y0 + k, 0.0) for k in range(1, 9) if y0 + k <= 2026]
    best = sorted(seasons, reverse=True)[:2] + [0.0, 0.0]
    peak = max(0.0, (best[0] + best[1]) / 2)
    # ev6d: the same six seasons discounted 10% a year, the units every
    # surplus figure in the simulator uses (and the Top 100 rank curve)
    return dict(peak=peak, ev6=sum(by.get(y0 + k, 0.0) for k in range(1, 7)), y1=by.get(y0 + 1, 0.0),
                ev6d=sum(by.get(y0 + k, 0.0) * 0.9 ** (k - 1) for k in range(1, 7)),
                traj=[by.get(y0 + k, 0.0) for k in range(1, 7)])          # season by season, for the Horizon

HIST = []
for yr in range(2012, 2020):
    rows = prospect_rows(yr)
    for r in rows: r.update(outcome(r)); r["f"] = feats(r)
    HIST += rows
    print("history cohort", yr, len(rows), flush=True)

import pickle
pickle.dump(HIST, open(f"{ROOT}/milb_cache/hist_rows.pkl", "wb"))
K = 100     # backtested: 25 / 50 / 100 comps, 100 best for unranked prospects
import numpy as np
_MAT = {}
def _mat(pool_key, pool):
    """vectorized history per kind"""
    if pool_key in _MAT: return _MAT[pool_key]
    m = {}
    for kind in ("H", "P"):
        hs = [h for h in pool if h["kind"] == kind]
        m[kind] = dict(h=hs, F=np.array([h["f"] for h in hs], float), pos=np.array([h["pos"] for h in hs]),
                       pid=np.array([h["pid"] for h in hs]), peak=np.array([h["peak"] for h in hs]),
                       rank=np.array([h["rank"] for h in hs]),
                       ev6=np.array([h["ev6"] for h in hs]), y1=np.array([h["y1"] for h in hs]),
                       ev6d=np.array([h["ev6d"] for h in hs]), traj=np.array([h["traj"] for h in hs]))
    _MAT[pool_key] = m
    return m
def project(r, pool, pool_key="all", k=K, ranked_only=False):
    M = _mat(pool_key, pool)[r["kind"]]
    sc = np.array(SC_H if r["kind"] == "H" else SC_P)
    f = np.array(r["f"] if "f" in r else feats(r), float)
    d = np.sqrt((((M["F"] - f) / sc) ** 2).sum(axis=1))
    if r["kind"] == "H":
        pen = np.where(M["pos"] == r["pos"], 0.0, np.where((M["pos"] == 0) | (r["pos"] == 0), 1.2, 0.6))
    else:
        pen = np.where(M["pos"] == r["pos"], 0.0, 0.6)
    d = d + pen
    d[M["pid"] == r["pid"]] = 1e9
    if ranked_only: d[M["rank"] == 0] = 1e9          # v5.4: Top 100 comps come from ranked history only
    # one comp per player (his closest season), as comparables systems do
    nc = min(6 * k, len(d) - 1)
    cand = np.argpartition(d, nc)[:nc]
    cand = cand[np.argsort(d[cand])]
    seen, keep = set(), []
    for i in cand:
        if d[i] >= 1e9: break
        p_ = M["pid"][i]
        if p_ in seen: continue
        seen.add(p_); keep.append(i)
        if len(keep) == k: break
    idx = np.array(keep)
    w = 1 / (0.5 + d[idx]); W = w.sum()
    pk = M["peak"][idx]
    o = np.argsort(pk); cw = np.cumsum(w[o]) / W
    up = float(pk[o][min(len(o) - 1, int(np.searchsorted(cw, 0.8)))])
    return dict(peak=float((w * pk).sum() / W), ev6=float((w * M["ev6"][idx]).sum() / W), y1=float((w * M["y1"][idx]).sum() / W),
                ev6d=float((w * M["ev6d"][idx]).sum() / W),
                traj=[round(float(x), 2) for x in (w[:, None] * M["traj"][idx]).sum(axis=0) / W],
                p2=float(w[pk >= 2].sum() / W), p4=float(w[pk >= 4].sum() / W), up=up,
                comps=[(M["h"][i]["name"], M["h"][i]["yr"], M["h"][i]["lvl"], M["h"][i]["age"], round(M["h"][i]["peak"], 1), round(M["h"][i]["ev6"], 1)) for i in idx[:10]])

# ---------- backtest: leave one cohort out ----------
def corr(a, b):
    n = len(a); ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa and sb else 0
def spear(a, b):
    ra = {i: k for k, i in enumerate(sorted(range(len(a)), key=lambda i: a[i]))}
    rb = {i: k for k, i in enumerate(sorted(range(len(b)), key=lambda i: b[i]))}
    return corr([ra[i] for i in range(len(a))], [rb[i] for i in range(len(b))])
CAL = json.load(open(f"{ROOT}/pros.json"))["calib"]
TYP = TYPICAL
# Top 100 rank curve (six seasons of Ledger WAR, discounted 10% a year).
# v5.4: hitters and pitchers apart, fitted on the ranked 2012-2019 history
# (realized ev6d = a + b ln rank; the old combined curve, VR, ran 1.36x low
# for hitters and 1.16x high for pitchers). Same anchors as desk_data.py
# (vrankH / vrankP), asset_rules.py, sweep_score.py and proj_v1.py.
VR = [[1, 8.0], [3, 7.0], [5, 6.5], [10, 5.5], [15, 4.8], [25, 4.0], [40, 3.2], [50, 2.8], [75, 2.0], [100, 1.5]]   # legacy, combined
VR_H = [[1, 12.4], [3, 10.0], [5, 8.8], [10, 7.3], [15, 6.4], [25, 5.3], [40, 4.2], [50, 3.7], [75, 2.8], [100, 2.2]]
VR_P = [[1, 6.7], [3, 5.5], [5, 4.9], [10, 4.2], [15, 3.7], [25, 3.2], [40, 2.6], [50, 2.4], [75, 2.0], [100, 1.6]]
def vrank(rk, kind=None):
    """log-rank interpolation (the page's dkInterp); kind 'H' / 'P', None = legacy combined curve"""
    a = VR_H if kind == "H" else VR_P if kind == "P" else VR
    if rk <= a[0][0]: return a[0][1]
    if rk >= a[-1][0]: return a[-1][1]
    for (x0, y0), (x1, y1) in zip(a, a[1:]):
        if x0 <= rk <= x1: return y0 + (math.log(rk) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (y1 - y0)
    return a[-1][1]

# ---------- v5.4: Top 100 rank prior for peak and the 2-/4-win odds ----------
W_PRIOR, K_RANKED = 0.7, 25
RBUCK = ((1, 5), (6, 10), (11, 25), (26, 50), (51, 100))
def _logit(X, y, it=60):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        p_ = 1 / (1 + np.exp(-X @ b)); w_ = p_ * (1 - p_) + 1e-9
        b = b + np.linalg.solve(X.T @ (X * w_[:, None]) + 1e-6 * np.eye(len(b)), X.T @ (y - p_))
    return b
def fit_prior(rows):
    """per kind: peak = a + b x (least squares), P(peak>=2), P(peak>=4) logistic in x = ln(max(rank, 2));
    upside = 80th percentile of realized peak in the kind x rank bucket"""
    out = {}
    for kind in ("H", "P"):
        xs = [h for h in rows if h["kind"] == kind and h["rank"]]
        X = np.c_[np.ones(len(xs)), [math.log(max(h["rank"], 2)) for h in xs]]
        pk = np.array([h["peak"] for h in xs])
        up = {}
        for lo, hi in RBUCK:
            v = sorted(h["peak"] for h in xs if lo <= h["rank"] <= hi)
            up[lo] = v[min(len(v) - 1, int(0.8 * len(v)))] if v else 0.0
        out[kind] = dict(peak=np.linalg.lstsq(X, pk, rcond=None)[0], p2=_logit(X, (pk >= 2).astype(float)),
                         p4=_logit(X, (pk >= 4).astype(float)), up=up)
    return out
def prior(pr, kind, rank):
    c = pr[kind]; x = np.array([1.0, math.log(max(rank, 2))])
    lo = next(a for a, b in RBUCK if rank <= b) if rank <= 100 else 51
    return dict(peak=max(0.0, float(x @ c["peak"])), p2=float(1 / (1 + np.exp(-x @ c["p2"]))),
                p4=float(1 / (1 + np.exp(-x @ c["p4"]))), up=float(c["up"][lo]))
def anchored(pr, kind, rank, comps=None):
    """0.7 x rank prior + 0.3 x ranked comps; the prior alone with no comps"""
    p_ = prior(pr, kind, rank)
    if comps is None: return p_
    return {k_: W_PRIOR * p_[k_] + (1 - W_PRIOR) * comps[k_] for k_ in ("peak", "p2", "p4", "up")}
PRIOR = fit_prior(HIST)
print("rank prior (intercept, slope on ln max(rank,2)):",
      {k_: {m_: [round(float(v), 3) for v in PRIOR[k_][m_]] for m_ in ("peak", "p2", "p4")} for k_ in PRIOR},
      "upside by bucket:", {k_: {b: round(v, 2) for b, v in PRIOR[k_]["up"].items()} for k_ in PRIOR})
import numpy as _np
P, R, RK, PK, RPK, BK, KD = [], [], [], [], [], [], []
RB = []     # v5.4: ranked rows: (old 100-comp, new anchored) peak/odds against realized
for yr in range(2013, 2020):
    pool = [h for h in HIST if h["yr"] != yr]
    test = [h for h in HIST if h["yr"] == yr]
    pr_loco = fit_prior(pool)
    for h in test:
        pr = project(h, pool, yr)
        P.append(pr["ev6"]); R.append(h["ev6"]); RK.append(h["rank"]); PK.append(pr["peak"]); RPK.append(h["peak"]); KD.append(h["kind"])
        same = [x["ev6"] for x in pool if x["kind"] == h["kind"] and x["lvl"] == h["lvl"] and abs(x["age"] - h["age"]) <= 0.5]
        BK.append(sum(same) / len(same) if same else 0.4)
        if h["rank"]:
            new = anchored(pr_loco, h["kind"], h["rank"], project(h, pool, yr, k=K_RANKED, ranked_only=True))
            RB.append((h["rank"], h["kind"], pr["peak"], pr["p2"], pr["p4"], new["peak"], new["p2"], new["p4"], h["peak"]))
P, R, RK, PK, RPK, BK = map(_np.array, (P, R, RK, PK, RPK, BK))
ranked = RK > 0
RO = _np.array([vrank(x, k_) if x else 0.41 for x, k_ in zip(RK, KD)])
RO_OLD = _np.array([vrank(x) if x else 0.41 for x in RK])
c = lambda a, b: round(float(_np.corrcoef(a, b)[0, 1]), 3)
BT = dict(n=int(len(R)), n_ranked=int(ranked.sum()),
          unranked=dict(comps_r=c(P[~ranked], R[~ranked]), level_age_bucket_r=c(BK[~ranked], R[~ranked])),
          ranked=dict(comps_r=c(P[ranked], R[ranked]), rank_curve_r=c(RO[ranked], R[ranked]), rank_curve_combined_r=c(RO_OLD[ranked], R[ranked])),
          all=dict(comps_r=c(P, R), bias=round(float(P.mean() - R.mean()), 3)),
          peak=dict(comps_r=c(PK, RPK)))
# Top 100 by level: the rank curve prices a #40 in rookie ball and a #40 in
# Triple-A alike, but the Triple-A player delivers more inside six seasons.
# Level factors (realized / rank-curve, normalized to mean 1) learned with
# each cohort held out, then scored.
LVL = _np.array([LV[h["lvl"]] for yr in range(2013, 2020) for h in HIST if h["yr"] == yr])
YR = _np.array([h["yr"] for yr in range(2013, 2020) for h in HIST if h["yr"] == yr])
band = _np.where(LVL <= LV["A"], 0, _np.where(LVL >= LV["AAA"], 2, 1))
ADJ = RO.copy()
for yr in range(2013, 2020):
    tr = ranked & (YR != yr); te = ranked & (YR == yr)
    tot = R[tr].sum() / RO[tr].sum()
    fac = [(R[tr & (band == b)].sum() / RO[tr & (band == b)].sum()) / tot if (tr & (band == b)).any() else 1.0 for b in range(3)]
    ADJ[te] = RO[te] * _np.array(fac)[band[te]]
tot = R[ranked].sum() / RO[ranked].sum()
LEVEL_FACTOR = {nm: round(float((R[ranked & (band == b)].sum() / RO[ranked & (band == b)].sum()) / tot), 2) for b, nm in enumerate(("low", "mid", "AAA"))}
BT["ranked"]["level_adjusted_rank_curve_r"] = c(ADJ[ranked], R[ranked])
BT["ranked"]["level_factor"] = LEVEL_FACTOR
order = _np.argsort(-P)[:max(1, len(P) // 20)]
BT["top5pct_regular_rate"] = round(float((RPK[order] >= 2).mean()), 3)
BT["base_regular_rate"] = round(float((RPK >= 2).mean()), 3)
# v5.4: ranked peak/odds, old (100 comps) vs anchored (0.7 rank prior + 0.3 x 25 ranked comps), LOCO
RBa = _np.array([x[2:] for x in RB], float); RBr = _np.array([x[0] for x in RB]); RBk = _np.array([x[1] for x in RB])
def _cal(m):
    o = {}
    for lo, hi in RBUCK:
        s_ = m & (RBr >= lo) & (RBr <= hi)
        if s_.any():
            o[f"{lo}-{hi}"] = dict(n=int(s_.sum()), real_peak=round(float(RBa[s_, 6].mean()), 2),
                                   real_p2=round(float((RBa[s_, 6] >= 2).mean()), 3), real_p4=round(float((RBa[s_, 6] >= 4).mean()), 3),
                                   old_peak=round(float(RBa[s_, 0].mean()), 2), old_p2=round(float(RBa[s_, 1].mean()), 3), old_p4=round(float(RBa[s_, 2].mean()), 3),
                                   new_peak=round(float(RBa[s_, 3].mean()), 2), new_p2=round(float(RBa[s_, 4].mean()), 3), new_p4=round(float(RBa[s_, 5].mean()), 3))
    return o
_y4 = (RBa[:, 6] >= 4).astype(float); _y2 = (RBa[:, 6] >= 2).astype(float)
_br = lambda p_, y_: round(float(((p_ - y_) ** 2).mean()), 4)
BT["ranked_peak"] = dict(
    method=f"{W_PRIOR} x rank prior (hitter/pitcher, ln max(rank,2)) + {1 - W_PRIOR:.1f} x {K_RANKED} ranked comps",
    n=len(RB), old_r=c(RBa[:, 0], RBa[:, 6]), new_r=c(RBa[:, 3], RBa[:, 6]),
    old_rmse=round(float(_np.sqrt(((RBa[:, 0] - RBa[:, 6]) ** 2).mean())), 3), new_rmse=round(float(_np.sqrt(((RBa[:, 3] - RBa[:, 6]) ** 2).mean())), 3),
    old_brier_p2=_br(RBa[:, 1], _y2), new_brier_p2=_br(RBa[:, 4], _y2), old_brier_p4=_br(RBa[:, 2], _y4), new_brier_p4=_br(RBa[:, 5], _y4),
    by_bucket=_cal(_np.ones(len(RB), bool)), hitters=_cal(RBk == "H"), pitchers=_cal(RBk == "P"))
print("BACKTEST", json.dumps(BT))

# Top 100 season-by-season shape by rank band (for ranked prospects with no
# 2026 minor-league line to match on): mean realized WAR in years 1..6
RANK_TRAJ = {}
for band, lo, hi in (("1-25", 1, 25), ("26-50", 26, 50), ("51-100", 51, 100)):
    xs = [h["traj"] for h in HIST if lo <= (h["rank"] or 0) <= hi]
    if xs: RANK_TRAJ[band] = [round(sum(t[k] for t in xs) / len(xs), 2) for k in range(6)] + [len(xs)]
print("rank-band trajectories:", RANK_TRAJ)

# ---------- current prospects (2026 season) ----------
cur = prospect_rows(2026)
out = {}
for r in cur:
    r["f"] = feats(r)
    pr = project(r, HIST)
    src = "comps100"
    if r["rank"]:
        # v5.4: a Top 100 prospect's peak and odds are anchored on his rank;
        # value / next season / trajectory stay on the 100 comps
        rc = project(r, HIST, k=K_RANKED, ranked_only=True)
        pr.update(anchored(PRIOR, r["kind"], r["rank"], rc)); pr["comps"] = rc["comps"]
        src = "rank prior 0.7 + ranked comps 0.3"
    out[str(r["pid"])] = dict(name=r["name"], kind=r["kind"], org=r["org"], lvl=r["lvl"], age=r["age"], rank=r["rank"],
                              pick=r["pick"], peak=round(pr["peak"], 2), ev6=round(pr["ev6"], 2), ev6d=round(pr["ev6d"], 2), y1=round(pr["y1"], 2), traj=pr["traj"],
                              p2=round(pr["p2"], 3), p4=round(pr["p4"], 3), up=round(pr["up"], 2), comps=pr["comps"],
                              line=r["line"], pos=r["ppos"], src=src,
                              tr={c: round(v, 2) for c, v in r["rel"].items()})
# v5.4: ranked prospects with no minor-league line to match on (injured,
# not yet playing, or a 2026 MLB look past 130 PA / 50 IP that the page still
# counts a prospect by service time, e.g. Max Clark) get the rank prior alone.
# Everyone on the current list is covered; the page decides who is a prospect.
_ROOK = json.load(open(f"{ROOT}/pros.json"))
n_prior = 0
for pid, rk in RANKS.get(2026, {}).items():
    if str(pid) in out: continue
    rr = RANK_ROWS[(2026, pid)]
    kind = "P" if rr.get("pos") == "P" else "H"
    band = "1-25" if rk <= 25 else "26-50" if rk <= 50 else "51-100"
    lvl = (_ROOK.get("top100Level") or {}).get(str(pid)) or ""
    y1 = ((_ROOK.get("rookie") or {}).get(band) or {}).get(lvl or "AA", [0.2])[0]
    traj = RANK_TRAJ.get(band, [0.0] * 7)[:6]
    pp = prior(PRIOR, kind, rk)
    age = 2026 - int(rr["bd"][:4]) if rr.get("bd") else 0
    out[str(pid)] = dict(name=rr["name"], kind=kind, org=None, lvl=lvl, age=age, rank=rk, pick=DRAFT.get(pid) or 0,
                         peak=round(pp["peak"], 2), ev6=round(sum(traj), 2), ev6d=round(sum(t * 0.9 ** i for i, t in enumerate(traj)), 2),
                         y1=round(y1, 2), traj=traj, p2=round(pp["p2"], 3), p4=round(pp["p4"], 3), up=round(pp["up"], 2), comps=[],
                         line="", pos=None, src="rank prior only", tr={})
    n_prior += 1
print("ranked prospects on the rank prior alone (no minor-league line):", n_prior)
json.dump(dict(players=out, backtest=BT, rankTraj=RANK_TRAJ, factors={f"{k[0]}|{k[1]}": {c: round(v, 3) for c, v in f.items()} for k, f in FACT.items()}),
          open(f"{ROOT}/pros_peak.json", "w"), ensure_ascii=False)
print("current prospects projected:", len(out))
for pid, z in sorted(out.items(), key=lambda kv: -kv[1]["peak"])[:25]:
    print("  ", z["name"], z["org"], z["lvl"], z["age"], "rank", z["rank"], "peak", z["peak"], "ev6", z["ev6"], "p4", z["p4"], [c[0] for c in z["comps"][:3]])
