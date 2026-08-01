"""
REGIME DNA part 2: development-effect scores.

Does a player get BETTER after joining this org? Two org-level effects,
computed from movers (players who changed orgs), receiving-org attribution:

  devDef  defense delta: mean of (def runs/season, first 2 seasons at the
          new org) minus (last 2 seasons at the old org), across all movers
          with defense data on both sides (SDI preferred, Statcast else).
          Positive = gloves improve after arriving. Runs per season.
  devPit  pitching delta: same construction on pitcher Ledger WAR seasons.
          Positive = arms improve after arriving. Wins per season.

Selection effects are real (clubs acquire players they think they can fix,
and playing-time survivorship trims the tails); scores are shown as org
tendencies, not causal claims, and need a minimum of 6 movers to display.
Attribution is to the ORG (not regime-windowed) because coaching infra
outlives GMs; the card notes the caveat.

Merges dna.devDef / dna.devPit into sweep_results.json.
"""
import json
from collections import defaultdict

SV = json.load(open("/home/claude/savant_runs.json"))
SDI = json.load(open("/home/claude/sdi_runs.json"))
LVM = {k: v for k, v in json.load(open("/home/claude/lvm_cache.json")).items() if not k.startswith("__")}
POS = json.load(open("/home/claude/positions.json"))
PITPOS = {"RHP", "LHP", "SP", "RP"}
cfg = json.load(open("/home/claude/regimes.json"))

NAME2AB = {}
for r in cfg["regimes"]:
    NAME2AB[r["team"]] = r["abbr"]
    for al in cfg["aliases"].get(str(r["teamId"]), []):
        NAME2AB[al] = r["abbr"]

def org_of(tm):
    if tm in NAME2AB: return NAME2AB[tm]
    for nm, ab in NAME2AB.items():
        if nm in tm: return ab
    return None

def def_runs(pid, y):
    s = SDI.get(pid, {}).get(str(y))
    if s is not None: return s
    sv = SV.get(pid, {}).get(str(y), {})
    if "def" in sv or "frame" in sv:
        return sv.get("def", 0.0) + sv.get("frame", 0.0)
    return None

def pit_wins(pid, y):
    rec = LVM.get(pid)
    if not rec: return None
    vals = [v for (yy, tm, v) in rec["rows"] if yy == y]
    return sum(vals) if vals else None

dd = defaultdict(list)   # org -> defense deltas
dp = defaultdict(list)   # org -> pitching deltas

for pid, rec in LVM.items():
    rows = rec.get("rows") or []
    seq = {}
    for (y, tm, v) in rows:
        ab = org_of(tm)
        if ab: seq.setdefault(y, ab)          # first org of the season
    years = sorted(seq)
    if len(years) < 3: continue
    is_pit = POS.get(str(pid)) in PITPOS
    for i in range(1, len(years)):
        y = years[i]
        if seq[y] == seq[years[i-1]]: continue          # no org change
        new_org = seq[y]
        before_y = [yy for yy in years[:i] if seq[yy] != new_org][-2:]
        after_y = [yy for yy in years[i:] if seq[yy] == new_org][:2]
        if not before_y or not after_y: continue
        if is_pit:
            b = [pit_wins(pid, yy) for yy in before_y]
            a = [pit_wins(pid, yy) for yy in after_y]
            b = [x for x in b if x is not None]; a = [x for x in a if x is not None]
            if b and a: dp[new_org].append(sum(a)/len(a) - sum(b)/len(b))
        else:
            b = [def_runs(pid, yy) for yy in before_y]
            a = [def_runs(pid, yy) for yy in after_y]
            b = [x for x in b if x is not None]; a = [x for x in a if x is not None]
            if b and a: dd[new_org].append(sum(a)/len(a) - sum(b)/len(b))
        break                                            # one move per player (first)

res = json.load(open("/home/claude/sweep_results.json"))
print(f"{'org':<5}{'defΔ':>8}{'n':>5}{'pitΔ':>8}{'n':>5}")
for r in res:
    ab = r["abbr"]
    d = dd.get(ab, []); p = dp.get(ab, [])
    r.setdefault("dna", {})
    r["dna"]["devDef"] = dict(v=round(sum(d)/len(d), 2), n=len(d)) if len(d) >= 6 else dict(v=None, n=len(d))
    r["dna"]["devPit"] = dict(v=round(sum(p)/len(p), 2), n=len(p)) if len(p) >= 6 else dict(v=None, n=len(p))
    print(f"{ab:<5}{(sum(d)/len(d) if d else 0):>+8.2f}{len(d):>5}{(sum(p)/len(p) if p else 0):>+8.2f}{len(p):>5}")

json.dump(res, open("/home/claude/sweep_results.json", "w"), indent=1)
print("\nmerged dna dev scores")
