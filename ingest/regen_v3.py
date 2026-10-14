"""Regenerate the prototype's data blocks from sweep_results.json:
AUTO_REGIMES, DEV_MAP, EXT_MAP, PLAYER_MOVES/NAMES/RANKS. UI code in the
page is already final; this swaps data only. Rebuilt Oct 2026 after the
container reclaim (original regen lived outside the repo; lesson learned,
this one ships in ingest/)."""
import json, sqlite3

P = "/home/claude/front-office-ledger-prototype.html"
res = json.load(open("/home/claude/sweep_results.json"))
s = open(P).read()

CH_LABEL = {"trade": "Trade", "draft": "Draft pick vs. slot",
            "waiver": "Waiver / Rule 5", "fa": "Free agency vs. contract cost",
            "intl": "International amateur class", "ext": "Extension vs. class market"}
def esc(x): return (x or "").replace("\\", "").replace('"', '&quot;').replace("\n", " ")

def dna_tags(dna):
    tags = []
    dd = (dna.get("devDef") or {}).get("v")
    dp = (dna.get("devPit") or {}).get("v")
    if dp is not None and dp >= 0.15: tags.append("Pitching lab")
    if dp is not None and dp <= -0.15: tags.append("Arms regress here")
    if dd is not None and dd >= 1.0: tags.append("Makes defenders better")
    if dd is not None and dd <= -1.5: tags.append("Gloves fade here")
    dr = dna.get("draft", {})
    if dr.get("pit", 0) >= 3 and dr.get("pit", 0) > 1.5 * max(dr.get("bat", 0), 0.1): tags.append("Drafts arms")
    elif dr.get("bat", 0) >= 3 and dr.get("bat", 0) > 1.5 * max(dr.get("pit", 0), 0.1): tags.append("Drafts bats")
    elif dr.get("pit", 0) >= 3 and dr.get("bat", 0) >= 3: tags.append("Draft machine, both sides")
    ti = dna.get("trade_in", {})
    if ti.get("pit", 0) >= 5 and ti.get("pit", 0) > ti.get("bat", 0): tags.append("Trades for arms")
    elif ti.get("bat", 0) >= 5 and ti.get("bat", 0) > ti.get("pit", 0): tags.append("Trades for bats")
    fa_ = dna.get("fa", {})
    if fa_.get("pit", 0) >= 2 and fa_.get("pit", 0) > fa_.get("bat", 0): tags.append("Signs arms well")
    elif fa_.get("bat", 0) >= 2 and fa_.get("bat", 0) > fa_.get("pit", 0): tags.append("Signs bats well")
    return tags[:4]

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
             open=(int(d["d"][:4]) >= 2022 or "OPEN" in d["h"]),
             t=CH_LABEL.get(d["ch"], "") + (" · Ledger WAR v1.5 · sweep v2" if d["ch"] != "walk" else " · passive loss, shown for context, not graded"),
             h=esc(d["h"]) + ' <span class="badge-real">COMPUTED</span>')
    if d.get("sides"): r["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
    if d.get("pids"): r["pids"] = [str(p) for p in d["pids"] if p]
    if d.get("att"): r["att"] = d["att"]
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

auto = []
for r in res:
    if r["id"] in ("lad", "bal", "mil"):
        continue
    badge = '<span class="badge-real">COMPUTED</span>'
    best_tr, worst_tr, acq, loss = [], [], [], []
    pool = (list(r["top"]) + list(r.get("fa_tops", [])) + list(r.get("intl_tops", []))
            + list(r.get("ext_tops", [])))
    for d in pool:
        e = dict(d=d["d"][:10], war=d["net"], real=True,
                 open=(int(d["d"][:4]) >= 2022 or "OPEN" in d["h"]),
                 t=(CH_LABEL.get(d["ch"], d["ch"]) + " · Ledger WAR v1.5 · sweep v2"),
                 h=esc(d["h"]) + " " + badge)
        if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
        if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
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
        id=r["id"], exec=r["exec"],
        title="Head of Baseball Operations" + (" (interim)" if "interim" in flags else ""),
        team=r["team"], start=r["start"], seasons=round(r["seasons"]),
        titles=r.get("titles", 0),
        forGrade=r["forGrade"], smallSample=r["seasons"] < 3, realCard=True,
        realBadge="COMPUTED · LEDGER WAR v1.5 · SWEEP v2 · THROUGH OCT 2026",
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
        dnaTags=dna_tags(r.get("dna", {})),
        h2h=r.get("h2h", [])[:10],
    ))

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
if os.path.exists("/home/claude/hist_results.json"):
    hres = json.load(open("/home/claude/hist_results.json"))
    PS = json.load(open("/home/claude/postseason.json"))
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
                     open=(int(d["d"][:4]) >= 2022),
                     t=(CH_LABEL.get(d["ch"], d["ch"]) + " · Ledger WAR v1.5 · archive sweep"),
                     h=esc(d["h"]) + " " + badge)
            if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
            if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
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
            e = dict(d=d["d"][:10], war=d["net"], real=True, open=(int(d["d"][:4]) >= 2022),
                     t=CH_LABEL.get(d["ch"], d["ch"]) + (" · Ledger WAR v1.5 · archive sweep" if d["ch"] != "walk" else " · passive loss, shown for context, not graded"),
                     h=esc(d["h"]) + ' <span class="badge-real">COMPUTED</span>')
            if d.get("sides"): e["sides"] = [[esc(lbl), [[esc(nm), str(v)] for nm, v in assets]] for lbl, assets in d["sides"]]
            if d.get("pids"): e["pids"] = [str(p) for p in d["pids"] if p]
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
            trueStart=r.get("trueStart"), flags=flags,
            seasons=round(r["seasons"]), titles=ws,
            forGrade=r["forGrade"], smallSample=r["seasons"] < 3, realCard=True,
            realBadge="COMPUTED · ARCHIVE SWEEP · LEDGER WAR v1.5 · TRADE/DRAFT/WAIVER GRADED; FA SHOWN RAW, DEV/EXT NOT SCORED FOR PAST WINDOWS",
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

devmap = {r["id"]: dict(r.get("dev", {}), tops=[dict(d=t["d"], war=t["net"], h=esc(t["h"]))
          for t in r.get("dev_tops", [])[:5]]) for r in res if r["id"] in ("lad", "bal", "mil")}
s = swap(s, "const DEV_MAP = ", ";\nconst devOf", json.dumps(devmap, indent=0))

extmap = {r["id"]: dict(r["chan"]["ext"], tops=[dict(d=t["d"], war=t["net"], h=esc(t["h"]))
          for t in r.get("ext_tops", [])[:4]]) for r in res if r["id"] in ("lad", "bal", "mil")}
s = swap(s, "const EXT_MAP = ", ";\nconst extOf", json.dumps(extmap, indent=0))

# player moves / names / ranks
cfg = json.load(open("/home/claude/regimes.json"))
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
con = sqlite3.connect("/home/claude/ledger.sqlite")
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
ranks_all = json.load(open("/home/claude/prospect_ranks.json"))
RANKS = {}
for rr in ranks_all:
    pid = str(rr["pid"])
    if pid in pidset:
        RANKS.setdefault(pid, {})[str(rr["year"])] = rr["rank"]
        NAMES.setdefault(pid, rr["name"])
print(f"moves {len(MOVES)} | ranks {len(RANKS)} players")
mv_js = ("const PLAYER_MOVES = " + json.dumps(MOVES, separators=(",", ":"))
         + ";\nconst PLAYER_NAMES = " + json.dumps(NAMES, separators=(",", ":"))
         + ";\nconst PLAYER_RANKS = " + json.dumps(RANKS, separators=(",", ":")) + ";\n\n")
i = s.find("const PLAYER_MOVES = ")
assert i >= 0
j = s.find("\n\n", s.find("const PLAYER_RANKS", i))
s = s[:i] + mv_js + s[j+2:]

open(P, "w").write(s)
print(f"regenerated {len(auto)} auto regimes (v3 data)")
