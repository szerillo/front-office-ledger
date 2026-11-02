"""v5.9 feed repair (idempotent, chain step 0): a Rule 5 pick traded by the
selecting club within three days was a conduit (Johan Santana, 1999: Florida
selected him from Houston and sent him straight to Minnesota for Jared Camp).
The selection is re-filed on the club that kept him, and the pass-through
trade row is marked so the conduit is not charged the player's career; the
losing club's Rule 5 loss is then valued where he actually played."""
import sqlite3, json
from datetime import date
cfg = json.load(open("/work/regimes.json"))
N2T = {}
for r in cfg["regimes"]:
    for n in set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]}: N2T[n] = r["teamId"]
c = sqlite3.connect("/work/ledger.sqlite")
n = 0
for rid, d, pid, nm, fr, to in c.execute("select rowid,date,person_id,person_name,from_team,to_team from sweep_tx "
                                         "where type_desc='Rule 5 Selection' and person_id is not null").fetchall():
    tr = [x for x in c.execute("select rowid,date,to_team from sweep_tx where type_desc='Trade' and person_id=? and from_team=? and date>=?",
                               (pid, to, d)).fetchall()
          if (date.fromisoformat(x[1][:10]) - date.fromisoformat(d[:10])).days <= 3]
    if not tr: continue
    final = tr[0][2]
    if final not in N2T: continue
    c.execute("update sweep_tx set to_team=?, team_id=? where rowid=?", (final, N2T[final], rid))
    # the same selection filed under the losing club: it lost him to the final club
    c.execute("update sweep_tx set to_team=? where type_desc='Rule 5 Selection' and person_id=? and date=? and to_team=?", (final, pid, d, to))
    for x in tr: c.execute("update sweep_tx set type_desc='Trade (Rule 5 conduit)' where rowid=?", (x[0],))
    n += 1; print(d, nm, fr, "->", to, "->", final)
c.commit(); print("conduits re-filed:", n)

# v5.9 (same step): a Retrosheet row resolved to the wrong player of the same
# name, filed beside the right one (Colorado signed one Matt Miller on
# 2002-11-20, the archive carries two ids). Where two ids share a name, date,
# club and transaction type and only one of them played for that club within
# a season of the date, the other row is marked as a mis-resolved duplicate.
import json as _j
L = {int(k): v for k, v in _j.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
_names = {}
for r in cfg["regimes"]:
    _names[r["teamId"]] = set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]}
fixed = 0
for d, tid, ty, nm, ids in c.execute("""select date, team_id, type_desc, person_name, group_concat(distinct person_id) from sweep_tx
        where person_id is not null and description like '%Retrosheet%' group by date, team_id, type_desc, person_name
        having count(distinct person_id) > 1""").fetchall():
    y = int(d[:4]); ok = []
    for pid in ids.split(","):
        rows = (L.get(int(pid)) or {}).get("rows", [])
        if any(abs(r_[0] - y) <= 1 and r_[1] in _names.get(tid, set()) for r_ in rows): ok.append(pid)
    if len(ok) == 1:
        for pid in ids.split(","):
            if pid != ok[0]:
                c.execute("update sweep_tx set type_desc = type_desc || ' (mis-resolved duplicate)' where date=? and team_id=? and type_desc=? and person_id=?", (d, tid, ty, pid))
                fixed += 1; print("mis-resolved:", d, nm, pid, "kept", ok[0])
c.commit(); print("mis-resolved duplicates marked:", fixed)
