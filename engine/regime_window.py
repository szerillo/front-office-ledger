"""Regime windows measured in real seasons (v5.4).

A front office hired or dismissed in the middle of a season held the seat
for only part of it. This module gives every engine one answer for:

  record(tid, start, end, wl)  -> (w, l, div_titles, october_seasons)
      W-L counted from the hire date (and to the dismissal date) using the
      game-by-game schedule for the partial seasons; division titles and
      October credit belong to whoever held the seat when the season ENDED.
  seasons(start, end)          -> seat time in seasons, fractional for a
      partial season (a June hire has about 0.55 of that season), 0 for a
      hire after the last completed season.
"""
import json, os, time, urllib.request
from datetime import date

ROOT = "/work"
CACHE = f"{ROOT}/sched_cache"; os.makedirs(CACHE, exist_ok=True)
LAST_SEASON = 2026
# regular-season spans (approximate opening day / final day; 2020 short)
SPAN = {y: (date(y, 3, 28), date(y, 9, 30)) for y in range(1998, 2027)}
SPAN[2020] = (date(2020, 7, 23), date(2020, 9, 27))
SPAN[2026] = (date(2026, 3, 26), date(2026, 9, 27))

def _d(s): return date.fromisoformat(s[:10])

def _games(tid, yr):
    fn = f"{CACHE}/{tid}_{yr}.json"
    if os.path.exists(fn): return json.load(open(fn))
    u = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={tid}&season={yr}&gameType=R"
    for a in range(4):
        try:
            x = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
            out = []
            for dd in x.get("dates", []):
                for g in dd.get("games", []):
                    if (g.get("status") or {}).get("codedGameState") != "F": continue
                    side = "home" if g["teams"]["home"]["team"]["id"] == tid else "away"
                    win = g["teams"][side].get("isWinner")
                    if win is None: continue
                    out.append([g.get("officialDate") or dd["date"], 1 if win else 0])
            json.dump(out, open(fn, "w")); time.sleep(0.2)
            return out
        except Exception:
            time.sleep(2 + 2 * a)
    return []

def _frac(yr, a, b):
    s0, s1 = SPAN[yr]
    a = max(a, s0); b = min(b, s1)
    if b <= a: return 0.0
    return (b - a).days / max((s1 - s0).days, 1)

def seasons(start, end=None):
    a = _d(max(start, "1998-01-01")); b = _d(end) if end else date(LAST_SEASON, 12, 31)
    tot = 0.0
    for yr in range(a.year, min(b.year, LAST_SEASON) + 1):
        tot += _frac(yr, max(a, date(yr, 1, 1)), min(b, date(yr, 12, 31)))
    return round(tot, 2)

def record(tid, start, end, wl):
    """wl: {(tid, yr): [w, l, divrank1]} full-season table"""
    a = _d(max(start, "1998-01-01")); b = _d(end) if end else date(LAST_SEASON, 12, 31)
    w = l = div = 0; octs = []
    for yr in range(a.year, min(b.year, LAST_SEASON) + 1):
        s0, s1 = SPAN[yr]
        lo, hi = max(a, date(yr, 1, 1)), min(b, date(yr, 12, 31))
        if hi < s0 or lo > s1: continue                      # off-season only
        full = lo <= s0 and hi >= s1
        if full:
            rec = wl.get((tid, yr))
            if rec: w += rec[0]; l += rec[1]
        else:
            for gd, win in _games(tid, yr):
                g = _d(gd)
                if lo <= g <= hi:
                    if win: w += 1
                    else: l += 1
        if hi >= s1:                                          # held the seat when the season ended
            rec = wl.get((tid, yr))
            if rec: div += rec[2]
            octs.append(yr)
    return w, l, div, octs
