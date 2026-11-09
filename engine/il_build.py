"""Nov 9: injured-list days per player-season from the transaction sweep (ledger.sqlite sweep_tx,
MLB Stats API 2005-2026). A stint opens on 'placed ... injured/disabled list' (retroactive date
when given) and closes on 'activated'/'reinstated' from it; a stint still open at season's end runs
to season's end. Days are clipped to the regular season window. Writes il_days.json {pid: {year: days}}."""
import sqlite3, re, json
from datetime import date
from collections import defaultdict
c = sqlite3.connect("/work/ledger.sqlite")
rows = c.execute("select distinct tx_id, date, person_id, description from sweep_tx where description like '%injured list%' or description like '%disabled list%' or description like '%activated%' or description like '%reinstated%' order by date, tx_id").fetchall()
print("IL transactions", len(rows))
# regular-season windows (approximate opening day and last day)
WIN = {y: (date(y, 3, 28), date(y, 9, 30)) for y in range(2005, 2027)}
WIN[2020] = (date(2020, 7, 23), date(2020, 9, 27)); WIN[2022] = (date(2022, 4, 7), date(2022, 10, 5))
for y in (2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015): WIN[y] = (date(y, 4, 1), date(y, 9, 30))
RETRO = re.compile(r"retroactive to (\w+ \d+, \d{4})", re.I)
MON = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}
def pdate(s):
    m, d, y = s.replace(",", "").split(); return date(int(y), MON[m], int(d))
open_ = {}; stints = defaultdict(list); bad = 0; chained = 0
for tx, ds, pid, desc in rows:
    d = date.fromisoformat(ds[:10]); low = desc.lower()
    # a stint with no activation on file ends with its own season (season-ending
    # injuries are activated in November, often with no row we can see)
    if pid in open_ and d.year > open_[pid].year:
        a0 = open_.pop(pid); stints[pid].append((a0, date(a0.year, 12, 31)))
    if " placed " in low or low.startswith("placed"):
        m = RETRO.search(desc)
        try: start = pdate(m.group(1)) if m else d
        except Exception: start = d
        if pid in open_:
            # a second placement with no activation between: close the first at
            # the earlier of this placement and 30 days (the activation is missing)
            a0 = open_.pop(pid); stints[pid].append((a0, min(start, date.fromordinal(a0.toordinal() + 30)))); chained += 1
        open_[pid] = start
    elif "activated" in low or "reinstated" in low:
        if pid in open_: stints[pid].append((open_.pop(pid), d))
        else: bad += 1
    # 'transferred ... to the 60-day' keeps the stint open
for pid, s in open_.items(): stints[pid].append((s, None))
print("players with stints", len(stints), "| activations with no open stint", bad, "| repeated placements", chained)
IL = defaultdict(lambda: defaultdict(int))
for pid, ss in stints.items():
    for a, b in ss:
        for y in range(a.year, (b or date(2026, 11, 9)).year + 1):
            if y not in WIN: continue
            w0, w1 = WIN[y]
            # an open stint (no activation) runs to that season's end only
            end = b if b is not None else date(a.year, 12, 31)
            lo, hi = max(a, w0), min(end, w1)
            if hi > lo: IL[pid][y] += (hi - lo).days
SEASON = {y: (WIN[y][1] - WIN[y][0]).days for y in WIN}
json.dump(dict(days={str(k): {str(y): v for y, v in d.items()} for k, d in IL.items()}, season=SEASON), open("/work/il_days.json", "w"))
for pid, n in (("665833", "Cruz"), ("680776", "Duran"), ("592450", "Judge"), ("621566", "Olson"), ("660670", "Acuna"), ("672335", "Westburg"), ("545361", "Trout")):
    print(n, dict(IL.get(pid, {})))
