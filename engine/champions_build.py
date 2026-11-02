"""
CHAMPIONS, COMPUTED: roster provenance for every World Series winner
1998-2025, plus cross-title through-lines.

For each title team: core contributors = players with >= 1.0 Ledger WAR v1.5
in the championship season for that club. Each is traced to the club's LAST
acquisition event before the title September (trade / FA signing / waiver or
Rule 5 claim from sweep_tx, or the club's draft pick from draft_picks).
Channel taxonomy matches the Champions tab: fa, trade, draft, intl (int'l or
minor-league find: waiver claims, amateur signings, no-record minor deals),
inherited (acquired before the sitting regime took office). Players acquired
before the 1985 provenance floor (Retrosheet) are tagged to the data floor and
disclosed. The sitting regime comes from regimes.json / regimes_hist.json
(the window containing the title season).

Outputs champs_computed.json: cards (same roster shape the tab renders) and
through-lines aggregated across all 21 titles.
"""
import json
import json, sqlite3
from era_names import era_team, draft_day
from collections import defaultdict

LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
cfg = json.load(open("/work/regimes.json"))
hcfg = json.load(open("/work/regimes_hist.json"))

import os as _os, urllib.request as _ur, time as _t
DRAFT_TERRITORY = {"USA", "Canada", "Puerto Rico", "Guam", "U.S. Virgin Islands", "Virgin Islands",
                   "American Samoa", "Northern Mariana Islands"}
_BFN = "/work/birth.json"
_BIRTH = json.load(open(_BFN)) if _os.path.exists(_BFN) else {}
def birth_country(pid):
    k = str(pid)
    if k not in _BIRTH:
        try:
            d = json.load(_ur.urlopen(f"https://statsapi.mlb.com/api/v1/people/{k}", timeout=30))
            _BIRTH[k] = (d.get("people") or [{}])[0].get("birthCountry") or ""
        except Exception:
            _BIRTH[k] = ""
        json.dump(_BIRTH, open(_BFN, "w")); _t.sleep(0.1)
    return _BIRTH[k]
ps = json.load(open("/work/postseason.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
TEAMS = {r["teamId"]: (r["team"], r["abbr"]) for r in cfg["regimes"]}
NAMES = {r["teamId"]: ALIAS.get(r["teamId"], {r["team"]}) for r in cfg["regimes"]}
con = sqlite3.connect("/work/ledger.sqlite"); con.row_factory = sqlite3.Row

# all regimes (active + archive) per team, with windows
WINDOWS = defaultdict(list)
for r in cfg["regimes"]:
    WINDOWS[r["teamId"]].append((r["start"], "9999-12-31", r["exec"], r.get("trueStart")))
for r in hcfg["regimes"]:
    WINDOWS[r["teamId"]].append((r["start"], r["end"], r["exec"], r.get("trueStart")))

def sitting(tid, date):
    best = None
    for (s, e, ex, ts) in WINDOWS[tid]:
        if s <= date <= e:
            if best is None or s > best[0]: best = (s, ex, ts)
    return best  # (start, exec, trueStart) or None

CHAMPS_WS = sorted([(int(k.split(":")[1]), int(k.split(":")[0]))
                    for k, v in ps.items() if v.get("ws")])

# draft index: pid -> [(year, team)]
DRAFTED = defaultdict(list)
for row in con.execute("select person_id, cast(year as int) y, team from draft_picks where person_id is not null"):
    DRAFTED[str(row["person_id"])].append((row["y"], row["team"]))

# ---- v5.9 provenance resolution (no guessing) ----
# When the feed has no acquisition row, the source is resolved in order:
#  1. the contract book: a free-agent deal with the club and no earlier
#     tenure there (Teixeira, NYY, Dec 2008, 8 yr / $180M)
#  2. CHAMP_PROV: pre-feed acquisitions from the public record
#  3. the Stats API draft: the club's own pick (draftYear + draft/{year})
#  4. the Stats API roster history: first pro assignment in the club's system
#     (an amateur signing by the club)
#  5. otherwise "Acquisition not on file", never a guessed draft pick
from feed_text import clean as feed_clean
CB = json.load(open("/work/contract_book.json"))["book"]
CB_BY = defaultdict(list)
for _c in CB: CB_BY[int(_c["pid"])].append(_c)
CHAMP_PROV = {
    # (pid, club abbr): (channel, date, how). Public record (MLB.com,
    # Baseball Almanac, club histories); the feed starts in 2005.
    (110840, "BOS"): ("trade", "2003-12", "Acquired from the Colorado Rockies in a trade, Dec 2003"),
    (132788, "BOS"): ("trade", "2003-02", "Purchased from the Florida Marlins, Feb 2003"),
    (400083, "SF"):  ("intl", "2008-12", "Signed as a minor-league free agent, Dec 2008 (originally a 1998 Tigers draft pick)"),
    (124288, "NYY"): ("intl", "1985-09", "Signed as an amateur free agent from Puerto Rico, Sep 1985 (before Puerto Rico entered the draft)"),
    (119064, "ARI"): ("trade", "1997-11-18", "Taken from the Minnesota Twins in the Nov 1997 expansion draft"),
    (133340, "NYY"): ("fa", "1998-03-07", "Signed as a free agent after defecting from Cuba, Mar 7 1998 (4 yr / $6.6M)"),
}
_SC = "/work/statsapi_cache"
_os.makedirs(_SC, exist_ok=True)
def _cget(fn, url):
    p = f"{_SC}/{fn}"
    if _os.path.exists(p): return json.load(open(p))
    try:
        d = json.load(_ur.urlopen(_ur.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
    except Exception:
        return None
    json.dump(d, open(p, "w")); _t.sleep(0.1)
    return d
def draft_by_club(pid, tid):
    """(year, round, pick) when the Stats API draft lists him as this club's pick"""
    pp = _cget(f"person_{pid}.json", f"https://statsapi.mlb.com/api/v1/people/{pid}?hydrate=rosterEntries")
    per = ((pp or {}).get("people") or [{}])[0]
    yrs = {per.get("draftYear")} - {None}
    for y in sorted(yrs):
        dd = _cget(f"draft_{y}.json", f"https://statsapi.mlb.com/api/v1/draft/{y}")
        for rd in ((dd or {}).get("drafts") or {}).get("rounds", []):
            for pk in rd.get("picks", []):
                if (pk.get("person") or {}).get("id") == pid and (pk.get("team") or {}).get("id") == tid:
                    return (y, pk.get("pickRound"), pk.get("pickNumber"))
    return None
def first_pro_org(pid):
    """(parent org id, team name, start date) of his first professional assignment"""
    pp = _cget(f"person_{pid}.json", f"https://statsapi.mlb.com/api/v1/people/{pid}?hydrate=rosterEntries")
    per = ((pp or {}).get("people") or [{}])[0]
    ents = sorted((e for e in per.get("rosterEntries", []) if e.get("startDate")), key=lambda e: e["startDate"])
    if not ents: return None
    e = ents[0]; tm = e.get("team") or {}; y = e["startDate"][:4]
    if tm.get("id") in TEAMS: return (tm["id"], tm.get("name"), e["startDate"])
    td = _cget(f"team_{tm.get('id')}_{y}.json", f"https://statsapi.mlb.com/api/v1/teams/{tm.get('id')}?season={y}")
    t0 = ((td or {}).get("teams") or [{}])[0]
    return (t0.get("parentOrgId"), tm.get("name"), e["startDate"])

CH_LABEL = dict(trade="Trade", fa="Free agent signing", draft="Draft",
                intl="Int'l / minor-lg find", inherited="Inherited")

# CONTINUITY LENS (secondary, disclosed): for champions whose sitting exec
# was promoted from the chair immediately below, the share of the core
# acquired while he already sat in that chair. Verified dates:
# Arnold named MIL GM 2020-11-19 (Stearns POBO stayed); Young named TEX GM
# 2020-12-04 (Daniels POBO stayed); Cashman NYY assistant GM from 1992
# (month approximate, flagged). Primary accounting still credits final
# authority; this lens answers "was he in the room".
DEPUTY = {
    ("Matt Arnold", 158): ("2020-11-19", "GM under Stearns' presidency"),
    ("Chris Young", 140): ("2020-12-04", "GM under Daniels' presidency"),
    ("Brian Cashman", 147): ("1992-03-01", "assistant GM (month approximate)"),
}

cards = []
agg = []
for (yr, tid) in CHAMPS_WS:
    team, abbr = TEAMS[tid]; names = NAMES[tid]
    cutoff = f"{yr}-09-15"
    reg = sitting(tid, f"{yr}-06-01")
    reg_start, reg_exec = (reg[0], reg[1]) if reg else ("1900-01-01", "(regime gap)")
    true_start = reg[2] if reg and reg[2] else None
    # the tag cutoff is the regime's TRUE seat date (pre-2005 seats are
    # truncated in the scoring tables but not for provenance attribution)
    tag_start = (true_start + "-01") if true_start and len(true_start) == 7 else (true_start or reg_start)
    # core roster
    core = []
    for pid, rec in LVM.items():
        w = sum(v for (y, tm, v) in rec["rows"] if y == yr and tm in names)
        if w >= 1.0:
            core.append((pid, rec["name"], w))
    core.sort(key=lambda t: -t[2])
    core = core[:16]
    roster = []
    for pid, nm, w in core:
        # last acquisition by this club before the title september
        acq = None
        for x in con.execute(
            "select date, type_desc, description, from_team, to_team from sweep_tx "
            "where person_id=? and date<=? and type_desc in "
            "('Trade','Signed as Free Agent','Claimed Off Waivers','Rule 5 Selection') "
            "order by date desc", (str(pid), cutoff)):
            if x["type_desc"] == "Trade":
                if x["to_team"] in names: acq = x; break
            elif x["to_team"] in names or (not x["to_team"] and x["from_team"] in names):
                acq = x; break
            if x["type_desc"] == "Signed as Free Agent" and x["to_team"] in names:
                acq = x; break
        dr = [t for t in DRAFTED.get(str(pid), []) if t[1] in names and t[0] <= yr]
        dr_year = max((t[0] for t in dr), default=None)
        ch, how, d = None, None, None
        # a free-agent deal with this club and no earlier tenure here (the feed
        # can miss the signing: Teixeira, Dec 2008)
        first_club_season = min((y for (y, tm, v) in LVM[pid]["rows"] if tm in names), default=yr)
        cb_fa = [c for c in CB_BY.get(pid, []) if c["club"] == abbr and c["kind"] == "fa" and c["start"] <= yr
                 and c["start"] <= first_club_season and f'{c["sign"]}-31' <= cutoff]
        cb_fa = max(cb_fa, key=lambda c: c["sign"]) if cb_fa else None
        if cb_fa and acq and acq["date"][:7] >= cb_fa["sign"]: cb_fa = None
        prov = CHAMP_PROV.get((pid, abbr))
        if prov and acq and acq["date"] >= prov[1]: prov = None
        if prov:
            ch, d, how = prov
        elif cb_fa:
            ch = "fa"; d = cb_fa["sign"]
            how = f'Signed as a free agent, {cb_fa["yrs"]} yr / ${cb_fa["tot"]:g}M (contract book, signed {cb_fa["sign"]})'
        elif acq and (dr_year is None or acq["date"] >= f"{dr_year}-06-01"):
            d = acq["date"]
            t = acq["type_desc"]
            # waiver claims and Rule 5 picks count with trades, as the legend says
            if t in ("Trade", "Claimed Off Waivers", "Rule 5 Selection"): ch = "trade"
            elif t == "Signed as Free Agent":
                ch = "fa"
                if "minor league" in (acq["description"] or "").lower():
                    ch = "intl"
                    # a draftee's first contract is a "minor league" signing in
                    # the feed (Brandon Belt 2009, Justin Wrobleski 2021)
                    dbc = draft_by_club(pid, tid)
                    if dbc and dbc[0] == int(d[:4]):
                        ch = "draft"; d = draft_day(dbc[0])
            else: ch = "intl"
            alts = [x["description"] for x in con.execute(
                "select description from sweep_tx where person_id=? and date=? and type_desc=?",
                (str(pid), acq["date"], acq["type_desc"]))]
            how = feed_clean(acq["description"] or t, nm, t, acq["from_team"], acq["to_team"], alts)
            if ch == "draft":
                how = f"Drafted by the club, {dbc[0]} (round {dbc[1]}, pick {dbc[2]}); signed {acq['date']}"
            if len(how) > 140:
                how = how[:140].rsplit(" ", 1)[0].rstrip(",;: ") + "…"
        elif dr_year:
            ch = "draft"; d = draft_day(dr_year); how = f"Drafted by the club, {dr_year}"
        else:
            # no feed row and no draft-table row: resolve from the Stats API
            dbc = draft_by_club(pid, tid)
            fpo = None if dbc else first_pro_org(pid)
            if dbc:
                ch = "draft"; d = draft_day(dbc[0]); how = f"Drafted by the club, {dbc[0]} (round {dbc[1]}, pick {dbc[2]})"
            elif fpo and fpo[0] == tid:
                ch = "intl"; d = fpo[2][:10]; how = f"Came up through the club's system (earliest assignment on file: {fpo[1]}, {fpo[2][:4]})"
            elif first_club_season < 1987:
                ch = "inherited"; d = "pre-1985"; how = "Acquired before the 1985 provenance floor (Retrosheet backfill starts 1985)"
            else:
                ch = "unk"; d = None; how = "Acquisition not on file"
                print("   provenance not on file:", yr, abbr, nm, pid)
        tag = "reg" if (d and not d.startswith("pre") and str(d).lstrip("~") >= tag_start) else "inh"
        if ch == "inherited": tag = "inh"
        if ch == "unk": tag = "unk"
        bucket = "inherited" if tag == "inh" else ch
        roster.append([nm, ch if ch != "inherited" else "intl", how, str(d), tag, round(w, 1), str(pid)])
    total = sum(r[5] for r in roster)
    mix = defaultdict(float)
    for r in roster:
        mix["inherited" if r[4] == "inh" else r[1]] += r[5]
    reg_share = round(100 * sum(r[5] for r in roster if r[4] == "reg") / total) if total else 0
    # v5.1: seasons counted the leaderboard's way: an exec hired after July
    # takes over the NEXT season, so a fall hire's first title year is year 1
    _ts = true_start or reg_start
    _first = int(_ts[:4]) + (1 if _ts[5:7] > "07" else 0)
    tenure_yr = max(1, yr - _first + 1)
    note = f"title in year {tenure_yr} of the regime"
    dep = DEPUTY.get((reg_exec, tid))
    cont_share = None
    if dep:
        dep_date, dep_label = dep
        cont = sum(r[5] for r in roster if r[3] and not r[3].startswith("pre") and r[3].lstrip("~") >= dep_date)
        cont_share = round(100 * cont / total) if total else 0
        note += (f" · continuity view: {cont_share}% of the core was acquired while {reg_exec.split()[-1]} "
                 f"was already {dep_label} (from {dep_date[:7]}); the primary accounting credits final authority")
    cards.append(dict(
        id=f"{abbr.lower()}{str(yr)[2:]}", label=f"{yr} {era_team(team, yr)}", team=era_team(team, yr), year=yr,
        result="Won World Series", regime=reg_exec,
        regimeNote=note,
        computed=True,
        roster=roster))
    agg.append(dict(id=f"{abbr.lower()}{str(yr)[2:]}", yr=yr, team=era_team(team, yr), abbr=abbr,
                    exec=reg_exec, tenure=tenure_yr, total=round(total, 1),
                    regShare=reg_share, contShare=cont_share,
                    mix={k: round(v, 1) for k, v in mix.items()}))
    print(f"{yr} {abbr:<4} {reg_exec:<22} core {total:5.1f} WAR | built-by-regime {reg_share:>3}% | "
          + " ".join(f"{k}:{round(100*v/total)}%" for k, v in sorted(mix.items(), key=lambda t: -t[1])))

# ---- through lines ----
import statistics
def share(a, k): return 100 * a["mix"].get(k, 0) / a["total"] if a["total"] else 0
lines = dict(
    n=len(agg),
    medianRegShare=round(statistics.median(a["regShare"] for a in agg)),
    medianTenure=round(statistics.median(a["tenure"] for a in agg)),
    earlyTitles=sum(1 for a in agg if a["tenure"] <= 3),
    lateTitles=sum(1 for a in agg if a["tenure"] >= 10),
    avgShare={k: round(statistics.mean(share(a, k) for a in agg), 1)
              for k in ("fa", "trade", "draft", "intl", "inherited")},
    majorityFA=[a["id"] for a in agg if share(a, "fa") > 50],
    majorityHomegrown=[a["id"] for a in agg if share(a, "draft") + share(a, "intl") > 50],
    mostInherited=max(agg, key=lambda a: share(a, "inherited"))["id"],
    mostBought=max(agg, key=lambda a: share(a, "fa"))["id"],
    mostHomegrown=max(agg, key=lambda a: share(a, "draft") + share(a, "intl"))["id"],   # same definition as majorityHomegrown
    mostTraded=max(agg, key=lambda a: share(a, "trade"))["id"],
    rows=agg,
)
print("\nTHROUGH LINES:", {k: v for k, v in lines.items() if k != "rows"})
json.dump(dict(cards=cards, lines=lines), open("/work/champs_computed.json", "w"), indent=1)
print("wrote champs_computed.json")
