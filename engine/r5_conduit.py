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
