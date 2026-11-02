"""v5.9 (chain step, before the scorers): calibrate the draft expectation.

Value of a pick = what the player produced in his original control seasons
(asset_rules.control_value: debut through the end of club control, ending
at a release or free-agent filing), wherever he played them.

  DRAFT_SHAPE[n]  share of that value realized by n seasons after the draft,
                  pooled over the matured 1998-2013 classes;
  K_CLASS[year]   the league's realized value per unit of the published slot
                  curve FOR THAT CLASS (realized / slot x shape), shrunk toward
                  the pooled ratio by the class's expectation (immature
                  classes lean on the pool).

Centering by class means a pick is judged against what the league got from
that slot in the same draft: the 1998-2006 classes returned about 0.8x the
pooled curve and later classes over 1.1x (Ledger WAR before 2014 is bat-only
on defense, and the pipeline changed), and one pooled K read every early-era
drafting regime as poor. Writes draft_calib.json."""
import json, sqlite3, sys
from collections import defaultdict
sys.path.insert(0, "/work")
import asset_rules as A
from era_names import draft_day
import math
def slot_expectation(pick):
    table = [(1, 9.9), (2, 7.5), (3, 6.7), (5, 5.5), (8, 4.6), (12, 3.6), (17, 3.0),
             (22, 2.6), (30, 2.1), (45, 1.5), (65, 1.1), (90, 0.85), (120, 0.6),
             (200, 0.35), (400, 0.18), (620, 0.10)]
    if pick <= 1: return table[0][1]
    for (p1, v1), (p2, v2) in zip(table, table[1:]):
        if pick <= p2:
            f = (math.log(pick) - math.log(p1)) / (math.log(p2) - math.log(p1))
            return v1 + f * (v2 - v1)
    return 0.10
con = sqlite3.connect("/work/ledger.sqlite")
L = A._lvm()
RED = defaultdict(set)
for pid, yy in con.execute("select person_id, cast(year as int) from draft_picks where person_id is not null"):
    RED[str(pid)].add(yy)
rows = []; seen = set()
for y, rd, pk, pid in con.execute("select cast(year as int), cast(round as int), cast(pick_overall as int), person_id from draft_picks "
                                  "where cast(year as int) between 1998 and 2025 and cast(round as int)<=5"):
    if not pk or (pid, y, pk) in seen: continue
    seen.add((pid, y, pk))
    if any(y2 > y for y2 in RED.get(str(pid), ())): continue          # unsigned: re-drafted later
    rec = L.get(int(pid)) if pid else None
    ser = A.control_value(rec, pid=int(pid), after=draft_day(y), series=True) if rec else {}
    rows.append((y, slot_expectation(pk), ser))
# shape over matured classes
cum = defaultdict(float); tot = 0.0; slot_m = 0.0
for y, sl, ser in rows:
    if y > 2013: continue
    slot_m += sl
    for yy, v in ser.items():
        cum[yy - y] += v; tot += v
K = tot / slot_m
shape = {}; run = 0.0
for n in range(0, 16):
    run += cum.get(n, 0.0); shape[n] = round(run / tot, 3)
last = 0.0
for n in range(16): shape[n] = max(last, shape[n]); last = shape[n]
shape = {n: v for n, v in shape.items() if v < 0.999 or n <= 13}
def sh(n): return shape.get(n, 1.0) if n >= 0 else 0.0
# class ratios, shrunk
LAM = 40.0
byc = defaultdict(lambda: [0.0, 0.0])
for y, sl, ser in rows:
    e = sl * sh(2026 - y)
    byc[y][0] += sum(v for yy, v in ser.items() if yy <= 2026); byc[y][1] += e
kc = {}
for y, (r, e) in sorted(byc.items()):
    kc[y] = round((r + LAM * K) / (e + LAM), 3)
out = dict(k_pooled=round(K, 3), shape={str(k): v for k, v in shape.items()}, k_class={str(k): v for k, v in kc.items()},
           raw={str(y): [round(r, 1), round(e, 1)] for y, (r, e) in byc.items()}, lam=LAM)
json.dump(out, open("/work/draft_calib.json", "w"))
print("pooled K", round(K, 3)); print("shape", shape)
print("class K", kc)
