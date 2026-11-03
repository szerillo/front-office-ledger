"""Rebuild lvm_cache.json and ext_lvm_cache.json at LEDGER WAR v1.7:
defense from Defensive Runs Saved (SIS) for 1B/2B/3B/SS and Statcast
Fielding Run Value for C/LF/CF/RF (2016+; DRS for C/OF 2003-2015; v1.6
SDI/Statcast value as the per-group fallback and for pre-2003), see
lvm15.def_runs. Batting, pitching, park, positional adjustment (v1.6,
games-weighted), replacement level and runs-per-win are unchanged.

Inputs: frv_runs.json (frv_ingest.py), drs_runs.json (drs_ingest.py).
Backs up the v1.6 caches once as *.v16.bak.json; marks caches __lvm_v17__.
Writes an audit file (AUDIT_OUT env, optional) with, per player, the rows
the same fetch gives under the v1.6 defense, so before/after comparisons
isolate the defense change from any stat drift in the feed.
Set FORCE=1 to rebuild a cache already marked v1.7."""
import json, os, shutil, time
from lvm15 import player_team_seasons_v15, old_def_runs

AUDIT = {}

def v16_rows(base, years, pid):
    """same base rows, joined with the v1.6 defense (SDI/OAA/framing)"""
    rows = [list(r) for r in base]
    byyear = {}
    for idx, (y, tm, v) in enumerate(rows): byyear.setdefault(y, []).append(idx)
    for y, idxs in byyear.items():
        dg = years.get(y, {})
        if "rpw" not in dg: continue
        runs = old_def_runs(pid, y) + dg.get("bsr", 0.0)
        if not runs: continue
        extra = runs / dg["rpw"]
        tot = sum(abs(rows[k][2]) for k in idxs)
        for k in idxs:
            rows[k][2] += extra * ((abs(rows[k][2]) / tot) if tot > 0 else 1.0 / len(idxs))
    return rows

def rebuild(path, tag):
    cache = json.load(open(path))
    if cache.get("__lvm_v17__") and not os.environ.get("FORCE"):
        print(path, "already v1.7, skipping"); return
    bak = path.replace(".json", ".v16.bak.json")
    if not os.path.exists(bak): shutil.copy(path, bak)
    ids = sorted(int(k) for k in cache if not k.startswith("__"))
    print(f"{path}: rebuilding {len(ids)} players", flush=True)
    t0 = time.time()
    diag = {}
    new = player_team_seasons_v15(ids, diag=diag)
    out = {str(k): v for k, v in new.items()}
    kept = 0
    for k, v in cache.items():
        if k.startswith("__"): continue
        if k not in out: out[k] = v; kept += 1
    for k in ("__lvm_v15__", "__lvm_v16__", "__lvm_v17__"): out[k] = True
    json.dump(out, open(path, "w"))
    AUDIT[tag] = {str(pid): {"v16eq": v16_rows(d["base"], d["years"], pid),
                             "years": {str(y): dg for y, dg in d["years"].items()}}
                  for pid, d in diag.items()}
    got = {str(x) for x in new}
    AUDIT[tag + "_kept"] = [k for k in cache if not k.startswith("__") and k not in got]
    print(f"{path}: {len(out)-3} players ({kept} kept at v1.6), {time.time()-t0:.0f}s", flush=True)

rebuild("/work/lvm_cache.json", "lvm")
if os.path.exists("/work/ext_lvm_cache.json"):
    rebuild("/work/ext_lvm_cache.json", "ext")
if os.environ.get("AUDIT_OUT"):
    json.dump(AUDIT, open(os.environ["AUDIT_OUT"], "w"))
    print("audit ->", os.environ["AUDIT_OUT"])
