"""Contract -> player id resolution shared by contract_book.py (engine) and
desk_data.py (the page's DESK.book), v5.9.

The page used to join on name alone and keep the namesake with the most WAR
around the signing, so the Dodgers' catcher Will Smith carried LHP Will
Smith's Rangers and Royals deals and a 31-year-old catcher carried the
Brewers prospect Luis Lara's extension. Both books now resolve the same
way, by name AND club AND era AND career stage:
  1. explicit overrides (OVERRIDE, keyed by normalized name, club, first
     season) for cases no record can settle;
  2. the namesake who played for the contract's club in the seasons around
     its start (start-1 .. start+1), then over its full term;
  3. career stage: a free-agent deal goes to the namesake with an MLB career
     before it (Roberto Hernandez's 2007 Cleveland deal is the veteran
     reliever's, not Fausto Carmona's); an extension goes to the namesake
     already in that organization;
  4. the namesake currently in the club's organization (Stats API currentTeam);
  5. the most active namesake around the start.
check_name_collisions.py lists any remaining row whose id never played for
the club while a namesake did."""
import json, unicodedata
from collections import defaultdict
ROOT = "/work"
_cfg = json.load(open(f"{ROOT}/regimes.json"))
NAMES = {r["abbr"]: set(_cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in _cfg["regimes"]}
TID2AB = {r["teamId"]: r["abbr"] for r in _cfg["regimes"]}

def norm(nm):
    x = unicodedata.normalize("NFKD", nm or "").encode("ascii", "ignore").decode()
    return x.lower().replace(".", "").replace(" jr", "").replace(" sr", "").replace(" iii", "").replace(" ii", "").strip()

# (normalized name, club, first season) -> pid. Only for cases the records
# cannot settle (pre-debut deals, namesakes on the same club).
OVERRIDE = {
    ("luis lara", "MIL", 2026): 800325,        # Brewers prospect (b. 2004), 7 yr / $31M, Jun 2026
    ("roberto hernandez", "CLE", 2007): 115832, # veteran RHP (b. 1964), 1 yr / $3.5M, Dec 2006
    ("chris young", "NYM", 2014): 455759,       # OF Chris Young, 1 yr / $7.25M, Dec 2013
    ("chris young", "NYM", 2011): 432934,       # RHP Chris Young, 1 yr / $1.1M
    ("chris young", "KC", 2015): 432934,        # RHP
    ("chris young", "KC", 2016): 432934,        # RHP, 2 yr / $11.5M
    ("chris young", "LAA", 2018): 455759,       # OF
    ("will smith", "TEX", 2023): 519293,        # LHP
    ("will smith", "KC", 2024): 519293,         # LHP
    ("will smith", "ATL", 2020): 519293,        # LHP
    ("will smith", "LAD", 2024): 669257,        # C, 10 yr / $140M extension
    ("alex gonzalez", "CIN", 2007): 136460,     # Alex Gonzalez (b. 1977)
    ("luis garcia", "NYM", 2026): 472610,       # RHP Luis García, signed Jan 21 2026
    ("luis garcia", "LAA", 2024): 472610,       # RHP Luis García
}

_PEOPLE = None
def _people():
    global _PEOPLE
    if _PEOPLE is None:
        try: _PEOPLE = json.load(open(f"{ROOT}/statsapi_cache/people.json"))
        except Exception: _PEOPLE = {}
    return _PEOPLE

class Resolver:
    def __init__(self, lvm, extra=()):
        """lvm: {pid: {"name", "rows": [(season, club name, war), ...]}};
        extra: (name, pid) pairs for players without value rows (prospects)"""
        self.lvm = lvm
        self.n2p = defaultdict(set)
        for pid, rec in lvm.items(): self.n2p[norm(rec.get("name", ""))].add(int(pid))
        for nm, pid in extra: self.n2p[norm(nm)].add(int(pid))
    def rows(self, pid): return (self.lvm.get(pid) or {}).get("rows", [])
    def resolve(self, name, ab, start, kind="fa", yrs=1):
        key = (norm(name), ab, start)
        if key in OVERRIDE: return OVERRIDE[key]
        c = sorted(self.n2p.get(norm(name), ()))
        if len(c) <= 1: return c[0] if c else None
        clubs = NAMES.get(ab, set())
        ppl = _people()
        def score(pid):
            rows = self.rows(pid)
            near = sum(1 for r in rows if start - 1 <= r[0] <= start + 1 and r[1] in clubs)
            term = sum(1 for r in rows if start - 1 <= r[0] <= start + max(yrs, 1) and r[1] in clubs)
            prior = len({r[0] for r in rows if r[0] < start})
            if kind == "fa": stage = 1 if prior >= 3 else 0
            else: stage = 1 if any(r[0] < start + 1 and r[1] in clubs for r in rows) else 0
            rec = ppl.get(str(pid)) or {}
            org = TID2AB.get(rec.get("team")) or TID2AB.get(rec.get("parent"))
            act = sum(abs(r[2]) for r in rows if start - 2 <= r[0] <= start + 1)
            return (near, term, stage, 1 if org == ab else 0, act)
        return max(c, key=score)
