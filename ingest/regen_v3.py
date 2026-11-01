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
            "intl": "International amateur class", "ext": "Extension vs. class market"}
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

def trade_note(d):
    base = (f"Auto-scored: value in {d.get('vin', 0):+0.1f} vs value out {d.get('vout', 0):+0.1f}, "
            "control windows, leverage-weighted, discounted 10%/yr to the deal date.")
    a = d.get("att")
    if a and a.get("n_out"):
        gap = d.get("vout", 0) - a["out"]
        verdict = ("the pieces outperformed their marks, bad luck more than bad process" if gap > 2.5
                   else "the pieces underperformed their marks, the process was better than the outcome" if gap < -2.5
                   else "the outcome tracked the marks, this one is on the process")
        base += (f" PROCESS CHECK: the {a['n_out']} ranked piece(s) surrendered carried a Pipeline mark of about "
                 f"{a['out']:+0.1f} wins at the time; they realized {d.get('vout', 0):+0.1f} for the counterparty, so {verdict}.")
    if a and a.get("n_in"):
        base += f" Acquired ranked pieces were marked {a['inn']:+0.1f} at the time."
    return base

def row(d):
    r = dict(d=d["d"][:10], war=d["net"], real=True,
             open=d.get("unsettled", int(d["d"][:4]) >= 2021),
             t=CH_LABEL.get(d["ch"], "") + ("" if d["ch"] != "walk" else " · passive loss, shown for context, not graded"),
             h=esc(d["h"]) + ' <span class="badge-real">COMPUTED</span>')
    if d.get("sides"): r["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
    if d.get("pids"): r["pids"] = [str(p) for p in d["pids"] if p]
    if d.get("att"): r["att"] = d["att"]
    if d.get("comps"): r["comps"] = d["comps"]
    if d.get("proj"): r["proj"] = d["proj"]
    if d["ch"] == "trade": r["note"] = trade_note(d)
    return r

def chan_ledgers(r):
    led = r.get("led", {})
    fa = r.get("fa_led", dict(best=[], worst=[]))
    ext_all = r.get("ext_tops", [])
    return dict(
        trade=dict(best=[row(d) for d in led.get("trade", {}).get("best", [])],
                   worst=[row(d) for d in led.get("trade", {}).get("worst", [])]),
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
    badge = '<span class="badge-real">COMPUTED</span>'
    best_tr, worst_tr, acq, loss = [], [], [], []
    pool = (list(r["top"]) + list(r.get("fa_tops", [])) + list(r.get("intl_tops", []))
            + list(r.get("ext_tops", [])))
    for d in pool:
        e = dict(d=d["d"][:10], war=d["net"], real=True,
                 open=d.get("unsettled", int(d["d"][:4]) >= 2021),
                 t=(CH_LABEL.get(d["ch"], d["ch"]) + ""),
                 h=esc(d["h"]) + " " + badge)
        if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
        if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
        if d.get("comps"): e["comps"] = d["comps"]
        if d.get("proj"): e["proj"] = d["proj"]
        if d["ch"] == "trade":
            e["note"] = trade_note(d)
            (best_tr if d["net"] >= 0 else worst_tr).append(e)
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
        team=r["team"], start=r["start"], seasons=round(r["seasons"]),
        titles=r.get("titles", 0),
        forGrade=r["forGrade"], smallSample=r["seasons"] < 3, realCard=True,
        realBadge="COMPUTED · FULL LEDGER · THROUGH OCT 2026",
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

s = swap(s, "const AUTO_REGIMES = ", ";\n\n/* =", json.dumps(auto, indent=0))

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
        badge = '<span class="badge-real">COMPUTED</span>'
        pool = list(r["top"])
        best_tr, worst_tr, acq, loss = [], [], [], []
        for d in pool:
            e = dict(d=d["d"][:10], war=d["net"], real=True,
                     open=d.get("unsettled", int(d["d"][:4]) >= 2021),
                     t=(CH_LABEL.get(d["ch"], d["ch"]) + " · archive sweep"),
                     h=esc(d["h"]) + " " + badge)
            if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
            if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
            if d.get("comps"): e["comps"] = d["comps"]
            if d.get("proj"): e["proj"] = d["proj"]
            if d["ch"] == "trade":
                e["note"] = trade_note(d)
                (best_tr if d["net"] >= 0 else worst_tr).append(e)
            else:
                (acq if d["net"] >= 0 else loss).append(e)
        best_tr.sort(key=lambda x: -x["war"]); worst_tr.sort(key=lambda x: x["war"])
        acq.sort(key=lambda x: -x["war"]); loss.sort(key=lambda x: x["war"])
        # postseason detail over seasons held
        sd, ed = r["startDate"], r["endDate"]
        s_first = r["start"] + (1 if sd[5:7] > "07" else 0)
        s_last = r["end"] - (1 if ed[5:7] < "04" else 0)
        po = sw = pen = ws = 0
        for y in range(s_first, s_last + 1):
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
            e = dict(d=d["d"][:10], war=d["net"], real=True, open=d.get("unsettled", int(d["d"][:4]) >= 2021),
                     t=CH_LABEL.get(d["ch"], d["ch"]) + (" · archive sweep" if d["ch"] != "walk" else " · passive loss, shown for context, not graded"),
                     h=esc(d["h"]) + ' <span class="badge-real">COMPUTED</span>')
            if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
            if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
            if d.get("comps"): e["comps"] = d["comps"]
            if d.get("proj"): e["proj"] = d["proj"]
            if d["ch"] == "trade": e["note"] = trade_note(d)
            return e
        led = r.get("led", {})
        chl = dict(
            trade=dict(best=[hrow(d) for d in led.get("trade", {}).get("best", [])],
                       worst=[hrow(d) for d in led.get("trade", {}).get("worst", [])]),
            draft=dict(best=[hrow(d) for d in led.get("draft", {}).get("best", [])],
                       worst=[hrow(d) for d in led.get("draft", {}).get("worst", [])]),
            waiver=dict(best=[hrow(d) for d in led.get("waiver", {}).get("best", [])],
                        worst=[hrow(d) for d in led.get("waiver", {}).get("worst", [])]),
            fa=dict(best=[], worst=[]), intl=dict(best=[], worst=[]), ext=dict(best=[], worst=[]),
        )
        flags = r.get("flags", [])
        hist_cards.append(dict(
            id=r["id"], exec=r["exec"],
            title="Head of Baseball Operations · archive regime",
            team=r["team"], start=r["start"], end=r["end"], era="hist",
            startDate=r.get("startDate"), endDate=r.get("endDate"),
            trueStart=r.get("trueStart"), flags=flags,
            seasons=round(r["seasons"], 1), titles=ws,
            forGrade=r["forGrade"], smallSample=r["seasons"] < 3, realCard=True,
            realBadge="COMPUTED · ARCHIVE SWEEP · TRADE/DRAFT/WAIVER GRADED; FA SHOWN RAW, DEV/EXT NOT SCORED FOR PAST WINDOWS",
            success=suc,
            chan=dict(draft=r["chan"]["draft"], trade=r["chan"]["trade"],
                      fa=dict(net=0.0, g=None, n=fa["n"], raw=fa["net"]),
                      waiver=r["chan"]["waiver"],
                      intl=dict(net=0.0, g=None, n=0), ext=dict(net=0.0, g=None, n=0)),
            surplus="≈$%dM" % round(r["total"] * 9.2),
            decisions=(r["chan"]["trade"]["n"] + r["chan"]["draft"]["n"]
                       + r["chan"]["waiver"]["n"] + fa["n"]),
            cum=r.get("cum"),
            ledgers=dict(bestTrades=best_tr[:3], worstTrades=worst_tr[:3],
                         bestAcq=acq[:4], losses=loss[:3]),
            chanLedgers=chl,
            walk=[hrow(d) for d in r.get("walk", [])],
        ))
    s = swap(s, "const LB_HIST = ", ";\n\n/* =", json.dumps(hist_cards, indent=0))
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
    s = swap(s, "const CHAMPS_AUTO = ", ";\n\n// cross-title", json.dumps(champs["cards"], indent=0))
    s = swap(s, "const CHAMP_LINES = ", ";\n\nconst ALL_CHAMPS", json.dumps(champs["lines"], indent=0))
    print(f"computed champions: {len(champs['cards'])} cards + through lines")

devmap = {r["id"]: dict(r.get("dev", {}), tops=[dict(d=t["d"], war=t["net"], h=esc(t["h"]))
          for t in r.get("dev_tops", [])[:5]]) for r in res if r["id"] in ("lad", "bal", "mil")}
s = swap(s, "const DEV_MAP = ", ";\nconst devOf", json.dumps(devmap, indent=0))

extmap = {r["id"]: dict(r["chan"]["ext"], tops=[dict(d=t["d"], war=t["net"], h=esc(t["h"]))
          for t in r.get("ext_tops", [])[:4]]) for r in res if r["id"] in ("lad", "bal", "mil")}
s = swap(s, "const EXT_MAP = ", ";\nconst extOf", json.dumps(extmap, indent=0))

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
for _c in champ_cards_g:
    for _row in _c.get("roster", []):
        if len(_row) > 6 and _row[6] and _row[6] != "None":
            pidset.add(str(_row[6]))
con = sqlite3.connect("/work/ledger.sqlite")
MOVES, NAMES = {}, {}
if pidset:
    q = ("select person_id, person_name, date, team_id, type_desc, description, from_team, to_team from sweep_tx "
         "where person_id in (%s) and type_desc in ('Trade','Signed as Free Agent',"
         "'Declared Free Agency','Claimed Off Waivers','Rule 5 Selection','Released') "
         "order by date" % ",".join("?" * len(pidset)))
    seen = set()
    for pid, nm, d, tid, ty, desc, ft, tt in con.execute(q, tuple(pidset)):
        pid = str(pid)
        if ty == "Signed as Free Agent" and "minor league" in (desc or "").lower(): continue
        k = (pid, d, ty)
        if k in seen: continue
        seen.add(k)
        ab = TID2.get(tid, "?")
        fa_, ta_ = n2a(ft), n2a(tt)
        if ty == "Declared Free Agency" and not fa_: fa_ = ab
        if ty in ("Signed as Free Agent", "Claimed Off Waivers", "Rule 5 Selection") and not ta_: ta_ = ab
        NAMES.setdefault(pid, nm)
        MOVES.setdefault(pid, []).append([d, ty, fa_, ta_, esc((desc or "")[:120])])
    for pid in MOVES: MOVES[pid] = MOVES[pid][:14]
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
FATE = {}
for pid in pidset | tb_pids:
    rec = _lvm.get(pid)
    if not rec or not rec["rows"]: continue
    last = max(rec["rows"], key=lambda t: t[0])
    FATE[pid] = [last[0], NAME2AB.get(last[1], "")]
print(f"moves {len(MOVES)} | ranks {len(RANKS)} players | fates {len(FATE)}")
mv_js = ("const PLAYER_MOVES = " + json.dumps(MOVES, separators=(",", ":"))
         + ";\nconst PLAYER_NAMES = " + json.dumps(NAMES, separators=(",", ":"))
         + ";\nconst PLAYER_RANKS = " + json.dumps(RANKS, separators=(",", ":"))
         + ";\nconst PLAYER_FATE = " + json.dumps(FATE, separators=(",", ":")) + ";\n\n")
i = s.find("const PLAYER_MOVES = ")
assert i >= 0
tail_anchor = "const PLAYER_FATE" if "const PLAYER_FATE" in s else "const PLAYER_RANKS"
j = s.find("\n\n", s.find(tail_anchor, i))
s = s[:i] + mv_js + s[j+2:]
_KEEP = ("chan", "chanLedgers", "cum", "decisions", "seasons", "forGrade", "surplus", "walk", "h2h",
         "startDate", "dna", "dnaTags", "start", "titles", "success")
_cx = {k: {f: v[f] for f in _KEEP if f in v} for k, v in CURATED_FULL.items()}
cx_js = "const CURATED_EXTRA = " + json.dumps(_cx, separators=(",", ":")) + ";\nREGIMES.forEach(r => { const x = CURATED_EXTRA[r.id]; if(x){ Object.assign(r, x); r.realBadge = 'COMPUTED · FULL LEDGER · WITH HAND-WRITTEN SHOWCASE DECISIONS'; } });\n"
k = s.find("const CURATED_EXTRA = ")
if k >= 0:
    s = s[:k] + cx_js + s[s.find("});\n", s.find("REGIMES.forEach(r => { const x = CURATED_EXTRA", k)) + 4:]
else:
    k = s.find("const PLAYER_MOVES = ")
    s = s[:k] + cx_js + s[k:]
if TB is not None:
    tb_js = "const TRADE_BOOK = " + json.dumps(TB, separators=(",", ":")) + ";\n"
    k = s.find("const TRADE_BOOK = ")
    if k >= 0:
        s = s[:k] + tb_js + s[s.find(";\n", k) + 2:]
    else:
        k = s.find("const PLAYER_MOVES = ")
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
open(P, "w").write(s)
print(f"regenerated {len(auto)} auto regimes (v3 data)")
