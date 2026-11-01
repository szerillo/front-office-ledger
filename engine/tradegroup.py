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
               "for SS Amed Rosario, SS Andres Gimenez, RHP Josh Wolf and OF Isaiah Greene. "
               "(curated repair: the league feed files only a garbled Lindor row)"),
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
