"""
FA CHANNEL GRADING: contracts meet the ledger.
Sources: ESPN free-agent tables 2006-2021 (contracts_espn.csv, 1,506 signed
deals) + curated majors for the 2022-2024 winters (contracts_recent.py,
verify pass pending). 2025-26 winter ungraded (season in progress).

Rule (documented): for a matched signing, implied wins = sum over elapsed
contract seasons of AAV / $-per-win(season); realized = LVM on the signing
org over those seasons; net = realized - implied. Traded-away or released
players keep accruing 'paid' but stop accruing 'realized' on your ledger,
which is the honest cost of a bad signing. Unmatched major-league signings
(depth deals below reporting radar, name mismatches) stay ungraded and are
counted. A regime's FA channel gets a letter only when >= 8 signings
matched; below that it stays pending.
"""
import csv, json, sqlite3
from collections import defaultdict
from contracts_recent import RECENT
from contracts_ext import QO, FA_CBT
from fa_grade_lib import norm, DPW

QO_CHARGE = 1.0  # wins: draft-comp forfeited signing a QO'd free agent
                 # (second-round-pick value on our pick curve; flat v1)

cfg = json.load(open("/home/claude/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
ABBR2TID = {r["abbr"]: r["teamId"] for r in cfg["regimes"]}
LVM = {k: v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}

# contracts: key (player_norm, offseason) -> (tid, years, total)
contracts = defaultdict(list)
def short_to_tid(short):
    for r in cfg["regimes"]:
        names = ALIAS.get(r["teamId"], {r["team"]})
        if any(short and short.lower() in nm.lower() for nm in names):
            return r["teamId"]
    return None
with open("/home/claude/contracts_espn.csv") as f:
    for row in csv.DictReader(f):
        tid = short_to_tid(row["to_team"])
        if tid: contracts[(row["player_norm"], int(row["offseason"]))].append(
            (tid, int(row["years"]), float(row["total_m"]), "espn"))
for off, pl, ab, yrs, tot in RECENT:
    contracts[(norm(pl), off)].append((ABBR2TID[ab], yrs, float(tot), "curated"))
print(f"contract book: {sum(len(v) for v in contracts.values())} deals")

con = sqlite3.connect("/home/claude/ledger.sqlite"); con.row_factory = sqlite3.Row
res = json.load(open("/home/claude/sweep_results.json"))

def grade(nps):
    for thr, g in [(2.6,80),(1.8,75),(1.2,70),(0.8,65),(0.5,60),(0.2,55),
                   (-0.2,50),(-0.6,45),(-1.0,40),(-1.6,35)]:
        if nps >= thr: return g
    return 30
def grade_comp(nps):
    for thr, g in [(8.0,80),(5.5,75),(3.5,70),(2.2,65),(1.2,60),(0.4,55),
                   (-0.4,50),(-1.2,45),(-2.2,40),(-3.5,35)]:
        if nps >= thr: return g
    return 30

print(f"\n{'team':<5}{'FA net':>8}{'matched':>9}{'majors':>8}   best / worst signing")
for r in res:
    tid = r["teamId"]; names = ALIAS.get(tid, {REG[tid]["team"]})
    start = max(REG[tid]["start"], "2005-01-01")
    rows = con.execute("""select date, person_id, person_name from sweep_tx
        where team_id=? and date>=? and type_desc='Signed as Free Agent'
        and lower(description) not like '%minor league%' and person_id is not null""",
        (tid, start)).fetchall()
    seen = set(); majors = []
    for x in rows:
        k = (x["date"], x["person_id"])
        if k not in seen: seen.add(k); majors.append(x)
    net = 0.0; matched = 0; decs = []
    for x in majors:
        pn = norm(x["person_name"]); ty = int(x["date"][:4])
        hit = None
        for off in (ty - 1, ty):
            for (tid2, yrs, tot, src) in contracts.get((pn, off), []):
                if tid2 == tid: hit = (off, yrs, tot, src); break
            if hit: break
        if not hit: continue
        off, yrs, tot, src = hit
        cbt = FA_CBT.get((pn, off))
        aav = (cbt if cbt else tot) / yrs
        seasons = [y for y in range(off + 1, min(off + yrs, 2025) + 1)]
        if not seasons: continue
        implied = sum(aav / DPW[y] for y in seasons)
        rec = LVM.get(x["person_id"])
        realized = sum(v for (y, tm, v) in rec["rows"] if tm in names and y in seasons) if rec else 0.0
        n = realized - implied
        notes = []
        if cbt: notes.append(f"CBT ${cbt:.0f}M used for cost")
        if (pn, off) in QO:
            n -= QO_CHARGE
            notes.append("QO signing, draft comp charged")
        note = (", " + ", ".join(notes)) if notes else ""
        net += n; matched += 1
        fasides = [["Production (LVM on club, elapsed seasons)", [[x["person_name"], f"{realized:+.1f}"]]],
                   ["Contract cost in wins" + (" (QO draft comp included)" if (pn, off) in QO else ""),
                    [[f"${tot:.0f}M over {yrs} yr at market $/win", f"{-(implied + (QO_CHARGE if (pn, off) in QO else 0)):+.1f}"]]]]
        decs.append(dict(d=x["date"], ch="fa", net=round(n, 1),
                         h=f"Signed {x['person_name']} · {yrs} yr / ${tot:.1f}M ({off}-{str(off+1)[2:]} winter, {src}{note})",
                         sides=fasides, pids=[x["person_id"]]))
    covered = matched >= 8
    r["chan"]["fa"] = dict(net=round(net, 1) if covered else 0,
                           g=grade(net / r["seasons"]) if covered else None,
                           n=matched, majors=len(majors),
                           raw=r["chan"]["fa"].get("net", r["chan"]["fa"].get("raw", 0)))
    if covered:
        r["total"] = round(r["total"] + net, 1)
        r["forGrade"] = grade_comp(r["total"] / r["seasons"])
    decs.sort(key=lambda d: -abs(d["net"]))
    r["fa_tops"] = decs[:4]
    r["fa_led"] = dict(best=sorted([d for d in decs if d["net"] > 0], key=lambda x: -x["net"])[:5],
                       worst=sorted([d for d in decs if d["net"] < 0], key=lambda x: x["net"])[:5])
    best = decs[0]["h"][:40] + f" ({decs[0]['net']:+.1f})" if decs else "-"
    worst = min(decs, key=lambda d: d["net"])["net"] if decs else 0
    print(f"{r['abbr']:<5}{(net if covered else 0):>+8.1f}{matched:>9}{len(majors):>8}   {best} / worst {worst:+.1f}")

json.dump(res, open("/home/claude/sweep_results.json", "w"), indent=1)
print("\nmerged graded FA into sweep_results.json")
