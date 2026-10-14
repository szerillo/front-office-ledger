"""Rebuild lvm_cache.json and ext_lvm_cache.json at LEDGER WAR v1.5:
full refetch of every cached player with park adjustment + defense join.
Backs up current (v1) caches once as *.v1.bak.json. Marks caches
__lvm_v15__ so the join is never doubled."""
import json, os, shutil, time
from lvm15 import player_team_seasons_v15

def rebuild(path):
    cache = json.load(open(path))
    if cache.get("__lvm_v15__"):
        print(path, "already v1.5, skipping"); return
    bak = path.replace(".json", ".v1.bak.json")
    if not os.path.exists(bak): shutil.copy(path, bak)
    ids = sorted(int(k) for k in cache if not k.startswith("__"))
    print(f"{path}: rebuilding {len(ids)} players", flush=True)
    t0 = time.time()
    new = player_team_seasons_v15(ids)
    out = {str(k): v for k, v in new.items()}
    # keep any cached player the refetch missed (API hiccup) at old values
    kept = 0
    for k, v in cache.items():
        if k.startswith("__"): continue
        if k not in out:
            out[k] = v; kept += 1
    out["__lvm_v15__"] = True
    json.dump(out, open(path, "w"))
    print(f"{path}: {len(out)-1} players ({kept} kept at v1), {time.time()-t0:.0f}s", flush=True)

rebuild("/home/claude/lvm_cache.json")
rebuild("/home/claude/ext_lvm_cache.json")

# spot checks: Coors bats should cool, Coors arms warm, neutral parks ~unchanged
L = json.load(open("/home/claude/lvm_cache.json"))
L1 = json.load(open("/home/claude/lvm_cache.v1.bak.json"))
for pid, nm in [("571448", "Nolan Arenado"), ("453568", "Charlie Blackmon"),
                ("608566", "German Marquez"), ("592450", "Aaron Judge"),
                ("545361", "Mike Trout"), ("660271", "Shohei Ohtani")]:
    a = {y: round(v, 1) for (y, tm, v) in (L1.get(pid, {}).get("rows") or []) if 2017 <= y <= 2019}
    b = {y: round(v, 1) for (y, tm, v) in (L.get(pid, {}).get("rows") or []) if 2017 <= y <= 2019}
    print(f"{nm:<18} v1 {a}  ->  v1.5 {b}")
