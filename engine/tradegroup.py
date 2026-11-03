"""Shared transaction hygiene for the scoring engines (v5.1).

1. dedupe_rows: the feed carries exact duplicate rows (the same waiver claim
   filed three or four times: Whitlock 2020-12-10, Aguilar, Perez). Scoring
   each copy counted the claim several times.

2. group_trades: trades used to be grouped by (date, description). The feed
   sometimes files ONE trade under several descriptions, so a deal split into
   fragments: one fragment with the club's outgoing player and no return
   (Halladay: "Toronto got nothing, -12.7"), or a second, garbled copy of the
   same incoming player ("traded SS Jake Cronenworth, , , , and to San Diego
   Padres"), which double-counted him. Groups are now merged when, for the
   seat being graded, they fall within one day of each other with an
   overlapping counterparty AND either share a player or are complementary
   (one has only outgoing players, the other only incoming).

Both functions are deterministic; used by sweep_score.py, hist_score.py,
trade_book.py.
"""
from datetime import date
import json as _json, os as _os

_CFG = _json.load(open("/work/regimes.json"))
_NAMES = {r["teamId"]: ({r["team"]} | set(_CFG["aliases"].get(str(r["teamId"]), []))) for r in _CFG["regimes"]}
# rows recovered from the daily feed where a trade's return was filed under
# minor-league affiliates (trade_repair.py); merged per club and window
_REPAIRS = _json.load(open("/work/trade_repairs.json")) if _os.path.exists("/work/trade_repairs.json") else []


# Trades the league feed files incompletely. The Lindor/Carrasco deal exists
# only as one garbled row ("traded SS Francisco Lindor to New York Mets.")
# with no origin club and none of the four players Cleveland received, which
# credited the Mets with Lindor for nothing and Cleveland with nothing at all.
REPAIRS = [
    dict(date="2021-01-07",
         desc=("Cleveland Indians traded SS Francisco Lindor and RHP Carlos Carrasco to New York Mets "
               "for SS Amed Rosario, SS Andres Gimenez, RHP Josh Wolf and OF Isaiah Greene."),
         teams={114: "Cleveland Indians", 121: "New York Mets"},
         moves=[("596019", "Francisco Lindor", "Cleveland Indians", "New York Mets"),
                ("471911", "Carlos Carrasco", "Cleveland Indians", "New York Mets"),
                ("642708", "Amed Rosario", "New York Mets", "Cleveland Indians"),
                ("665926", "Andres Gimenez", "New York Mets", "Cleveland Indians"),
                ("683181", "Josh Wolf", "New York Mets", "Cleveland Indians"),
                ("693309", "Isaiah Greene", "New York Mets", "Cleveland Indians")]),
]


_N2T = {}
for _r in _CFG["regimes"]:
    for _n in _NAMES[_r["teamId"]]: _N2T[_n] = _r["teamId"]
_LEGS = None
def _legs():
    """every trade leg in the archive (plus repairs), by player, for resolving
    players who only pass through a club inside a linked same-day deal"""
    global _LEGS
    if _LEGS is not None: return _LEGS
    import sqlite3 as _sq
    con = _sq.connect("/work/ledger.sqlite")
    _LEGS = {}
    seen = set()
    rows = [dict(zip(("date", "person_id", "from_team", "to_team"), x)) for x in
            con.execute("select date, person_id, from_team, to_team from sweep_tx where type_desc='Trade' and person_id is not null")]
    rows += [dict(date=r["date"], person_id=r["person_id"], from_team=r["from_team"], to_team=r["to_team"]) for r in _REPAIRS]
    for r in rows:
        a, b = _N2T.get(r["from_team"]), _N2T.get(r["to_team"])
        if not a or not b or a == b: continue
        k = (r["date"], str(r["person_id"]), a, b)
        if k in seen: continue
        seen.add(k)
        _LEGS.setdefault(str(r["person_id"]), []).append((_d(r["date"]), a, b, r["from_team"], r["to_team"]))
    return _LEGS

def _resolve_pass_through(rows, tid):
    """A player traded A->S and S->B within a day only passed through S (the
    feed files three-team deals as legs; linked same-day flips work the same
    way). S neither receives nor surrenders him; A's surrender is valued at B
    and B's receipt comes from A, so every seat still mirrors."""
    legs = _legs(); out = []
    for r in rows:
        if r.get("type_desc") != "Trade" or not r.get("person_id"):
            out.append(r); continue
        L = legs.get(str(r["person_id"]), [])
        dd = _d(r["date"]); fr, to = _N2T.get(r.get("from_team")), _N2T.get(r.get("to_team"))
        near = [x for x in L if dd and x[0] and abs((x[0] - dd).days) <= 1]
        drop = False; r2 = dict(r)
        # this row arrives at a pass-through club S = to
        nxt = [x for x in near if x[1] == to and x[2] != fr] if to else []
        prv = [x for x in near if x[2] == fr and x[1] != to] if fr else []
        if nxt and fr:
            if to == tid: drop = True                      # I am S: never really had him
            else: r2["to_team"] = nxt[0][4]                # I am A: he went on to B
        if prv and to and not drop:
            if fr == tid: drop = True                      # I am S
            else: r2["from_team"] = prv[0][3]              # I am B: he came from A
        if not drop: out.append(r2)
    return out


def dedupe_rows(rows, tid=None, lo="0000", hi="9999"):
    rows = list(rows)
    # curated repairs for this club and window
    if tid is not None:
        for rp in REPAIRS:
            if tid in rp["teams"] and lo <= rp["date"] <= hi:
                pids = {m[0] for m in rp["moves"]}
                rows = [r for r in rows if not (r.get("type_desc") == "Trade" and str(r.get("person_id")) in pids
                                                and abs((_d(r["date"]) - _d(rp["date"])).days) <= 3)]
                for pid, nm, fr, to in rp["moves"]:
                    rows.append(dict(date=rp["date"], person_id=pid, person_name=nm, from_team=fr, to_team=to,
                                     type_desc="Trade", description=rp["desc"], team_id=tid))
    if tid is not None and _REPAIRS:
        nm = _NAMES.get(tid, set())
        for rr in _REPAIRS:
            if lo <= rr["date"] <= hi and (rr["from_team"] in nm or rr["to_team"] in nm):
                rows.append(dict(rr, team_id=tid))
    # a trade row missing a club is a garbled duplicate when a complete row
    # for the same player sits within three days (Cronenworth, Lynn, Vesia...)
    complete = {}
    for r in rows:
        if r.get("type_desc") == "Trade" and r.get("from_team") and r.get("to_team"):
            complete.setdefault(str(r.get("person_id")), []).append(_d(r["date"]))
    kept = []
    for r in rows:
        if r.get("type_desc") == "Trade" and not (r.get("from_team") and r.get("to_team")):
            dd = _d(r["date"])
            if dd and any(c and abs((c - dd).days) <= 3 for c in complete.get(str(r.get("person_id")), [])):
                continue
        kept.append(r)
    rows = kept
    if tid is not None:
        rows = _resolve_pass_through(rows, tid)
    if lo and lo > "0000":
        C = _completions()
        rows = [r for r in rows if not (r.get("type_desc") == "Trade" and r.get("person_id")
                                        and C.get((r.get("date"), str(r.get("person_id"))), "9999") < lo)]
    seen, out = set(), []
    for r in rows:
        k = (r.get("date"), r.get("person_id"), r.get("type_desc"), r.get("from_team"),
             r.get("to_team"), (r.get("description") or "").strip())
        k2 = (r.get("date"), r.get("person_id"), r.get("type_desc"), r.get("from_team"), r.get("to_team"))
        if r.get("person_id") and r.get("type_desc") == "Trade":
            k = k2                      # one player, one move, whatever the filing text
        if r.get("person_id") and r.get("type_desc") in ("Claimed Off Waivers", "Rule 5 Selection"):
            # a claim is one event: blank and filled copies of the losing club collapse
            k = (r.get("date"), r.get("person_id"), r.get("type_desc"), r.get("to_team"))
        if k in seen: continue
        seen.add(k); out.append(r)
    return out



_PAIRS = None
def _club_pairs():
    """(date, {club a, club b}) for every trade leg between two MLB clubs:
    lets a seat see that its two one-way legs on the same day are halves of a
    three-team deal (v5.4: SD sent Ross and a PTBNL to WSH, WSH sent Souza to
    TB, TB sent Myers to SD; the feed files three separate legs)."""
    global _PAIRS
    if _PAIRS is not None: return _PAIRS
    _PAIRS = set()
    for pid, L in _legs().items():
        for (dd, a, b, fa, fb) in L:
            if dd: _PAIRS.add((dd, frozenset((a, b))))
    return _PAIRS

def _bare_leg(G):
    """a one-way leg whose filing names no return at all ("X traded P to Y."):
    the shape the feed uses for the legs of a three-team deal. A leg "for cash"
    or "for a player to be named later" is a complete two-club deal."""
    return (not G["ins"] or not G["outs"]) and " for " not in (G["desc"] or "")

def _closed_deal(G):
    """a deal the filing itself closes with cash or future considerations"""
    d = (G["desc"] or "").lower()
    return " for cash" in d or " for future considerations" in d

_COMPL = None
def _completions():
    """(date, person_id) -> date of the deal that promised him, for every
    player-to-be-named-later completion in the feed (v5.4). A completion that
    finishes a deal made before a regime's window belongs to the predecessor,
    so both seats of every pairing count the same deals."""
    global _COMPL
    if _COMPL is not None: return _COMPL
    import sqlite3 as _sq
    con = _sq.connect("/work/ledger.sqlite")
    rows = con.execute("select date, person_id, from_team, to_team, description from sweep_tx "
                       "where type_desc='Trade' and person_id is not null").fetchall()
    promises = []
    for d, pid, fr, to, desc in rows:
        snd = _ptbnl_sender(desc)
        if not snd: continue
        st = _N2T.get(snd)
        clubs = {_N2T.get(fr), _N2T.get(to)} - {None}
        if st and st in clubs and len(clubs) == 2:
            promises.append((_d(d), st, (clubs - {st}).pop()))
    promises = sorted(set(promises))
    _COMPL = {}
    for d, pid, fr, to, desc in rows:
        if " for " in (desc or "") or "Player To Be Named Later" in (desc or ""): continue
        a, b, dd = _N2T.get(fr), _N2T.get(to), _d(d)
        if not a or not b or not dd: continue
        cands = [p for p in promises if p[1] == a and p[2] == b and 0 < (dd - p[0]).days <= 400]
        if cands: _COMPL[(d, str(pid))] = max(cands)[0].isoformat()
    return _COMPL

def _ptbnl_sender(desc):
    """club name that owes the player to be named later in a trade filing"""
    if "Player To Be Named Later" not in (desc or ""): return None
    head, _, tail = desc.partition(" for ")
    if "Player To Be Named Later" in head:
        return head.split(" traded ")[0].strip()
    i = head.rfind(" to ")
    return head[i + 4:].strip().rstrip(".") if i > 0 else None

def _d(s):
    try: return date.fromisoformat(s[:10])
    except Exception: return None


def group_trades(rows, names):
    """rows: Trade rows touching the seat (club `names`). Returns a list of
    (date, description, rows) groups, merged as described above."""
    base = {}
    for r in rows:
        base.setdefault((r["date"], r["description"]), []).append(r)
    groups = [dict(d=k[0], desc=k[1], rows=v) for k, v in base.items()]
    for g in groups:
        ins = {x["person_id"] for x in g["rows"] if x["to_team"] in names and x["person_id"]}
        outs = {x["person_id"] for x in g["rows"] if x["from_team"] in names and x["person_id"]}
        cps = set()
        for x in g["rows"]:
            if x["to_team"] in names and x["from_team"]: cps.add(x["from_team"])
            if x["from_team"] in names and x["to_team"]: cps.add(x["to_team"])
        g.update(ins=ins, outs=outs, cps=cps, dd=_d(g["d"] or ""))
    # union-find
    parent = list(range(len(groups)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    order = sorted(range(len(groups)), key=lambda i: groups[i]["d"] or "")
    for a_i, a in enumerate(order):
        A = groups[a]
        for b in order[a_i + 1:]:
            B = groups[b]
            if not A["dd"] or not B["dd"]: continue
            if (B["dd"] - A["dd"]).days > 1: break
            shared = (A["ins"] | A["outs"]) & (B["ins"] | B["outs"])
            complementary = ((not A["ins"] and not B["outs"]) or (not A["outs"] and not B["ins"]))
            # a shared player links the legs of a multi-team deal even across
            # different counterparties; complementary halves need a common one
            if shared or (complementary and (A["cps"] & B["cps"])):
                parent[find(a)] = find(b)
            # v5.4: three-team deals filed as separate legs. Two of this seat's
            # same-day legs with different counterparties X and Y, at least one
            # of them one-way, belong to one deal when X and Y also traded that day
            elif (A["cps"] and B["cps"] and not (A["cps"] & B["cps"])
                  and (_bare_leg(A) or _bare_leg(B)) and not (_closed_deal(A) or _closed_deal(B))):
                P = _club_pairs()
                if any((dd, frozenset((_N2T.get(x), _N2T.get(y)))) in P
                       for x in A["cps"] for y in B["cps"]
                       for dd in (A["dd"], B["dd"]) if _N2T.get(x) and _N2T.get(y)):
                    parent[find(a)] = find(b)
    # v5.4: a player to be named later completes the deal that promised him.
    # A one-way leg from the club that owed the PTBNL to the same counterparty,
    # within 400 days, joins that deal (Trea Turner, June 2015, joins the
    # December 2014 Myers deal; graded alone he read as a 25-win giveaway).
    for i, H in enumerate(groups):
        snd = _ptbnl_sender(H["desc"])
        if not snd or not H["dd"]: continue
        for j, G in enumerate(groups):
            if j == i or not G["dd"] or "Player To Be Named Later" in (G["desc"] or ""): continue
            gap = (G["dd"] - H["dd"]).days
            if not (0 < gap <= 400): continue
            if not (G["cps"] and G["cps"] <= H["cps"]): continue
            one_way = (G["outs"] and not G["ins"]) or (G["ins"] and not G["outs"])
            if not one_way or " for " in (G["desc"] or ""): continue
            # direction: the PTBNL moves from the club that owed him
            mover = [x for x in G["rows"] if x.get("person_id")]
            if mover and mover[0].get("from_team") == snd or (mover and _N2T.get(mover[0].get("from_team")) == _N2T.get(snd)):
                parent[find(j)] = find(i)
    merged = {}
    for i in order:
        root = find(i)
        m = merged.setdefault(root, dict(d=groups[i]["d"], descs=[], rows=[]))
        m["d"] = min(m["d"], groups[i]["d"]) if m["d"] else groups[i]["d"]
        if groups[i]["desc"]: m["descs"].append(groups[i]["desc"])
        m["rows"].extend(groups[i]["rows"])
    out = []
    for m in merged.values():
        # the longest description is the most complete one
        desc = max(m["descs"], key=lambda s: len((s or "").replace(",", "").strip()), default="")
        # multi-team deals: a player who comes in and goes straight back out
        # in the same deal only passed through this seat (Gregorius in the
        # Choo/Bauer three-way); he is neither received nor surrendered here
        ins_ = {x["person_id"] for x in m["rows"] if x["to_team"] in names and x["person_id"]}
        outs_ = {x["person_id"] for x in m["rows"] if x["from_team"] in names and x["person_id"]}
        thru = ins_ & outs_
        rows_ = [x for x in m["rows"] if x["person_id"] not in thru] if thru else m["rows"]
        if rows_: out.append((m["d"], desc, rows_))
    out.sort(key=lambda t: t[0] or "")
    return out
