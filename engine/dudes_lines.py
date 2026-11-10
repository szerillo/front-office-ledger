"""Remember Some Dudes: each dude's best-season stat line (Nov 10 2026).
Best season = his top Baseball-Reference WAR year (already in dudes.json); the line for that year comes
from the league's public year-by-year stats, summed across clubs in a split season.
Usage: python3 dudes_lines.py <dir with bref/ and dudes.json>; adds a 'best_line' column (v3)."""
import csv, json, sys, urllib.request, time, os
from concurrent.futures import ThreadPoolExecutor
S = sys.argv[1]
mlb = {}
for fn in ("war_daily_bat.txt", "war_daily_pitch.txt"):
    with open(f"{S}/bref/{fn}", newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r.get("mlb_ID") and r["mlb_ID"] != "NULL": mlb[r["player_ID"]] = r["mlb_ID"]
d = json.load(open(f"{S}/dudes.json"))
CACHE = f"{S}/dudes_yby.json"
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def get(mid, grp):
    k = f"{mid}:{grp}"
    if k in cache: return cache[k]
    u = f"https://statsapi.mlb.com/api/v1/people/{mid}/stats?stats=yearByYear&group={grp}&sportId=1"
    for t in range(4):
        try:
            j = json.load(urllib.request.urlopen(u, timeout=30)); break
        except Exception: time.sleep(1 + 2 * t); j = None
    sp = (j or {}).get("stats") or []
    cache[k] = [[s.get("season"), 1 if s.get("team") else 0, s["stat"]] for s in (sp[0]["splits"] if sp else [])]
    return cache[k]
def season(rows, yr):
    xs = [r for r in rows if r[0] == str(yr)]
    tot = [r for r in xs if not r[1]]          # the feed adds a combined row for a split season
    return (tot or xs or [None])[0] and (tot[0][2] if tot else (xs[0][2] if len(xs) == 1 else None)), xs
def line(row):
    bid, pit, yr = row[0], row[4], row[8]
    mid = mlb.get(bid)
    if not mid: return ""
    rows = get(mid, "pitching" if pit else "hitting")
    st, xs = season(rows, yr)
    if st is None and xs:                      # split season without a combined row: use the biggest stint, say so
        key = (lambda s: float(str(s.get("inningsPitched", 0)) or 0)) if pit else (lambda s: s.get("plateAppearances", 0))
        st = max((x[2] for x in xs), key=key)
    if not st: return ""
    try:
        if pit:
            gs, sv = st.get("gamesStarted", 0), st.get("saves", 0)
            head = f'{st.get("wins", 0)}-{st.get("losses", 0)}, ' if gs >= 10 else ""
            return f'{head}{st["era"]} ERA, {st["inningsPitched"]} IP, {st["strikeOuts"]} K' + (f', {sv} SV' if sv >= 5 else "")
        return f'{st["avg"]}/{st["obp"]}/{st["slg"]}, {st["homeRuns"]} HR, {st["rbi"]} RBI' + (f', {st["stolenBases"]} SB' if st.get("stolenBases", 0) >= 15 else "")
    except KeyError: return ""
rows = d["rows"]
with ThreadPoolExecutor(12) as ex: lines = list(ex.map(line, rows))
json.dump(cache, open(CACHE, "w"))
out = [r[:11] + [l] for r, l in zip(rows, lines)]
cols = d["cols"][:11] + ["best_line"]
json.dump({"v": 3, "src": d["src"] + "; season lines: MLB", "cols": cols, "rows": out}, open(f"{S}/dudes.json", "w"), separators=(",", ":"), ensure_ascii=False)
print(f"dudes: {len(out)} rows, {sum(1 for l in lines if l)} with a best-season line")
