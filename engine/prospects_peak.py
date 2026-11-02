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
for x in json.load(open(f"{ROOT}/prospect_ranks.json")):
    if x["pid"]: RANKS[x["year"]][int(x["pid"])] = x["rank"]

SPORT = {1: "MLB", 11: "AAA", 12: "AA", 13: "A+", 14: "A"}
LADDER = ["A", "A+", "AA", "AAA", "MLB"]
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

def parent(team, yr):
    yrs = AFF.get(team)
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
    for lvl in ("A", "A+", "AA", "AAA"):
        r = REL.get((yr, pid, kind, lvl))
        if not r: continue
        rel, n = r
        for c, v in rel.items(): tot[c] += v * FACT[(kind, lvl)].get(c, 1.0) * n
        n_tot += n
        if n >= 60 and (top is None or LV[lvl] > LV[top]): top = lvl
    if n_tot == 0: return None
    if top is None:
        top = max((l for l in ("A", "A+", "AA", "AAA") if REL.get((yr, pid, kind, l))), key=lambda l: LV[l])
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
    base = [r["age"], r["age"] - (21 + 1.2 * lv), lv]
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
    return dict(peak=peak, ev6=sum(by.get(y0 + k, 0.0) for k in range(1, 7)), y1=by.get(y0 + 1, 0.0))

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
                       ev6=np.array([h["ev6"] for h in hs]), y1=np.array([h["y1"] for h in hs]))
    _MAT[pool_key] = m
    return m
def project(r, pool, pool_key="all"):
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
    # one comp per player (his closest season), as comparables systems do
    cand = np.argpartition(d, 6 * K)[:6 * K]
    cand = cand[np.argsort(d[cand])]
    seen, keep = set(), []
    for i in cand:
        p_ = M["pid"][i]
        if p_ in seen: continue
        seen.add(p_); keep.append(i)
        if len(keep) == K: break
    idx = np.array(keep)
    w = 1 / (0.5 + d[idx]); W = w.sum()
    pk = M["peak"][idx]
    o = np.argsort(pk); cw = np.cumsum(w[o]) / W
    up = float(pk[o][min(len(o) - 1, int(np.searchsorted(cw, 0.8)))])
    return dict(peak=float((w * pk).sum() / W), ev6=float((w * M["ev6"][idx]).sum() / W), y1=float((w * M["y1"][idx]).sum() / W),
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
TYP = {"AAA": 25.0, "AA": 23.5, "A+": 22.0, "A": 21.0}
VR = [[1, 8.0], [3, 7.0], [5, 6.5], [10, 5.5], [15, 4.8], [25, 4.0], [40, 3.2], [50, 2.8], [75, 2.0], [100, 1.5]]
def vrank(rk):
    for (a, va), (b, vb) in zip(VR, VR[1:]):
        if a <= rk <= b: return va + (vb - va) * (rk - a) / (b - a)
    return 1.5
import numpy as _np
P, R, RK, PK, RPK, BK = [], [], [], [], [], []
for yr in range(2013, 2020):
    pool = [h for h in HIST if h["yr"] != yr]
    test = [h for h in HIST if h["yr"] == yr]
    for h in test:
        pr = project(h, pool, yr)
        P.append(pr["ev6"]); R.append(h["ev6"]); RK.append(h["rank"]); PK.append(pr["peak"]); RPK.append(h["peak"])
        same = [x["ev6"] for x in pool if x["kind"] == h["kind"] and x["lvl"] == h["lvl"] and abs(x["age"] - h["age"]) <= 0.5]
        BK.append(sum(same) / len(same) if same else 0.4)
P, R, RK, PK, RPK, BK = map(_np.array, (P, R, RK, PK, RPK, BK))
ranked = RK > 0
RO = _np.array([vrank(x) if x else 0.41 for x in RK])
c = lambda a, b: round(float(_np.corrcoef(a, b)[0, 1]), 3)
BT = dict(n=int(len(R)), n_ranked=int(ranked.sum()),
          unranked=dict(comps_r=c(P[~ranked], R[~ranked]), level_age_bucket_r=c(BK[~ranked], R[~ranked])),
          ranked=dict(comps_r=c(P[ranked], R[ranked]), rank_curve_r=c(RO[ranked], R[ranked])),
          all=dict(comps_r=c(P, R), bias=round(float(P.mean() - R.mean()), 3)),
          peak=dict(comps_r=c(PK, RPK)))
order = _np.argsort(-P)[:max(1, len(P) // 20)]
BT["top5pct_regular_rate"] = round(float((RPK[order] >= 2).mean()), 3)
BT["base_regular_rate"] = round(float((RPK >= 2).mean()), 3)
print("BACKTEST", json.dumps(BT))

# ---------- current prospects (2026 season) ----------
cur = prospect_rows(2026)
out = {}
for r in cur:
    r["f"] = feats(r)
    pr = project(r, HIST)
    out[str(r["pid"])] = dict(name=r["name"], kind=r["kind"], org=r["org"], lvl=r["lvl"], age=r["age"], rank=r["rank"],
                              pick=r["pick"], peak=round(pr["peak"], 2), ev6=round(pr["ev6"], 2), y1=round(pr["y1"], 2),
                              p2=round(pr["p2"], 3), p4=round(pr["p4"], 3), up=round(pr["up"], 2), comps=pr["comps"],
                              line=r["line"], pos=r["ppos"],
                              tr={c: round(v, 2) for c, v in r["rel"].items()})
json.dump(dict(players=out, backtest=BT, factors={f"{k[0]}|{k[1]}": {c: round(v, 3) for c, v in f.items()} for k, f in FACT.items()}),
          open(f"{ROOT}/pros_peak.json", "w"), ensure_ascii=False)
print("current prospects projected:", len(out))
for pid, z in sorted(out.items(), key=lambda kv: -kv[1]["peak"])[:25]:
    print("  ", z["name"], z["org"], z["lvl"], z["age"], "rank", z["rank"], "peak", z["peak"], "ev6", z["ev6"], "p4", z["p4"], [c[0] for c in z["comps"][:3]])
