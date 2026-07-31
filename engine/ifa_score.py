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

Scoring: realized = LVM while on the signing org (class year +10 cap);
baseline = class mean among observed regimes; regime net = sum over classes.
Known gaps: value-relevant signees only (kids without MLB time count as
volume, not value); signing dates are as-filed; posting-system pros with
major-league deals (Ohtani, Yamamoto) are NOT here, they stay in FA-major.

Merges chan.intl into sweep_results.json in place.
"""
import json, sqlite3
from collections import defaultdict
from datetime import date
from ledger_war import get, API

NA_DRAFT = {"USA", "Canada", "Puerto Rico", "Guam", "U.S. Virgin Islands",
            "Virgin Islands", "American Samoa", "Northern Mariana Islands"}

cfg = json.load(open("/home/claude/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
LVM = json.load(open("/home/claude/lvm_cache.json"))
con = sqlite3.connect("/home/claude/ledger.sqlite"); con.row_factory = sqlite3.Row

rows = [dict(r) for r in con.execute(
    """select team_id, date, person_id, person_name from sweep_tx
       where type_desc='Signed as Free Agent' and lower(description) like '%minor league%'
       and person_id is not null""")]
first_seen = {}
for r in con.execute("select person_id, min(date) d from sweep_tx where person_id is not null group by person_id"):
    first_seen[r["person_id"]] = r["d"]

# value-relevant universe
cands = sorted({r["person_id"] for r in rows if r["person_id"] in LVM and LVM[r["person_id"]]["rows"]})
print(f"value-relevant minor-FA signees: {len(cands)}", flush=True)

bio = {}
for i in range(0, len(cands), 100):
    chunk = ",".join(cands[i:i+100])
    d = get(f"{API}/people?personIds={chunk}&fields=people,id,birthDate,birthCountry")
    for p in d.get("people", []):
        bio[str(p["id"])] = (p.get("birthDate"), p.get("birthCountry"))
print(f"bios: {len(bio)}", flush=True)

def age_at(bd, when):
    b = date.fromisoformat(bd); w = date.fromisoformat(when)
    return (w - b).days / 365.25

# classify + realize
ifa = []  # (team_id, class_year, person_id, name, realized)
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
    realized = sum(v for (y, tm, v) in LVM[pid]["rows"] if tm in names and yr <= y <= yr + 10)
    ifa.append((tid, yr, pid, r["person_name"], round(realized, 2)))
print(f"classified IFA signings (value-relevant): {len(ifa)}", flush=True)

# class means among observed regimes
class_tot = defaultdict(float); class_teams = defaultdict(set)
observed = defaultdict(int)
for reg in cfg["regimes"]:
    y0 = max(int(reg["start"][:4]), 2005)
    for y in range(y0, 2027): observed[y] += 1
for tid, yr, pid, nm, v in ifa:
    class_tot[yr] += v
def class_mean(yr):
    return class_tot[yr] / max(1, observed[yr])

# per-regime channel
res = json.load(open("/home/claude/sweep_results.json"))
by_id = {r["teamId"]: r for r in res}
def grade(nps):
    for thr, g in [(2.6,80),(1.8,75),(1.2,70),(0.8,65),(0.5,60),(0.2,55),
                   (-0.2,50),(-0.6,45),(-1.0,40),(-1.6,35)]:
        if nps >= thr: return g
    return 30

per = defaultdict(lambda: dict(real=0.0, exp=0.0, n=0, tops=[]))
for tid, yr, pid, nm, v in ifa:
    p = per[tid]; p["real"] += v; p["n"] += 1
    p["tops"].append((v, yr, nm))
for tid, p in per.items():
    y0 = max(int(REG[tid]["start"][:4]), 2005)
    p["exp"] = sum(class_mean(y) for y in range(y0, 2027))

print(f"\n{'team':<6}{'IFA net':>9}{'real':>8}{'exp':>7}{'n':>5}   best signing")
for r in res:
    tid = r["teamId"]; p = per.get(tid, dict(real=0.0, exp=sum(class_mean(y) for y in range(max(int(REG[tid]['start'][:4]),2005), 2027)), n=0, tops=[]))
    net = p["real"] - p["exp"]
    r["chan"]["intl"] = dict(net=round(net, 1), g=grade(net / r["seasons"]), n=p["n"])
    tops = sorted(p["tops"], reverse=True)[:3]
    r["intl_tops"] = [dict(d=f"{y}-01-15", ch="intl", net=v,
                           h=f"Int'l amateur signing: {nm} ({y} class)") for v, y, nm in tops if v >= 0.8]
    r["total"] = round(r["total"] + net, 1)
    best = f"{tops[0][2]} (+{tops[0][0]:.1f})" if tops and tops[0][0] > 0.3 else "-"
    print(f"{r['abbr']:<6}{net:>+9.1f}{p['real']:>8.1f}{p['exp']:>7.1f}{p['n']:>5}   {best}")

json.dump(res, open("/home/claude/sweep_results.json", "w"), indent=1)
print("\nmerged chan.intl into sweep_results.json")
