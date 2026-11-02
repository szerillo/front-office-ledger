"""Clean transaction-feed text for display (v5.9).

The feed carries some broken rows: names dropped from a trade ("traded  to
Los Angeles Dodgers for ."), a signing with an empty tail ("signed free
agent RHP Justin Verlander,  and."), and three-club deals written by the
minor-league affiliates ("Springfield Cardinals Traded RF Alex Castellanos
to Chattanooga Lookouts and Los Angeles Dodgers Traded cash and SS Rafael
Furcal to St. Louis Cardinals."). clean() picks the best row among the
duplicates of one transaction, keeps only the clause about the player when
affiliates share the sentence, repairs the empty-name gaps, and falls back to
a plain sentence built from the structured from/to clubs."""
import re
_GARBLE = [re.compile(p) for p in (r"\s{2,}", r"\bfor\s*\.", r",\s*and\s*\.", r",\s+and\s+to\b", r"^traded\b", r"^signed\b",
                                     r"\bTraded\b", r"\bto\s*\.")]
def garble_score(desc):
    d = desc or ""
    return sum(1 for p in _GARBLE if p.search(d)) + (1 if not d.strip() else 0)

def _clause(desc, name):
    last = (name or "").split()[-1] if name else ""
    parts = re.split(r";\s*|\s+and\s+(?=(?:[A-Z][\w.'-]*\s){1,4}Traded\b)", desc)
    if len(parts) < 2: return desc
    hit = [p for p in parts if last and last in p]
    if not hit: return desc
    c = hit[0].strip().rstrip(".")
    return c + "."

def clean(desc, name=None, typ=None, from_team=None, to_team=None, alts=()):
    cands = [d for d in [desc, *alts] if d]
    if not cands: cands = [""]
    best = min(cands, key=lambda d: (garble_score(d), -len(d)))
    d = best
    if re.search(r"\bTraded\b", d):
        d = _clause(d, name)
        d = re.sub(r"\bTraded\b", "traded", d)
    d = re.sub(r",\s+and\s*\.", ".", d)
    d = re.sub(r",\s+and\s+(?=to\b)", " ", d)
    d = re.sub(r"\s{2,}", " ", d).strip()
    if garble_score(d) == 0:
        return d
    if typ == "Trade":
        if from_team and to_team and name: return f"{from_team} traded {name} to {to_team}."
        if to_team and name: return f"{name} was acquired by the {to_team} in a trade."
    if typ == "Signed as Free Agent" and to_team and name:
        return f"{to_team} signed free agent {name}."
    return re.sub(r"\s+for\s*\.$", ".", d)
