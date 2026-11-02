"""Rebuild lvm_cache.json and ext_lvm_cache.json at LEDGER WAR v1.6:
positional adjustment by games actually played at each position each
season (lvm15.season_posadj). Backs up the v1.5 caches as *.v15.bak.json.
Marks caches __lvm_v16__."""
import json, os, shutil, time
from lvm15 import player_team_seasons_v15

def rebuild(path):
    cache = json.load(open(path))
    if cache.get("__lvm_v16__"):
        print(path, "already v1.6, skipping"); return
    bak = path.replace(".json", ".v15.bak.json")
    if not os.path.exists(bak): shutil.copy(path, bak)
    ids = sorted(int(k) for k in cache if not k.startswith("__"))
    print(f"{path}: rebuilding {len(ids)} players", flush=True)
    t0 = time.time()
    new = player_team_seasons_v15(ids)
    out = {str(k): v for k, v in new.items()}
    kept = 0
    for k, v in cache.items():
        if k.startswith("__"): continue
        if k not in out: out[k] = v; kept += 1
    out["__lvm_v15__"] = True; out["__lvm_v16__"] = True
    json.dump(out, open(path, "w"))
    print(f"{path}: {len(out)-2} players ({kept} kept at v1.5), {time.time()-t0:.0f}s", flush=True)

rebuild("/work/lvm_cache.json")
if os.path.exists("/work/ext_lvm_cache.json"):
    rebuild("/work/ext_lvm_cache.json")
