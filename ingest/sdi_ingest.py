"""SABR Defensive Index ingest: final-season SDI (runs) per player-year,
2014-2025, parsed from sabr.org/sdi/{year}-final HTML tables. SDI blends
DRS, UZR, and stringer-based systems and includes catcher framing in
recent seasons, so where SDI covers a player it REPLACES the Statcast
defense+framing component rather than adding to it. Qualifiers only; the
long tail falls back to Statcast. Name resolution via the feed map with
club fit for same-name collisions.

Output: sdi_runs.json {pid: {year: sdi}}
"""
import json, re, sqlite3, time, urllib.request
from fa_grade_lib import norm

cfg = json.load(open("/home/claude/regimes.json"))
AB2NAMES = {}
for r in cfg["regimes"]:
    AB2NAMES[r["abbr"]] = set([r["team"]]) | set(cfg["aliases"].get(str(r["teamId"]), []))
# common alternate abbrs used by SABR
ALT = {"WAS": "WSH", "KCR": "KC", "SDP": "SD", "SFG": "SF", "TBR": "TB", "CHW": "CWS", "OAK": "ATH", "ANA": "LAA"}

LVM = json.load(open("/home/claude/lvm_cache.json"))
con = sqlite3.connect("/home/claude/ledger.sqlite")
NAME2PIDS = {}
for pid, rec in LVM.items():
    NAME2PIDS.setdefault(norm(rec.get("name", "")), []).append(pid)
for nm, pid in con.execute("select distinct person_name, person_id from sweep_tx where person_id is not null"):
    p = str(pid)
    lst = NAME2PIDS.setdefault(norm(nm), [])
    if p not in lst: lst.append(p)

def resolve(name, team_ab, year):
    cands = NAME2PIDS.get(norm(name), [])
    if not cands: return None
    if len(cands) == 1: return cands[0]
    ab = ALT.get(team_ab, team_ab)
    names = AB2NAMES.get(ab, set())
    def fit(pid):
        rec = LVM.get(pid)
        if not rec: return 0.0
        return sum(abs(v) for (y, tm, v) in rec["rows"]
                   if y == year and any(al in tm for al in names))
    best = max(cands, key=fit)
    return best if fit(best) > 0 else cands[0]

def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")

OUT = {}
misses = 0
for yr in range(2014, 2026):
    try:
        page = get(f"https://sabr.org/sdi/{yr}-final")
    except Exception as e:
        print(yr, "FAIL", e); continue
    n = 0
    for table in re.findall(r"<table[^>]*>.*?</table>", page, re.S):
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S):
            cells = [re.sub(r"<[^>]+>", "", c).strip()
                     for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
            if len(cells) < 4 or cells[0] in ("Player", ""): continue
            player, team, pos, sdi = cells[0], cells[1], cells[2], cells[3]
            try: v = float(sdi)
            except ValueError: continue
            pid = resolve(player.replace("&#8217;", "'"), team, yr)
            if not pid:
                misses += 1; continue
            OUT.setdefault(pid, {})[str(yr)] = v
            n += 1
    print(f"{yr}: {n} player rows", flush=True)
    time.sleep(0.8)

json.dump(OUT, open("/home/claude/sdi_runs.json", "w"))
print(f"\nsaved sdi_runs.json: {len(OUT)} players, "
      f"{sum(len(v) for v in OUT.values())} player-seasons, {misses} unresolved names")
