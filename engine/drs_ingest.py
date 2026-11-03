"""Defensive Runs Saved ingest (Sports Info Solutions, Fielding Bible API).

Per season 2003-2026: /api/v2/fieldingbible/DRS?season=Y (rows per player x
position, with and without a teamId; pos 0 total, 1 P, 2..9 positions,
3456 IF, 789 OF) and /api/v2/fieldingbible/playerTeams?season=Y.

SIS rows carry SIS player ids, not MLBAM ids. Resolution is done once per
SIS player (the id is stable across seasons):
  1. SIS teamId -> MLB club name, learned per season by voting from players
     whose normalized name maps to exactly one Ledger player (LVM cache).
  2. Candidates by normalized name (LVM cache names + sweep_tx feed names,
     same normalization as sdi_ingest.py). A candidate scores one point per
     SIS (season, club) stint that matches an LVM row (same season, club).
     Single candidate: accepted if it has a row in any SIS season.
     Several: highest score wins; ties are left unresolved.
  3. No name hit: fallback on (last name, first initial) with suffixes
     stripped, accepted only with a unique best stint score >= 1.
Only players with innings at C..RF (pos 2..9) are resolved; pitcher DRS is
not part of Ledger WAR.

Output: drs_runs.json
  {pid: {year: {"pos": {"2": drs, ...}, "inn": {"2": innings, ...}, "sz": catcher strike-zone runs}}}
  plus "__unresolved__" (innings-weighted report), "__sis2mlbam__" and
  "__league__" {year: {pos: {"drs", "inn", "sz"}}} (all SIS fielders).
Set DRS_RAW_DIR to cache raw API responses between runs.
"""
import json, os, re, sqlite3, time, urllib.request
from collections import Counter, defaultdict
from fa_grade_lib import norm

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
API = "https://api.sportsinfosolutions.com/api/v2/fieldingbible"
RAW = os.environ.get("DRS_RAW_DIR")
YEARS = range(2003, 2027)

def get_json(url, cache_name, tries=3):
    if RAW:
        p = os.path.join(RAW, cache_name)
        if os.path.exists(p): return json.load(open(p))
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            d = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
            if RAW: json.dump(d, open(os.path.join(RAW, cache_name), "w"))
            time.sleep(1.0)
            return d
        except Exception as e:
            print("  retry", a, e, flush=True); time.sleep(3 + 3 * a)
    return []

def innings(x):
    """SIS innings use baseball notation: 1393.2 = 1393 and 2/3."""
    w = int(x); f = round((x - w) * 10)
    return w + f / 3.0

# ---------------- fetch ----------------
DRS, PT = {}, {}
for y in YEARS:
    DRS[y] = get_json(f"{API}/DRS?season={y}", f"drs_{y}.json")
    PT[y] = get_json(f"{API}/playerTeams?season={y}", f"pt_{y}.json")
    print(y, "DRS rows", len(DRS[y]), "playerTeams", len(PT[y]), flush=True)

# ---------------- Ledger name universe ----------------
LVM = {k: v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
NAME2PIDS = defaultdict(list)
for pid, rec in LVM.items():
    NAME2PIDS[norm(rec.get("name", ""))].append(pid)
con = sqlite3.connect("/work/ledger.sqlite")
for nm, pid in con.execute("select distinct person_name, person_id from sweep_tx where person_id is not null"):
    p = str(pid)
    if p in LVM and p not in NAME2PIDS[norm(nm)]: NAME2PIDS[norm(nm)].append(p)
SUFFIX = re.compile(r"\b(jr|sr|ii|iii|iv)\b")
NICK = {"andy": "andrew", "mike": "michael", "matt": "matthew", "chris": "christopher",
        "nick": "nicholas", "jake": "jacob", "joe": "joseph", "dan": "daniel", "danny": "daniel",
        "tony": "anthony", "zach": "zachary", "alex": "alexander", "rob": "robert", "bob": "robert",
        "jon": "jonathan", "tom": "thomas", "steve": "steven", "will": "william", "ben": "benjamin",
        "sam": "samuel", "greg": "gregory", "jeff": "jeffrey", "josh": "joshua", "dave": "david"}
def nick_keys(n):
    w = norm(n).split()
    out = set()
    if w:
        for a, b in NICK.items():
            if w[0] == a: out.add(" ".join([b] + w[1:]))
            if w[0] == b: out.add(" ".join([a] + w[1:]))
    return out
def short_key(n):
    n = SUFFIX.sub("", norm(n)).split()
    return (n[-1], n[0][0]) if len(n) >= 2 else None
SHORT2PIDS = defaultdict(set)
for nm, pids in NAME2PIDS.items():
    k = short_key(nm)
    if k:
        for p in pids: SHORT2PIDS[k].add(p)
# club names drift (Oakland Athletics / Athletics, Florida / Miami): compare franchises
_cfg = json.load(open("/work/regimes.json"))
FRAN = {}
for _r in _cfg["regimes"]:
    for _n in [_r["team"]] + _cfg["aliases"].get(str(_r["teamId"]), []): FRAN[_n] = _r["teamId"]
LVM_YT = {pid: {(y, FRAN.get(tm, tm)) for (y, tm, v) in rec["rows"]} for pid, rec in LVM.items()}
LVM_Y = {pid: {y for (y, tm, v) in rec["rows"]} for pid, rec in LVM.items()}

# ---------------- per-SIS-player season data ----------------
SIS_NAME = {}
SIS_STINTS = defaultdict(set)          # sis id -> {(year, sisTeamId)}
SEASON = defaultdict(dict)             # sis id -> {year: {"pos":{}, "inn":{}, "sz":x}}
for y in YEARS:
    for r in DRS[y]:
        sid = r["playerId"]; SIS_NAME[sid] = r["player"]
        if "teamId" in r:
            if r["pos"] == 0: SIS_STINTS[sid].add((y, r["teamId"]))
            continue
        p = r["pos"]
        if 2 <= p <= 9:
            s = SEASON[sid].setdefault(y, {"pos": {}, "inn": {}})
            s["pos"][str(p)] = float(r.get("total") or 0)
            s["inn"][str(p)] = innings(float(r.get("inn") or 0))
            if p == 2 and r.get("sz") is not None: s["sz"] = float(r["sz"])
    for r in PT[y]:
        SIS_STINTS[r["playerId"]].add((y, r["teamId"]))

# ---------------- SIS team id -> MLB club name per season ----------------
votes = defaultdict(Counter)
for sid, stints in SIS_STINTS.items():
    cands = NAME2PIDS.get(norm(SIS_NAME.get(sid, "")), [])
    if len(cands) != 1: continue
    rows = LVM[cands[0]]["rows"]
    for (y, t) in stints:
        tms = {tm for (yy, tm, v) in rows if yy == y}
        if len(tms) == 1 and len([1 for (yy, tt) in stints if yy == y]) == 1:
            votes[(y, t)][FRAN.get(next(iter(tms)), next(iter(tms)))] += 1
TEAM = {}
for k, c in votes.items():
    (nm, n), = c.most_common(1)
    if n >= 3 and n >= 0.6 * sum(c.values()): TEAM[k] = nm
bad = [(k, votes[k].most_common(2)) for k in votes if k not in TEAM]
print(f"SIS team map: {len(TEAM)} (season, team) keys; ambiguous: {bad[:5]}")
SIS_TEAM_FRANCHISE = {}
for (y, t), fr in TEAM.items(): SIS_TEAM_FRANCHISE.setdefault(t, Counter())[fr] += 1
print("SIS teamId -> MLB franchise:", {t: c.most_common(1)[0][0] for t, c in sorted(SIS_TEAM_FRANCHISE.items())})

def stint_score(pid, sid):
    yt = LVM_YT.get(pid, set())
    return sum(1 for (y, t) in SIS_STINTS[sid] if TEAM.get((y, t)) and (y, TEAM[(y, t)]) in yt)

# ---------------- resolve ----------------
SIS2PID, how = {}, Counter()
unres = []
for sid, seasons in SEASON.items():
    nm = SIS_NAME[sid]; yrs = set(seasons)
    cands = [p for p in NAME2PIDS.get(norm(nm), []) if LVM_Y.get(p, set()) & yrs]
    if not cands:
        cands = [p for k in nick_keys(nm) for p in NAME2PIDS.get(k, []) if LVM_Y.get(p, set()) & yrs]
    pick = None
    if len(cands) == 1:
        # a lone same-name candidate must still share a club-season with the
        # SIS player (a Giants OF Juan Perez is not the pitcher Juan Pablo Perez)
        if stint_score(cands[0], sid) >= 1: pick = cands[0]; how["name_unique"] += 1
        else: how["name_no_club_fit"] += 1
    elif len(cands) > 1:
        sc = sorted(((stint_score(p, sid), p) for p in cands), reverse=True)
        if sc[0][0] > 0 and sc[0][0] > sc[1][0]:
            pick = sc[0][1]; how["name_team"] += 1
        else: how["name_tie"] += 1
    else:
        k = short_key(nm)
        fc = [p for p in (SHORT2PIDS.get(k, set()) if k else set()) if LVM_Y.get(p, set()) & yrs]
        sc = sorted(((stint_score(p, sid), p) for p in fc), reverse=True)
        if sc and sc[0][0] >= 1 and (len(sc) == 1 or sc[0][0] > sc[1][0]):
            pick = sc[0][1]; how["short_team"] += 1
        else:
            # 4. last name only (B.J. Upton is "Melvin Upton Jr." at SIS): needs
            #    a unique best that matches at least half the SIS club stints
            last = SUFFIX.sub("", norm(nm)).split()[-1:]
            lc = [p for p in LVM if last and SUFFIX.sub("", norm(LVM[p]["name"])).split()[-1:] == last
                  and LVM_Y[p] & yrs]
            sc = sorted(((stint_score(p, sid), p) for p in lc), reverse=True)
            need = max(2, 0.5 * len(SIS_STINTS[sid]))
            if sc and sc[0][0] >= need and (len(sc) == 1 or sc[0][0] > 2 * sc[1][0]):
                pick = sc[0][1]; how["last_team"] += 1
    if pick: SIS2PID[sid] = pick
    else:
        for y, s in seasons.items():
            unres.append((nm, y, sum(s["inn"].values()), sum(s["pos"].values())))

# two SIS ids onto one Ledger player would double count: keep the better stint fit
by_pid = defaultdict(list)
for sid, pid in SIS2PID.items(): by_pid[pid].append(sid)
for pid, sids in by_pid.items():
    if len(sids) > 1:
        keep = max(sids, key=lambda s: (stint_score(pid, s), norm(SIS_NAME[s]) == norm(LVM[pid]["name"])))
        for s in sids:
            if s != keep:
                del SIS2PID[s]; how["dup_dropped"] += 1
                for y, ss in SEASON[s].items():
                    unres.append((SIS_NAME[s], y, sum(ss["inn"].values()), sum(ss["pos"].values())))

zero_fit = [(SIS_NAME[s], LVM[p]["name"], p) for s, p in SIS2PID.items()
            if SIS_STINTS[s] and stint_score(p, s) == 0]
print(f"resolved with no matching club stint (check): {len(zero_fit)} {zero_fit[:15]}")

OUT = {}
for sid, pid in SIS2PID.items():
    for y, s in SEASON[sid].items():
        OUT.setdefault(pid, {})[str(y)] = s

tot_inn = sum(sum(s["inn"].values()) for seasons in SEASON.values() for s in seasons.values())
un_inn = sum(u[2] for u in unres)
by_year = defaultdict(lambda: [0.0, 0.0])
for seasons in SEASON.values():
    for y, s in seasons.items(): by_year[y][0] += sum(s["inn"].values())
for u in unres: by_year[u[1]][1] += u[2]
OUT["__unresolved__"] = dict(
    how=dict(how), sis_players=len(SEASON), resolved=len(SIS2PID),
    innings_share_unresolved=round(un_inn / tot_inn, 5),
    by_year={str(y): round(v[1] / v[0], 5) for y, v in sorted(by_year.items()) if v[0]},
    top=[dict(name=n, year=y, inn=round(i, 1), drs=d) for (n, y, i, d) in sorted(unres, key=lambda u: -u[2])[:60]])
OUT["__sis2mlbam__"] = {str(k): v for k, v in SIS2PID.items()}
# league DRS and innings per (season, position) over ALL SIS fielders
# (resolved or not), so the WAR build can center DRS at zero per position-season
LG = {}
for seasons in SEASON.values():
    for y, s in seasons.items():
        for p, v in s["pos"].items():
            a = LG.setdefault(str(y), {}).setdefault(p, {"drs": 0.0, "inn": 0.0, "sz": 0.0})
            a["drs"] += v; a["inn"] += s["inn"].get(p, 0.0)
            if p == "2": a["sz"] += s.get("sz", 0.0)
OUT["__league__"] = LG
json.dump(OUT, open("/work/drs_runs.json", "w"))
print(f"resolution: {dict(how)}; SIS fielders {len(SEASON)}, resolved {len(SIS2PID)}")
print(f"unresolved innings share {un_inn / tot_inn:.4%}")
for n, y, i, d in sorted(unres, key=lambda u: -u[2])[:25]:
    print(f"  unresolved {n:<28}{y} inn {i:7.1f} drs {d:+.0f}")
