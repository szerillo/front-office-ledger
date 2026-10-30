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
import json, sqlite3
from collections import defaultdict

LVM = {int(k): v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}
cfg = json.load(open("/home/claude/regimes.json"))
hcfg = json.load(open("/home/claude/regimes_hist.json"))
ps = json.load(open("/home/claude/postseason.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
TEAMS = {r["teamId"]: (r["team"], r["abbr"]) for r in cfg["regimes"]}
NAMES = {r["teamId"]: ALIAS.get(r["teamId"], {r["team"]}) for r in cfg["regimes"]}
con = sqlite3.connect("/home/claude/ledger.sqlite"); con.row_factory = sqlite3.Row

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
        if acq and (dr_year is None or acq["date"] >= f"{dr_year}-06-01"):
            d = acq["date"]
            t = acq["type_desc"]
            if t == "Trade": ch = "trade"
            elif t == "Signed as Free Agent":
                ch = "fa"
                if "minor league" in (acq["description"] or "").lower(): ch = "intl"
            else: ch = "intl"
            how = (acq["description"] or t)[:95]
        elif dr_year:
            ch = "draft"; d = f"{dr_year}-06-15"; how = f"Drafted by the club, {dr_year}"
        else:
            # no record in the 2005+ feed and no draft row: amateur signing or pre-floor
            first_club_season = min((y for (y, tm, v) in LVM[pid]["rows"] if tm in names), default=yr)
            if first_club_season >= 1987:
                ch = "intl"; d = f"~{first_club_season - 2}"; how = "Amateur / minor-league signing (no major-league transaction on record)"
            else:
                ch = "inherited"; d = "pre-1985"; how = "Acquired before the 1985 provenance floor (Retrosheet backfill starts 1985)"
        tag = "reg" if (d and not d.startswith("pre") and str(d).lstrip("~") >= tag_start) else "inh"
        if ch == "inherited": tag = "inh"
        bucket = "inherited" if tag == "inh" else ch
        roster.append([nm, ch if ch != "inherited" else "intl", how, str(d), tag, round(w, 1), str(pid)])
    total = sum(r[5] for r in roster)
    mix = defaultdict(float)
    for r in roster:
        mix["inherited" if r[4] == "inh" else r[1]] += r[5]
    reg_share = round(100 * sum(r[5] for r in roster if r[4] == "reg") / total) if total else 0
    tenure_yr = yr - int(reg_start[:4]) + 1
    if true_start: tenure_yr = yr - int(true_start[:4]) + 1
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
        id=f"{abbr.lower()}{str(yr)[2:]}", label=f"{yr} {team}", team=team, year=yr,
        result="Won World Series", regime=reg_exec,
        regimeNote=note,
        computed=True,
        roster=roster))
    agg.append(dict(id=f"{abbr.lower()}{str(yr)[2:]}", yr=yr, team=team, abbr=abbr,
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
    mostHomegrown=max(agg, key=lambda a: share(a, "draft"))["id"],
    mostTraded=max(agg, key=lambda a: share(a, "trade"))["id"],
    rows=agg,
)
print("\nTHROUGH LINES:", {k: v for k, v in lines.items() if k != "rows"})
json.dump(dict(cards=cards, lines=lines), open("/home/claude/champs_computed.json", "w"), indent=1)
print("wrote champs_computed.json")
