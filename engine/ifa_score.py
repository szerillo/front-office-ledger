"""
IFA CHANNEL v1: international amateur signings as their own graded channel.

Why it grades cleanly: since 2017 every club shops from a near-equal bonus
pool, so a team's expectation for a signing CLASS (team-year) is simply the
league's realized value from that class divided by the number of clubs
observed shopping it. Beating the class mean is scouting skill, not budget.
Pre-2017 classes carry an "uncapped era" flag (pools were soft).

Classification (automated, documented):
  minor-league FA signing in the feed AND age at signing <= 23 AND born
  outside draft territory (USA/Canada/Puerto Rico/US territories) AND it is
  the person's first appearance in the feed (approximates first pro deal).
  The under-25 pool rule (2017+) is why the age cap sits above 18: Cuban
  and Asian amateur-classified pros land in the pool too.

Scoring: realized = value in the player's six control seasons, wherever he
played them (v5.5 asset accounting; a later trade is graded in the trade);
baseline = league class value over 30 clubs; regime net = sum over classes.
Known gaps: value-relevant signees only (kids without MLB time count as
volume, not value); signing dates are as-filed; posting-system pros with
major-league deals (Ohtani, Yamamoto) are NOT here, they stay in FA-major.

Merges chan.intl into sweep_results.json in place.
"""
import json
from asset_rules import control_value
def grade_comp_ifa(nps):
    for thr, g in [(8.0,80),(5.5,75),(3.5,70),(2.2,65),(1.2,60),(0.4,55),
                   (-0.4,50),(-1.2,45),(-2.2,40),(-3.5,35)]:
        if nps >= thr: return g
    return 30
import sqlite3
from collections import defaultdict
from datetime import date
from ledger_war import get, API

NA_DRAFT = {"USA", "Canada", "Puerto Rico", "Guam", "U.S. Virgin Islands",
            "Virgin Islands", "American Samoa", "Northern Mariana Islands"}

cfg = json.load(open("/work/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
LVM = {k: v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
con = sqlite3.connect("/work/ledger.sqlite"); con.row_factory = sqlite3.Row

rows = [dict(r) for r in con.execute(
    """select team_id, date, person_id, person_name from sweep_tx
       where type_desc='Signed as Free Agent' and lower(description) like '%minor league%'
       and person_id is not null""")]
first_seen = {}
for r in con.execute("select person_id, min(date) d from sweep_tx where person_id is not null group by person_id"):
    first_seen[r["person_id"]] = r["d"]

# v5.6: every minor-league signee, not only those who reached the majors.
# The channel's volume (n) counts every international amateur a regime
# signed; before, only big leaguers counted, so a club whose recent classes
# have not debuted yet (or, like Atlanta 2018-21, signed under MLB sanctions)
# showed one or two signings and no grade.
import os as _os
cands = sorted({r["person_id"] for r in rows})
BIO_P = "/work/ifa_bios.json"
bio = {k: tuple(v) for k, v in json.load(open(BIO_P)).items()} if _os.path.exists(BIO_P) else {}
need = [c for c in cands if c not in bio]
print(f"minor-FA signees: {len(cands)} | bios to fetch: {len(need)}", flush=True)
for i in range(0, len(need), 100):
    chunk = ",".join(need[i:i+100])
    try:
        d = get(f"{API}/people?personIds={chunk}&fields=people,id,birthDate,birthCountry")
    except Exception:
        d = {"people": []}      # an id the API no longer serves sinks the batch; record and move on
    for p in d.get("people", []):
        bio[str(p["id"])] = (p.get("birthDate"), p.get("birthCountry"))
for c in need:
    bio.setdefault(c, (None, None))
json.dump(bio, open(BIO_P, "w"))
print(f"bios: {len(bio)}", flush=True)

def age_at(bd, when):
    b = date.fromisoformat(bd); w = date.fromisoformat(when)
    return (w - b).days / 365.25

# classify + realize
ifa = []  # (team_id, class_year, person_id, name, realized, sign_date)
for r in rows:
    pid = r["person_id"]
    if pid not in bio: continue
    bd, bc = bio[pid]
    if not bd or not bc or bc in NA_DRAFT: continue
    if first_seen.get(pid) != r["date"]: continue      # first pro appearance only
    a = age_at(bd, r["date"])
    if a > 23.0: continue
    tid = r["team_id"]; names = ALIAS.get(tid, {REG[tid]["team"]})
    yr = int(r["date"][:4])
    # v5.5 asset accounting (asset_rules.py): six control seasons, any club;
    # a signee later traded is graded once, in the trade
    realized = control_value(LVM[pid]) if pid in LVM else 0.0
    ifa.append((tid, yr, pid, r["person_name"], round(realized, 2), r["date"]))
print(f"classified IFA signings (all, v5.6): {len(ifa)} | reached MLB value: {sum(1 for x in ifa if abs(x[4]) > 0.05)}", flush=True)

# class means: league value over 30 clubs
class_tot = defaultdict(float)
for tid, yr, pid, nm, v, dt in ifa:
    class_tot[yr] += v
def class_mean(yr):
    # every club shops every class from (near-)equal pools: the expectation
    # is the league's realized value from that class over 30 clubs
    return class_tot[yr] / 30.0

# per-regime channel
res = json.load(open("/work/sweep_results.json"))
for r in res:
    old = (r.get("chan", {}).get("intl") or {}).get("net")
    if old is not None:
        r["total"] = round(r["total"] - old, 1)
by_id = {r["teamId"]: r for r in res}
def grade(nps):
    for thr, g in [(2.6,80),(1.8,75),(1.2,70),(0.8,65),(0.5,60),(0.2,55),
                   (-0.2,50),(-0.6,45),(-1.0,40),(-1.6,35)]:
        if nps >= thr: return g
    return 30

per = defaultdict(lambda: dict(real=0.0, exp=0.0, n=0, tops=[]))

for tid, yr, pid, nm, v, dt in ifa:
    # attribution fix: a signing belongs to the regime only if it happened
    # on this regime's watch (true signing date on/after the start date;
    # the league class baseline stays league-wide)
    if dt < REG[tid]["start"]: continue
    p = per[tid]; p["real"] += v; p["n"] += 1
    p["tops"].append((v, yr, nm, pid, dt))
for tid, p in per.items():
    y0 = max(int(REG[tid]["start"][:4]), 2005)
    p["exp"] = sum(class_mean(y) for y in range(y0, 2027))

print(f"\n{'team':<6}{'IFA net':>9}{'real':>8}{'exp':>7}{'n':>5}   best signing")
for r in res:
    tid = r["teamId"]; p = per.get(tid, dict(real=0.0, exp=sum(class_mean(y) for y in range(max(int(REG[tid]['start'][:4]),2005), 2027)), n=0, tops=[]))
    net = p["real"] - p["exp"]
    r["chan"]["intl"] = dict(net=round(net, 1), g=grade(net / r["seasons"]), n=p["n"])
    if r["teamId"] == 144 and REG[144]["start"] >= "2017-11":
        r["chan"]["intl"]["note"] = ("Context: in November 2017 MLB sanctioned Atlanta for the previous front office's "
                                     "international violations: 13 signees were released, signings were capped at $10,000 "
                                     "for the 2019-20 period, and the 2020-21 bonus pool was cut in half.")
    tops = sorted(p["tops"], key=lambda t: -t[0])[:5]
    r["allx_intl"] = [[dt, nm, y, round(v, 1), pp] for v, y, nm, pp, dt in sorted(p["tops"], key=lambda t: t[4]) if abs(v) >= 0.05]
    r["intl_tops"] = [dict(d=dt, ch="intl", net=round(v, 1), st=0.5,
                           h=f"Int'l amateur signing: {nm} ({y} class)",
                           sides=[["Produced in his six control seasons (any club)", [[nm, f"{v:+.1f}"]]],
                                  ["Class baseline", [["league class value over 30 clubs, near-equal pools", "shared"]]]],
                           pids=[pp])
                      for v, y, nm, pp, dt in tops if v >= 0.5]
    r["total"] = round(r["total"] + net, 1)
    r["forGrade"] = grade_comp_ifa(r["total"] / r["seasons"])   # v5.1: the composite grade follows the total
    best = f"{tops[0][2]} (+{tops[0][0]:.1f})" if tops and tops[0][0] > 0.3 else "-"
    print(f"{r['abbr']:<6}{net:>+9.1f}{p['real']:>8.1f}{p['exp']:>7.1f}{p['n']:>5}   {best}")

json.dump(res, open("/work/sweep_results.json", "w"), indent=1)
json.dump({"intl": [[0.5, round(v, 2)] for (_t, _y, _p, _n, v, _d) in ifa if _y <= 2020]}, open("/work/move_pop_intl.json", "w"))
print("\nmerged chan.intl into sweep_results.json")
