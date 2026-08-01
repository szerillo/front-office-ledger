"""
LEDGER WAR v1: real defense and baserunning join.

Component priority per player-season:
  defense = SDI (SABR Defensive Index, runs; includes framing for catchers)
            when published for the player-year (finalists 2014-2022, all
            qualifiers 2023+), else Statcast fielding_runs_prevented (2016+,
            position players) + catcher framing runs (2015+). Pre-2014 and
            non-qualifying pre-2016 seasons stay batting+positional only.
  baserunning = Statcast runner runs (2016+), always additive (neither SDI
            nor FRP includes it).

Runs convert to wins at the season's runs-per-win (1.5*lgRPG+3, same scale
as the batting component). Multi-team seasons split the add-on across the
player's team rows proportional to absolute offensive value share.

Rewrites lvm_cache.json and ext_lvm_cache.json in place (originals backed
up once as *.v0.bak). Idempotent: refuses to run twice by marking caches.
"""
import json, os, shutil
from ledger_war import constants

SV = json.load(open("/home/claude/savant_runs.json"))
SDI = json.load(open("/home/claude/sdi_runs.json"))

RPW = {}
for y in range(2013, 2027):
    RPW[y] = constants(y)["rpw"]
print("rpw loaded 2013-2026")

def season_extra(pid, y):
    ys = str(y)
    sdi = SDI.get(pid, {}).get(ys)
    sv = SV.get(pid, {}).get(ys, {})
    d = sdi if sdi is not None else (sv.get("def", 0.0) + sv.get("frame", 0.0))
    b = sv.get("bsr", 0.0)
    runs = d + b
    if not runs: return 0.0
    return runs / RPW.get(y, 9.0)

def join_cache(path):
    cache = json.load(open(path))
    if cache.get("__lvm_v1__"):
        print(path, "already v1, skipping"); return
    bak = path.replace(".json", ".v0.bak.json")
    if not os.path.exists(bak): shutil.copy(path, bak)
    touched = players = 0
    for pid, rec in cache.items():
        if pid.startswith("__") or not isinstance(rec, dict): continue
        rows = rec.get("rows") or []
        byyear = {}
        for i, (y, tm, v) in enumerate(rows):
            byyear.setdefault(y, []).append(i)
        changed = False
        for y, idxs in byyear.items():
            extra = season_extra(str(pid), y)
            if not extra: continue
            tot = sum(abs(rows[i][2]) for i in idxs)
            for i in idxs:
                share = (abs(rows[i][2]) / tot) if tot > 0 else (1.0 / len(idxs))
                rows[i][2] += extra * share
            changed = True; touched += 1
        if changed: players += 1
    cache["__lvm_v1__"] = True
    json.dump(cache, open(path, "w"))
    print(f"{path}: {players} players, {touched} player-seasons upgraded to v1")

join_cache("/home/claude/lvm_cache.json")
join_cache("/home/claude/ext_lvm_cache.json")

# spot-check: catchers should warm up
L = json.load(open("/home/claude/lvm_cache.json"))
L0 = json.load(open("/home/claude/lvm_cache.v0.bak.json"))
for pid, nm in [("663728", "Cal Raleigh"), ("668939", "Adley Rutschman"), ("621020", "Dansby Swanson")]:
    a = {y: round(v, 1) for (y, tm, v) in (L0.get(pid, {}).get("rows") or []) if y >= 2023}
    b = {y: round(v, 1) for (y, tm, v) in (L.get(pid, {}).get("rows") or []) if y >= 2023}
    print(f"{nm:<18} v0 {a}  ->  v1 {b}")
