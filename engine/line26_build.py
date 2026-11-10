"""2026 big-league stat lines for every player in the pool (Nov 10 2026).
Hitters: AVG/OBP/SLG, HR, SB, PA. Pitchers: IP, ERA, K, BB (saves for relievers).
Source: the league's public season-stats feed. Writes line26.json {pid: line};
read by desk_data.py and shipped as DESK.line26."""
import json, urllib.request, time
ROOT = "/work"
def pull(group):
    rows, off = [], 0
    while True:
        u = f"https://statsapi.mlb.com/api/v1/stats?stats=season&group={group}&season=2026&sportId=1&playerPool=ALL&limit=500&offset={off}"
        for k in range(4):
            try: d = json.load(urllib.request.urlopen(u, timeout=40)); break
            except Exception as e: time.sleep(2 + 2 * k)
        sp = d["stats"][0]["splits"]; rows += sp; off += 500
        if off >= d["stats"][0].get("totalSplits", 0) or not sp: break
    return rows
def best(rows, key):
    # one row per player: the season total when the feed gives one (no team on the row), else the biggest sample
    by = {}
    for r in rows:
        pid = r["player"]["id"]; tot = 0 if r.get("team") else 1
        k = (tot, key(r["stat"]))
        if pid not in by or k > by[pid][0]: by[pid] = (k, r["stat"], sum(1 for x in rows if x["player"]["id"] == pid) if False else 0)
    return {pid: v[1] for pid, v in by.items()}
def ipf(s):
    a, _, b = str(s).partition("."); return int(a or 0) + int(b or 0) / 3
hit = best(pull("hitting"), lambda s: s.get("plateAppearances", 0))
pit = best(pull("pitching"), lambda s: ipf(s.get("inningsPitched", 0)))
d = json.load(open(f"{ROOT}/desk_data.json"))
out = {}
for p in d["players"]:
    pid = p[1]; h, q = hit.get(pid), pit.get(pid); bits = []
    if q and ipf(q.get("inningsPitched", 0)) >= 5 and (p[3] or not h or h.get("plateAppearances", 0) < 30):
        sv = q.get("saves", 0)
        bits.append(f'{q["inningsPitched"]} IP, {q["era"]} ERA, {q["strikeOuts"]} K, {q["baseOnBalls"]} BB' + (f", {sv} SV" if sv >= 5 else ""))
    if h and h.get("plateAppearances", 0) >= 20 and (not p[3] or h.get("plateAppearances", 0) >= 150):
        bits.insert(0, f'{h["avg"]}/{h["obp"]}/{h["slg"]}, {h["homeRuns"]} HR, {h["stolenBases"]} SB in {h["plateAppearances"]} PA')
    if bits: out[str(pid)] = "; ".join(bits)
json.dump(out, open(f"{ROOT}/line26.json", "w"), separators=(",", ":"))
print(f"2026 lines: {len(out)} of {len(d['players'])} pool players ({len(hit)} hitters, {len(pit)} pitchers in the feed)")
