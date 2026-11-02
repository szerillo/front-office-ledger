"""Regenerate the prototype's data blocks from sweep_results.json:
AUTO_REGIMES, DEV_MAP, EXT_MAP, PLAYER_MOVES/NAMES/RANKS. UI code in the
page is already final; this swaps data only. Rebuilt Oct 2026 after the
container reclaim (original regen lived outside the repo; lesson learned,
this one ships in ingest/)."""
import json, sqlite3

P = "/work/front-office-ledger-prototype.html"
res = json.load(open("/work/sweep_results.json"))
s = open(P).read()

CH_LABEL = {"trade": "Trade", "draft": "Draft pick vs. slot",
            "waiver": "Waiver / Rule 5", "fa": "Free agency vs. contract cost",
            "intl": "International amateur class", "ext": "Extension vs. the path it replaced"}
def esc(x): return (x or "").replace("\\", "").replace('"', '&quot;').replace("\n", " ")

def build_styles(res):
    """Two distinctive style traits per regime, scored against the league.
    Wider vocabulary, no boilerplate: each trait is the regime's biggest
    z-score deviation in its group (development / acquisition taste /
    market skill / temperament)."""
    import statistics
    def metric(r, fn):
        try:
            v = fn(r)
            return float(v) if v is not None else None
        except Exception:
            return None
    mix = lambda d: (d.get("pit", 0) - d.get("bat", 0)) / (abs(d.get("pit", 0)) + abs(d.get("bat", 0)) + 2.0)
    CANDS = [
        # key, group, extractor, label if high, label if low
        ("devPit", "dev", lambda r: (r["dna"].get("devPit") or {}).get("v"), "A pitching lab", "Arms stall here"),
        ("devBat", "dev", lambda r: (r["dna"].get("devBat") or {}).get("v"), "Bats bloom here", "Hitters plateau here"),
        ("devDef", "dev", lambda r: (r["dna"].get("devDef") or {}).get("v"), "Glove whisperers", "Defense fades here"),
        ("draftMix", "taste", lambda r: mix(r["dna"].get("draft", {})), "Drafts arms first", "Drafts bats first"),
        ("tradeMix", "taste", lambda r: mix(r["dna"].get("trade_in", {})), "Imports pitching", "Trades for thump"),
        ("faMix", "taste", lambda r: mix(r["dna"].get("fa", {})), "Shops for arms", "Spends on bats"),
        ("overslot", "taste", lambda r: (r["dna"].get("draftRoom") or {}).get("overslot"), "Swings over slot", "Plays the slot book straight"),
        ("prep", "taste", lambda r: (r["dna"].get("draftRoom") or {}).get("prep"), "Prep-school dreamer", "College polish only"),
        ("buyLow", "temperament", lambda r: (r["dna"].get("buyLow") or {}).get("rate"), "Bargain-bin believer", "Pays retail"),
        ("inj", "temperament", lambda r: ((r["dna"].get("inj") or {}).get("pit", 0) + (r["dna"].get("inj") or {}).get("bat", 0)), "Lives in the training room", "Keeps bodies on the field"),   # per covered season already (archetype.py)
        ("vol", "temperament", lambda r: r["chan"]["trade"]["n"] / max(r["seasons"], 1), "Never stops dealing", "Patient to a fault"),
        ("trSkill", "skill", lambda r: r["chan"]["trade"]["net"] / max(r["seasons"], 1), "Wins the trade table", "Bleeds value in trades"),
        ("drSkill", "skill", lambda r: r["chan"]["draft"]["net"] / max(r["seasons"], 1), "A draft-room edge", "Draft-room drag"),
        ("intlSkill", "skill", lambda r: r["chan"]["intl"]["net"] / max(r["seasons"], 1), "An international pipeline", "Quiet internationally"),
        ("extSkill", "skill", lambda r: r["chan"]["ext"]["net"] / max(r["seasons"], 1), "Extends its own early and well", "Extensions bite back here"),
    ]
    stats = {}
    for key, grp, fn, hi, lo in CANDS:
        vals = [v for r in res if (v := metric(r, fn)) is not None]
        if len(vals) >= 6 and statistics.pstdev(vals) > 1e-9:
            stats[key] = (statistics.mean(vals), statistics.pstdev(vals))
    out = {}
    for r in res:
        scored = []
        for key, grp, fn, hi, lo in CANDS:
            if key not in stats: continue
            v = metric(r, fn)
            if v is None: continue
            mu, sd = stats[key]
            z = (v - mu) / sd
            if abs(z) >= 0.6:
                scored.append((abs(z), grp, hi if z > 0 else lo))
        scored.sort(reverse=True)
        picks, groups = [], set()
        for az, grp, label in scored:
            if grp in groups: continue
            picks.append(label); groups.add(grp)
            if len(picks) == 2: break
        out[r["teamId"]] = picks if picks else ["A balanced book"]
    return out

STYLES = build_styles(res)

# v5.9: one number per deal. Card trade entries read the trade book's seat
# value (trade_book.py, the same engine math), so a card, the "every trade"
# table, the H2H list and the trees agree; and a trade sits under "best" only
# when positive and under "worst" only when negative (r2 audit items 3, 16).
_TBX = {}
_cfg0 = json.load(open("/work/regimes.json"))
_TID2AB0 = {x["teamId"]: x["abbr"] for x in _cfg0["regimes"]}
for _d, _seats in json.load(open("/work/trade_book.json"))["trades"]:
    for _st in _seats:
        _TBX.setdefault((_d, _st[0]), []).append(_st)
CUR_TID = [None]
def tb_net(d):
    """the trade book's seat value for a card's trade decision, else its own"""
    if d.get("ch") != "trade" or CUR_TID[0] is None: return d["net"]
    seats = _TBX.get((d["d"][:10], _TID2AB0.get(CUR_TID[0])), [])
    pids = {str(p) for p in (d.get("pids") or []) if p}
    hit = [st for st in seats if pids & {str(p) for p, _ in st[2] + st[3]}]
    if len(hit) == 1 or (hit and len(seats) == 1): return round(hit[0][1], 1)
    if not pids and len(seats) == 1: return round(seats[0][1], 1)
    return d["net"]
def by_sign(best, worst):
    """re-sort a channel's best/worst lists by sign, one row per deal"""
    seen, rows = set(), []
    for e in best + worst:
        k = (e["d"], tuple(sorted(e.get("pids") or [])), e.get("h", "")[:60] if not e.get("pids") else "")
        if k in seen: continue
        seen.add(k); rows.append(e)
    b = sorted([e for e in rows if e["war"] > 0], key=lambda e: -e["war"])
    w = sorted([e for e in rows if e["war"] < 0], key=lambda e: e["war"])
    return b, w

def trade_note(d):
    base = f"Auto-scored: value in {d.get('vin', 0):+0.1f} vs value out {d.get('vout', 0):+0.1f} (control windows net of salary, 10%/yr discount)."
    a = d.get("att")
    if a and a.get("n_out"):
        gap = d.get("vout", 0) - a["out"]
        verdict = ("they beat their marks, so the deal cost more than a fair read at the time expected" if gap > 2.5
                   else "they fell short of their marks, so the outcome flatters the process" if gap < -2.5
                   else "they did about what their marks said")
        _n = a['n_out']
        base += (f" PROCESS CHECK: the {_n} ranked {'piece' if _n == 1 else 'pieces'} surrendered carried a Pipeline mark of about "
                 f"{a['out']:+0.1f} wins at the time; they realized {d.get('vout', 0):+0.1f} for the counterparty, so {verdict}.")
    if a and a.get("n_in"):
        base += f" Acquired ranked pieces were marked {a['inn']:+0.1f} at the time."
    return base

def row(d):
    r = dict(d=d["d"][:10], war=tb_net(d), real=True,
             open=d.get("unsettled", int(d["d"][:4]) >= 2021),
             t=CH_LABEL.get(d["ch"], "") + ("" if d["ch"] != "walk" else " · passive loss, shown for context, not graded"),
             h=esc(d["h"]) + ' <span class="badge-real">COMPUTED</span>')
    if d.get("sides"): r["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
    if d.get("pids"): r["pids"] = [str(p) for p in d["pids"] if p]
    if d.get("att"): r["att"] = d["att"]
    if d.get("comps"): r["comps"] = d["comps"]
    if d.get("proj"): r["proj"] = d["proj"]
    if d["ch"] == "trade": r["note"] = trade_note(d)
    r["ch"] = d["ch"]
    if d.get("st") is not None: r["st"] = d["st"]
    return r

def chan_ledgers(r):
    led = r.get("led", {})
    fa = r.get("fa_led", dict(best=[], worst=[]))
    ext_all = r.get("ext_tops", [])
    _tb, _tw = by_sign([row(d) for d in led.get("trade", {}).get("best", [])],
                       [row(d) for d in led.get("trade", {}).get("worst", [])])
    return dict(
        trade=dict(best=_tb, worst=_tw),
        draft=dict(best=[row(d) for d in led.get("draft", {}).get("best", [])],
                   worst=[row(d) for d in led.get("draft", {}).get("worst", [])]),
        waiver=dict(best=[row(d) for d in led.get("waiver", {}).get("best", [])],
                    worst=[row(d) for d in led.get("waiver", {}).get("worst", [])]),
        fa=dict(best=[row(d) for d in fa.get("best", [])],
                worst=[row(d) for d in fa.get("worst", [])]),
        intl=dict(best=[row(d) for d in r.get("intl_tops", [])], worst=[]),
        ext=dict(best=[row(d) for d in ext_all if d["net"] >= 0],
                 worst=[row(d) for d in ext_all if d["net"] < 0]),
    )

_START = {x["teamId"]: x["start"] for x in json.load(open("/work/regimes.json"))["regimes"]}
auto = []
CURATED_FULL = {}
for r in res:
    CUR_TID[0] = r["teamId"]
    badge = '<span class="badge-real">COMPUTED</span>'
    best_tr, worst_tr, acq, loss = [], [], [], []
    pool = (list(r["top"]) + list(r.get("fa_tops", [])) + list(r.get("intl_tops", []))
            + list(r.get("ext_tops", [])))
    for d in pool:
        e = dict(d=d["d"][:10], war=tb_net(d), real=True,
                 open=d.get("unsettled", int(d["d"][:4]) >= 2021),
                 t=(CH_LABEL.get(d["ch"], d["ch"]) + ""),
                 h=esc(d["h"]) + " " + badge)
        if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
        if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
        if d.get("comps"): e["comps"] = d["comps"]
        if d.get("proj"): e["proj"] = d["proj"]
        if d["ch"] == "trade":
            e["note"] = trade_note(d)
            (best_tr if e["war"] > 0 else worst_tr if e["war"] < 0 else []).append(e)
        else:
            (acq if d["net"] >= 0 else loss).append(e)
    best_tr.sort(key=lambda x: -x["war"]); worst_tr.sort(key=lambda x: x["war"])
    acq.sort(key=lambda x: -x["war"]); loss.sort(key=lambda x: x["war"])
    fa = r["chan"]["fa"]
    dev = r.get("dev", dict(net=0, g=None, n=0, farmNow=0, farmN=0, flows={}))
    flags = r.get("flags", [])
    auto.append(dict(
        id=r["id"], exec=r["exec"], startDate=_START.get(r["teamId"]),
        title="Head of Baseball Operations" + (" (interim)" if "interim" in flags else ""),
        team=r["team"], start=r["start"], seasons=round(r["seasons"], 1), seatSeasons=r.get("seatSeasons"), flags=flags,
        titles=r.get("titles", 0),
        forGrade=r["forGrade"], smallSample=r["seasons"] < 3, realCard=True,
        realBadge="COMPUTED · FULL LEDGER · THROUGH THE 2026 SEASON",
        success=dict(wpct=r["success"]["wpct"], div=r["success"]["div"],
                     po=r["success"].get("po"), sw=r["success"].get("sw"),
                     pen=r["success"].get("pen"), ws=r["success"].get("ws"),
                     g=r["success"]["g"]),
        chan=dict(draft=r["chan"]["draft"], trade=r["chan"]["trade"],
                  fa=fa, waiver=r["chan"]["waiver"], intl=r["chan"]["intl"],
                  ext=r["chan"]["ext"], ret=r["chan"].get("ret")),
        dev=dev,
        devTops=[dict(d=t["d"], war=t["net"], h=esc(t["h"])) for t in r.get("dev_tops", [])[:5]],
        surplus="≈$%dM" % round(r["total"] * 9.2),
        decisions=(r["chan"]["trade"]["n"] + r["chan"]["draft"]["n"]
                   + r["chan"]["waiver"]["n"] + fa["n"] + r["chan"]["intl"]["n"]
                   + r["chan"]["ext"]["n"]),
        cum=r.get("cum"),
        ledgers=dict(bestTrades=best_tr[:3], worstTrades=worst_tr[:3],
                     bestAcq=acq[:4], losses=loss[:3]),
        chanLedgers=chan_ledgers(r),
        allx=dict(r.get("allx", {}), fa=r.get("allx_fa", []), ext=r.get("allx_ext", []), intl=r.get("allx_intl", [])),
        walk=[row(d) for d in r.get("walk", [])],
        dna=r.get("dna", {}),
        dnaTags=STYLES.get(r["teamId"], []),
        h2h=r.get("h2h", [])[:10],
    ))
    if r["id"] in ("lad", "bal", "mil"):
        # v5.1: the three hand-verified cards are graded by the same engine as
        # every other card; their hand-written decision pages ride along as a
        # showcase. Move the computed card aside instead of listing it twice.
        CURATED_FULL[r["id"]] = auto.pop()
        CURATED_FULL[r["id"]]["h2h"] = r.get("h2h", [])

def swap(s, anchor, end_marker, payload):
    i = s.find(anchor)
    assert i >= 0, anchor
    j = s.find(end_marker, i)
    assert j > i, end_marker
    return s[:i] + anchor + payload + s[j:]

s = swap(s, "const AUTO_REGIMES = ", ";\n\n/* =", json.dumps(auto, separators=(",", ":"), ensure_ascii=False))

# ---- ARCHIVE (historical) regimes -> LB_HIST, full report cards ----
import os
hist_cards = []
if os.path.exists("/work/hist_results.json"):
    hres = json.load(open("/work/hist_results.json"))
    PS = json.load(open("/work/postseason.json"))
    def sgrade(pts):
        for thr, g in [(4.5,80),(3.4,75),(2.6,70),(1.9,65),(1.3,60),(0.7,55),
                       (0.0,50),(-0.8,45),(-1.6,40),(-2.6,35)]:
            if pts >= thr: return g
        return 30
    for r in hres:
        CUR_TID[0] = r["teamId"]
        badge = '<span class="badge-real">COMPUTED</span>'
        pool = list(r["top"]) + list(r.get("fa_tops", [])) + list(r.get("ext_tops", []))   # v5.9: archive FA and extensions are graded
        best_tr, worst_tr, acq, loss = [], [], [], []
        for d in pool:
            e = dict(d=d["d"][:10], war=tb_net(d), real=True,
                     open=d.get("unsettled", int(d["d"][:4]) >= 2021),
                     t=(CH_LABEL.get(d["ch"], d["ch"]) + " · archive sweep"),
                     h=esc(d["h"]) + " " + badge)
            if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
            if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
            if d.get("comps"): e["comps"] = d["comps"]
            if d.get("proj"): e["proj"] = d["proj"]
            if d["ch"] == "trade":
                e["note"] = trade_note(d)
                (best_tr if e["war"] > 0 else worst_tr if e["war"] < 0 else []).append(e)
            else:
                (acq if d["net"] >= 0 else loss).append(e)
        best_tr.sort(key=lambda x: -x["war"]); worst_tr.sort(key=lambda x: x["war"])
        acq.sort(key=lambda x: -x["war"]); loss.sort(key=lambda x: x["war"])
        # postseason detail over seasons held
        sd, ed = r["startDate"], r["endDate"]
        # October belongs to whoever held the seat when the season ended (v5.4)
        from regime_window import record as _rec
        _octs = _rec(r["teamId"], sd, ed, {})[3]
        s_first, s_last = (min(_octs), max(_octs)) if _octs else (1, 0)
        po = sw = pen = ws = 0
        for y in _octs:
            rec = PS.get(f'{r["teamId"]}:{y}')
            if rec:
                po += rec["berth"]; sw += rec["sw"]; pen += rec["pennant"]; ws += rec["ws"]
        suc = dict(r["success"])
        wpct = float(suc["wpct"]); seasons_i = max(1, s_last - s_first + 1)
        october = (1.2 * suc["div"] + 0.8 * po + 0.6 * sw + 1.5 * pen + 3.0 * ws) / seasons_i
        pts = (wpct - 0.500) * 40 + (october - 0.55)
        suc.update(po=po, sw=sw, pen=pen, ws=ws, g=sgrade(pts))
        fa = r["chan"]["fa"]
        def hrow(d):
            e = dict(d=d["d"][:10], war=tb_net(d), real=True, open=d.get("unsettled", int(d["d"][:4]) >= 2021),
                     t=CH_LABEL.get(d["ch"], d["ch"]) + (" · archive sweep" if d["ch"] != "walk" else " · passive loss, shown for context, not graded"),
                     h=esc(d["h"]) + ' <span class="badge-real">COMPUTED</span>')
            if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
            if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
            if d.get("comps"): e["comps"] = d["comps"]
            if d.get("proj"): e["proj"] = d["proj"]
            if d["ch"] == "trade": e["note"] = trade_note(d)
            return e
        led = r.get("led", {})
        _hb, _hw = by_sign([hrow(d) for d in led.get("trade", {}).get("best", [])],
                           [hrow(d) for d in led.get("trade", {}).get("worst", [])])
        chl = dict(
            trade=dict(best=_hb, worst=_hw),
            draft=dict(best=[hrow(d) for d in led.get("draft", {}).get("best", [])],
                       worst=[hrow(d) for d in led.get("draft", {}).get("worst", [])]),
            waiver=dict(best=[hrow(d) for d in led.get("waiver", {}).get("best", [])],
                        worst=[hrow(d) for d in led.get("waiver", {}).get("worst", [])]),
            fa=dict(best=[hrow(d) for d in r.get("fa_led", {}).get("best", [])],
                    worst=[hrow(d) for d in r.get("fa_led", {}).get("worst", [])]),
            intl=dict(best=[], worst=[]),
            ext=dict(best=[hrow(d) for d in r.get("ext_tops", []) if d.get("net", 0) >= 0 and d.get("sides")],
                     worst=[hrow(d) for d in r.get("ext_tops", []) if d.get("net", 0) < 0]),
        )
        flags = r.get("flags", [])
        # v5.9: the club's name in the seasons this regime ran (Cleveland
        # Indians for Hart and Shapiro, Tampa Bay Devil Rays for LaMar,
        # Florida Marlins for Beinfest through 2011); `team` stays the
        # franchise key the page matches on
        from era_names import era_team as _era
        _sd = r.get("startDate") or f'{r["start"]}-01-01'
        _y0 = int(_sd[:4]) + (1 if int(_sd[5:7]) >= 8 else 0)
        _y1 = max(_y0, int(str(r.get("endDate") or r["end"])[:4]) - (1 if (r.get("endDate") or "")[5:7] in ("01", "02", "03") else 0))
        _eras = []
        for _y in range(_y0, _y1 + 1):
            _n = _era(r["team"], _y)
            if _n not in _eras: _eras.append(_n)
        _team_era = " / ".join(_eras) if _eras else r["team"]
        hist_cards.append(dict(
            id=r["id"], exec=r["exec"], teamEra=_team_era,
            title="Head of Baseball Operations · archive regime",
            team=r["team"], start=r["start"], end=r["end"], era="hist",
            startDate=r.get("startDate"), endDate=r.get("endDate"),
            trueStart=r.get("trueStart"), flags=flags,
            seasons=round(r["seasons"], 1), seatSeasons=r.get("seatSeasons"), titles=ws,
            forGrade=r["forGrade"], smallSample=r["seasons"] < 3, realCard=True,
            realBadge="COMPUTED · ARCHIVE SWEEP · INTERNATIONAL AND RETENTION NOT SCORED",
            success=suc,
            chan=dict(draft=r["chan"]["draft"], trade=r["chan"]["trade"],
                      fa=r["chan"]["fa"],
                      waiver=r["chan"]["waiver"],
                      intl=dict(net=0.0, g=None, n=0), ext=r["chan"].get("ext") or dict(net=0.0, g=None, n=0)),
            surplus="≈$%dM" % round(r["total"] * 9.2),
            decisions=(r["chan"]["trade"]["n"] + r["chan"]["draft"]["n"]
                       + r["chan"]["waiver"]["n"] + fa["n"] + (r["chan"].get("ext") or {}).get("n", 0)),
            cum=r.get("cum"),
            ledgers=dict(bestTrades=best_tr[:3], worstTrades=worst_tr[:3],
                         bestAcq=acq[:4], losses=loss[:3]),
            chanLedgers=chl,
            allx=dict(r.get("allx", {}), fa=r.get("allx_fa", []), ext=r.get("allx_ext", [])),
            walk=[hrow(d) for d in r.get("walk", [])],
        ))
    # v5.9: the archive cards outgrew the deploy limit. Three lossless
    # compactions, expanded by the page on load (expandHistCards): ledger
    # entries that repeat a channel-ledger entry become references, the
    # COMPUTED badge is a token, and the full free-agent list keeps the priced
    # signings (the unpriced ones are counted)
    BADGE = ' <span class="badge-real">COMPUTED</span>'
    for c in hist_cards:
        idx = {}
        for ch, sides in c["chanLedgers"].items():
            for side, lst in sides.items():
                for i_, e in enumerate(lst): idx.setdefault((e.get("d"), e.get("h")), f"{ch}:{side}:{i_}")
        for k, lst in c["ledgers"].items():
            c["ledgers"][k] = [({"ref": idx[(e.get("d"), e.get("h"))]} if (e.get("d"), e.get("h")) in idx else e) for e in lst]
        def tok(o):
            if isinstance(o, dict):
                for kk, vv in o.items():
                    if kk == "h" and isinstance(vv, str): o[kk] = vv.replace(BADGE, " \u00a7C")
                    else: tok(vv)
            elif isinstance(o, list):
                for vv in o: tok(vv)
        tok(c["chanLedgers"]); tok(c["ledgers"]); tok(c["walk"])
        def trim(o):
            # every archive entry is real data; "open" is only stored when true
            if isinstance(o, dict):
                if o.get("real") is True: o.pop("real")
                if o.get("open") is False: o.pop("open")
                for vv in o.values(): trim(vv)
            elif isinstance(o, list):
                for vv in o: trim(vv)
        trim(c["chanLedgers"]); trim(c["ledgers"]); trim(c["walk"])
        fa_rows = c["allx"].get("fa") or []
        c["allx"]["fa"] = [x for x in fa_rows if len(x) > 2 and x[2] is not None]
        c["faUnpriced"] = len(fa_rows) - len(c["allx"]["fa"])
    s = swap(s, "const LB_HIST = ", ";\n\n/* =", json.dumps(hist_cards, separators=(",", ":"), ensure_ascii=False))
    print(f"archive cards: {len(hist_cards)}")

# ---- Deal Desk data pack ----
if os.path.exists("/work/desk_data.json"):
    desk = open("/work/desk_data.json").read()
    s = swap(s, "const DESK = ", ";\n\n// COMPUTED champions", desk)
    print("desk data pack spliced")
if os.path.exists("/work/scenarios.json") and "const SCEN = " in s:
    scen = open("/work/scenarios.json").read()
    s = swap(s, "const SCEN = ", "; // SCEN-END", scen)
    print("scenario pack spliced")
if os.path.exists("/work/gm_offseasons.json") and "const GMC = " in s:
    gmc = open("/work/gm_offseasons.json").read()
    s = swap(s, "const GMC = ", "; // GMC-END", gmc)
    print("gm offseason pack spliced")

# ---- computed champions + through lines ----
champ_cards_g = []
if os.path.exists("/work/champs_computed.json"):
    champs = json.load(open("/work/champs_computed.json"))
    champ_cards_g = champs["cards"]
    s = swap(s, "const CHAMPS_AUTO = ", ";\n\n// cross-title", json.dumps(champs["cards"], indent=0, ensure_ascii=False))
    s = swap(s, "const CHAMP_LINES = ", ";\n\nconst ALL_CHAMPS", json.dumps(champs["lines"], indent=0, ensure_ascii=False))
    print(f"computed champions: {len(champs['cards'])} cards + through lines")

devmap = {r["id"]: dict(r.get("dev", {}), tops=[dict(d=t["d"], war=t["net"], h=esc(t["h"]))
          for t in r.get("dev_tops", [])[:5]]) for r in res if r["id"] in ("lad", "bal", "mil")}
s = swap(s, "const DEV_MAP = ", ";\nconst devOf", json.dumps(devmap, indent=0, ensure_ascii=False))

extmap = {r["id"]: dict(r["chan"]["ext"], tops=[dict(d=t["d"], war=t["net"], h=esc(t["h"]))
          for t in r.get("ext_tops", [])[:4]]) for r in res if r["id"] in ("lad", "bal", "mil")}
s = swap(s, "const EXT_MAP = ", ";\nconst extOf", json.dumps(extmap, indent=0, ensure_ascii=False))

# player moves / names / ranks
cfg = json.load(open("/work/regimes.json"))
TID2 = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
NAME2AB = {}
for r0 in cfg["regimes"]:
    NAME2AB[r0["team"]] = r0["abbr"]
    for al in cfg["aliases"].get(str(r0["teamId"]), []):
        NAME2AB[al] = r0["abbr"]
def n2a(nm): return NAME2AB.get(nm, (nm or "")[:14])

pidset = set()
def collect(o):
    if isinstance(o, dict):
        for p in o.get("pids", []): pidset.add(str(p))
        for v in o.values(): collect(v)
    elif isinstance(o, list):
        for v in o: collect(v)
collect(auto)
collect(hist_cards)
# v5.7: every player in a trade since 2023 gets his move history, so recent
# chains (the ones people follow) end where the player stands, whichever
# trades the report cards happen to feature
for _t in json.load(open("/work/trade_book.json"))["trades"]:
    if _t[0] >= "2023-01-01":
        for _seat in _t[1]:
            for _pc in _seat[2] + _seat[3]: pidset.add(str(_pc[0]))
for _c in champ_cards_g:
    for _row in _c.get("roster", []):
        if len(_row) > 6 and _row[6] and _row[6] != "None":
            pidset.add(str(_row[6]))
con = sqlite3.connect("/work/ledger.sqlite")
MOVES, NAMES = {}, {}
if pidset:
    q = ("select person_id, person_name, date, team_id, type_desc, description, from_team, to_team from sweep_tx "
         "where person_id in (%s) and type_desc in ('Trade','Signed as Free Agent',"
         "'Declared Free Agency','Claimed Off Waivers','Rule 5 Selection','Released','Selected') "
         "order by date" % ",".join("?" * len(pidset)))
    seen = set()
    from feed_text import clean as _ft_clean, garble_score as _ft_score
    _MV_AT = {}
    def _trim120(t):
        return t if len(t) <= 120 else t[:120].rsplit(" ", 1)[0].rstrip(",;: ") + "…"
    for pid, nm, d, tid, ty, desc, ft, tt in con.execute(q, tuple(pidset)):
        pid = str(pid)
        # v5.3.2: a minor-league deal is a real move (Morel to the Mets in July
        # 2026); a contract selection counts only when it follows one
        if ty == "Signed as Free Agent" and "minor league" in (desc or "").lower(): ty = "Minor-league deal"
        if ty == "Selected":
            prev = MOVES.get(pid, [])
            if not prev or prev[-1][1] != "Minor-league deal" or n2a(tt) is None: continue
        k = (pid, d, ty)
        # v5.9: duplicate feed rows for one transaction: keep the cleanest
        # text (feed_text.py), never "traded  to Los Angeles Dodgers for ."
        _txt = _ft_clean(desc or "", nm, ty if ty != "Minor-league deal" else "Signed as Free Agent", ft, tt)
        if k in seen:
            _prev = _MV_AT.get(k)
            if _prev is not None and _ft_score(_prev[4]) > _ft_score(_txt): _prev[4] = esc(_trim120(_txt))
            continue
        seen.add(k)
        ab = TID2.get(tid, "?")
        fa_, ta_ = n2a(ft), n2a(tt)
        if ty == "Declared Free Agency" and not fa_: fa_ = ab
        if ty in ("Signed as Free Agent", "Claimed Off Waivers", "Rule 5 Selection") and not ta_: ta_ = ab
        NAMES.setdefault(pid, nm)
        MOVES.setdefault(pid, []).append([d, ty, fa_, ta_, esc(_trim120(_txt))])
        _MV_AT[k] = MOVES[pid][-1]
    for pid in MOVES:
        mlb_sign = {(m[0], m[3]) for m in MOVES[pid] if m[1] == "Signed as Free Agent"}
        MOVES[pid] = [m for m in MOVES[pid] if not (m[1] == "Minor-league deal" and (m[0], m[3]) in mlb_sign)][-24:]   # the most recent moves
ranks_all = json.load(open("/work/prospect_ranks.json"))
RANKS = {}
for rr in ranks_all:
    pid = str(rr["pid"])
    if pid in pidset:
        RANKS.setdefault(pid, {})[str(rr["year"])] = rr["rank"]
        NAMES.setdefault(pid, rr["name"])
# player fates: last MLB season and club from the value cache, so open
# chain endings can say what actually happened (still here / career over /
# left without a graded move)
_lvm = {k: v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
# every trade, every seat (trade_book.py): its pieces get names and fates too
TB = None
if os.path.exists("/work/trade_book.json"):
    TB = json.load(open("/work/trade_book.json")); TB.pop("check", None)
    tb_pids = {p for _, seats in TB["trades"] for st in seats for p, _ in st[2] + st[3]}
    TB["names"] = {p: TB["names"].get(p) for p in tb_pids if p not in NAMES and TB["names"].get(p)}
else:
    tb_pids = set()
# v5.8: every player linked from a card's full lists (draft, waivers, walks,
# signings, international) gets a name and a fate too, so no link opens an
# anonymous card
allx_pids = set()
for _fn in ("/work/sweep_results.json", "/work/hist_results.json"):
    for _r in json.load(open(_fn)):
        _ax = dict(_r.get("allx") or {})
        _ax.update(fa=_r.get("allx_fa") or [], intl=_r.get("allx_intl") or [])
        for _k, _rows in _ax.items():
            _i = {"draft": 7, "waiver": 4, "walk": 4, "fa": 7, "intl": 4}.get(_k)
            if _i is None: continue
            for _row in _rows:
                if len(_row) > _i and _row[_i]: allx_pids.add(str(_row[_i]))
for _p in allx_pids:
    if _p not in NAMES and _p in _lvm: NAMES[_p] = _lvm[_p].get("name") or NAMES.get(_p)
FATE = {}
for pid in pidset | tb_pids | allx_pids:
    rec = _lvm.get(pid)
    if not rec or not rec["rows"]: continue
    # the LAST club of the final season (rows run in order within a season):
    # max() picked the first, so Holmes read NYM after his August trade to CHC
    ly = max(t[0] for t in rec["rows"])
    last = [t for t in rec["rows"] if t[0] == ly][-1]
    FATE[pid] = [last[0], NAME2AB.get(last[1], "")]
# v5.9: display names as MLB lists them today (Stats API fullName, cached in
# statsapi_cache/names.json): the feed's names at transaction time drop
# suffixes ("Ken Griffey" for id 115135, Junior; "Bobby Witt" for Witt Jr.)
_NM_F = "/work/statsapi_cache/names.json"
try: _SANM = json.load(open(_NM_F))
except Exception: _SANM = {}
try:
    for _k, _v in json.load(open("/work/statsapi_cache/people.json")).items():
        if _k != "__asof" and _v.get("name"): _SANM.setdefault(_k, _v["name"])
except Exception: pass
_want = sorted({str(p) for p in list(NAMES) + list((TB or {}).get("names", {}))} - set(_SANM))
if _want:
    import urllib.request as _ur
    for _i in range(0, len(_want), 150):
        try:
            _r = json.load(_ur.urlopen(_ur.Request("https://statsapi.mlb.com/api/v1/people?personIds=" + ",".join(_want[_i:_i + 150]),
                                                   headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
            for _pp in _r.get("people", []): _SANM[str(_pp["id"])] = _pp.get("fullName")
        except Exception as _e:
            print("name fetch failed:", _e); break
    json.dump(_SANM, open(_NM_F, "w"))
_nfix = 0
for _k in list(NAMES):
    if _SANM.get(str(_k)) and NAMES[_k] != _SANM[str(_k)]: NAMES[_k] = _SANM[str(_k)]; _nfix += 1
if TB is not None:
    for _k in list(TB["names"]):
        if _SANM.get(str(_k)) and TB["names"][_k] != _SANM[str(_k)]: TB["names"][_k] = _SANM[str(_k)]; _nfix += 1
print("names set to MLB's current listing:", _nfix)
print(f"moves {len(MOVES)} | ranks {len(RANKS)} players | fates {len(FATE)}")
# v5.9: move types travel as indexes into PLAYER_MOVE_TYPES (expanded on load)
_MT = sorted({m[1] for ms in MOVES.values() for m in ms})
_MTI = {t: i for i, t in enumerate(_MT)}
MOVES = {k: [[m[0], _MTI[m[1]]] + list(m[2:]) for m in ms] for k, ms in MOVES.items()}
# v5.9: the career move log (about a third of the page) ships as moves.js
# beside the page and loads in parallel; the page declares empty bindings and
# anything drawn before it lands is redrawn on the "moves-loaded" event
_mv_body = ("PLAYER_MOVE_TYPES = " + json.dumps(_MT, ensure_ascii=False) + ";\nPLAYER_MOVES = " + json.dumps(MOVES, separators=(",", ":"), ensure_ascii=False)
            + ";\nfor(const _k in PLAYER_MOVES) PLAYER_MOVES[_k].forEach(m => { if(typeof m[1] === 'number') m[1] = PLAYER_MOVE_TYPES[m[1]]; });\n"
            + "window.MOVES_READY = true; window.dispatchEvent(new Event('moves-loaded'));\n")
import hashlib as _hl
MOVES_VER = _hl.md5(_mv_body.encode()).hexdigest()[:10]
open(os.path.join(os.path.dirname(P), "moves.js"), "w").write(_mv_body)
mv_js = ("let PLAYER_MOVE_TYPES = [], PLAYER_MOVES = {};"
         + "\nconst PLAYER_NAMES = " + json.dumps(NAMES, separators=(",", ":"), ensure_ascii=False)
         + ";\nconst PLAYER_RANKS = " + json.dumps(RANKS, separators=(",", ":"), ensure_ascii=False)
         + ";\nconst PLAYER_FATE = " + json.dumps(FATE, separators=(",", ":"), ensure_ascii=False) + ";\n\n")
i = min(x for x in (s.find("let PLAYER_MOVE_TYPES = "), s.find("const PLAYER_MOVE_TYPES = "), s.find("const PLAYER_MOVES = ")) if x >= 0)
assert i >= 0
tail_anchor = "const PLAYER_FATE" if "const PLAYER_FATE" in s else "const PLAYER_RANKS"
j = s.find("\n\n", s.find(tail_anchor, i))
s = s[:i] + mv_js + s[j+2:]
_KEEP = ("chan", "chanLedgers", "allx", "cum", "decisions", "seasons", "forGrade", "surplus", "walk", "h2h",
         "startDate", "dna", "dnaTags", "start", "titles", "success")
_cx = {k: {f: v[f] for f in _KEEP if f in v} for k, v in CURATED_FULL.items()}
cx_js = "const CURATED_EXTRA = " + json.dumps(_cx, separators=(",", ":"), ensure_ascii=False) + ";\nREGIMES.forEach(r => { const x = CURATED_EXTRA[r.id]; if(x){ Object.assign(r, x); r.realBadge = 'COMPUTED · FULL LEDGER · WITH HAND-WRITTEN SHOWCASE DECISIONS'; } });\n"
k = s.find("const CURATED_EXTRA = ")
if k >= 0:
    s = s[:k] + cx_js + s[s.find("});\n", s.find("REGIMES.forEach(r => { const x = CURATED_EXTRA", k)) + 4:]
else:
    k = min(x for x in (s.find("let PLAYER_MOVE_TYPES = "), s.find("const PLAYER_MOVES = ")) if x >= 0)
    s = s[:k] + cx_js + s[k:]
if TB is not None:
    tb_js = "const TRADE_BOOK = " + json.dumps(TB, separators=(",", ":"), ensure_ascii=False) + ";\n"
    k = s.find("const TRADE_BOOK = ")
    if k >= 0:
        s = s[:k] + tb_js + s[s.find(";\n", k) + 2:]
    else:
        k = min(x for x in (s.find("let PLAYER_MOVE_TYPES = "), s.find("const PLAYER_MOVES = ")) if x >= 0)
        s = s[:k] + tb_js + s[k:]
    print("trade book spliced:", len(TB["trades"]), "trades,", len(TB["names"]), "extra names")

# curated cards (lad/bal/mil): their decision pages are hand-verified, but the
# Results block is objective standings + October data, so it syncs from the
# computed sweep every regen (it had drifted: the 2026 champion read 0 titles)
import re as _re
for _r in res:
    if _r["id"] not in ("lad", "bal", "mil"): continue
    _su = _r["success"]
    _lit = ("success:{wpct:'%s', div:%d, po:%d, sw:%d, pen:%d, ws:%d, g:%d}"
            % (_su["wpct"], _su["div"], _su["po"], _su["sw"], _su["pen"], _su["ws"], _su["g"]))
    _i = s.find("id:'%s', exec:" % _r["id"])
    assert _i > 0, _r["id"]
    _j = s.find("success:{", _i); _k = s.find("}", _j) + 1
    s = s[:_j] + _lit + s[_k:]
    _t = _re.compile(r"titles:\d+").search(s, _i)
    s = s[:_t.start()] + "titles:%d" % _su["ws"] + s[_t.end():]
    print("curated success synced:", _r["id"], _lit)
# v5.5: single-move grades are relative to moves of the same kind and size.
# For each channel, every decision the engines graded (all clubs, all
# regimes; trades from both seats of the full trade book) is split into five
# stake bands (stake = what the move put at risk, in wins: contract cost,
# slot expectation, the larger side of a trade); within a band the letter is
# the move's percentile (F bottom 10%, D to 30%, C to 70%, B to 90%, A to
# 97.5%, A+ above). A $1M signing is compared with other $1M signings.
import os as _os
_pop = {}
for _f in ("sweep", "hist", "fa", "ext", "intl"):
    _p = f"/work/move_pop_{_f}.json"
    if _os.path.exists(_p):
        for _k, _v in json.load(open(_p)).items(): _pop.setdefault(_k, []).extend(_v)
_tb = json.load(open("/work/trade_book.json"))
_pop["trade"] = [[round(max(sum(abs(v) for _, v in st[2]), sum(abs(v) for _, v in st[3])), 2), st[1]] for _d, seats in _tb["trades"] for st in seats]
def _bands(pairs, nb=5):
    pairs = sorted(pairs)
    if len({st for st, _ in pairs}) == 1: nb = 1          # one-size channels (waivers, int'l)
    nb = max(1, min(nb, len(pairs) // 40))
    out = []
    for b in range(nb):
        seg = pairs[b * len(pairs) // nb:(b + 1) * len(pairs) // nb]
        nets = sorted(n for _, n in seg)
        q = [round(nets[min(len(nets) - 1, int(k / 40 * (len(nets) - 1) + 0.5))], 2) for k in range(41)]
        out.append([seg[-1][0] if b < nb - 1 else 9999, q, len(seg)])
    return out
MOVE_BANDS = {k: _bands(v) for k, v in _pop.items() if v}
s = _re.sub(r"const MOVE_BANDS = .*?;\n", lambda m: "const MOVE_BANDS = " + json.dumps(MOVE_BANDS, separators=(",", ":"), ensure_ascii=False) + ";\n", s, count=1, flags=_re.S)
print("move bands:", {k: [b[2] for b in v] for k, v in MOVE_BANDS.items()})
# v5.4: readers know the metric as Ledger WAR; "LVM" was internal shorthand
import re
s = re.sub(r"\bLVM\b", "WAR", s)
s = _re.sub(r"moves\.js\?v=[0-9a-f]*", "moves.js?v=" + MOVES_VER, s)
open(P, "w").write(s)
print(f"regenerated {len(auto)} auto regimes (v3 data)")
