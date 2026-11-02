"""Fetch the MLB Stats API transaction feed (Jan 2025 - today) and the
people records (currentTeam, active, birthDate, name) for a list of ids.
Writes statsapi_cache/tx.json and statsapi_cache/people.json. Used by
desk_data.py (club/status refresh, v5.9) and the page-currency checks.
Run standalone; desk_data.py reads the cache and refreshes it if stale."""
import json, os, sys, time, datetime, urllib.request
C = "/work/statsapi_cache"
os.makedirs(C, exist_ok=True)
def get(u, tries=4):
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
        except Exception as e:
            time.sleep(2 + 3 * a)
    return None

def fetch_tx(start="2025-01-01", end=None):
    end = end or datetime.date.today().isoformat()
    out = []
    d = datetime.date.fromisoformat(start)
    e = datetime.date.fromisoformat(end)
    while d <= e:
        d2 = min(d + datetime.timedelta(days=30), e)
        r = get(f"https://statsapi.mlb.com/api/v1/transactions?startDate={d}&endDate={d2}")
        if r is None: raise SystemExit(f"tx fetch failed {d}")
        out += r.get("transactions", [])
        d = d2 + datetime.timedelta(days=1)
    seen, uniq = set(), []
    for t in out:
        if t.get("id") in seen: continue
        seen.add(t.get("id")); uniq.append(t)
    json.dump(dict(asof=end, tx=uniq), open(f"{C}/tx.json", "w"))
    print("tx rows", len(uniq), "through", end)
    return uniq

def fetch_people(ids):
    ids = sorted({int(i) for i in ids})
    out = {}
    for i in range(0, len(ids), 120):
        ch = ids[i:i + 120]
        r = get("https://statsapi.mlb.com/api/v1/people?personIds=" + ",".join(map(str, ch)) + "&hydrate=currentTeam,rosterEntries")
        if r is None: continue
        for p in r.get("people", []):
            ct = p.get("currentTeam") or {}
            # open roster entries on a list that removes a player from play
            # (restricted, ineligible, suspended): [status, since]
            lists = [[(e.get("status") or {}).get("description"), e.get("statusDate") or e.get("startDate")]
                     for e in p.get("rosterEntries", []) if not e.get("endDate")
                     and any(w in ((e.get("status") or {}).get("description") or "").lower() for w in ("restricted", "ineligible", "suspended"))]
            out[str(p["id"])] = dict(name=p.get("fullName"), active=p.get("active"), birth=p.get("birthDate"),
                                     team=ct.get("id"), parent=ct.get("parentOrgId"), pos=(p.get("primaryPosition") or {}).get("abbreviation"),
                                     last=p.get("lastPlayedDate"), debut=p.get("mlbDebutDate"), death=p.get("deathDate"), lists=lists)
        time.sleep(0.2)
    return out

if __name__ == "__main__":
    fetch_tx()
