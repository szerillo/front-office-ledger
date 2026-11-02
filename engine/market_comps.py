"""
MARKET COMPS FOR EVERY KIND OF MOVE (Nov 2): trades already carry the three
nearest deals of their shape (trade_comps.py). This gives free-agent
signings, extensions and draft picks the same thing, so any graded move on a
card can be read against what moves like it usually returned.

  * Free agency: the nearest signings league-wide by money at stake (cost in
    wins, log scale), age at signing, pitcher vs hitter and era, other
    players only, finished deals preferred. Shown: what he produced on the
    club and his result against a typical club's return for the same money.
  * Extensions: the same service class (pre-debut, early, arbitration,
    veteran), nearest by cost and age, deals with more seasons played
    preferred. Shown: seasons played and the result against the class.
  * Draft picks: picks within a few slots in other drafts (1998 on), nearest
    first. Shown: wins in club control and the result against the slot.

Writes comps onto every fa/ext/draft decision in sweep_results.json and
hist_results.json (the regen passes them through to the decision pages).
"""
import json, math
AGES = {int(k): v for k, v in json.load(open("/work/ages.json")).items()}
POS = json.load(open("/work/positions.json"))
PIT = {"RHP", "LHP", "SP", "RP", "P"}
R = json.load(open("/work/sweep_results.json"))
H = json.load(open("/work/hist_results.json"))
HL = H if isinstance(H, list) else H.get("regimes", [])
EXT = json.load(open("/work/ext_eval.json"))

def age_at(pid, yr):
    by = AGES.get(int(pid)) if pid else None
    return (yr - by) if by else None
def is_pit(pid): return POS.get(str(pid)) in PIT

# ---- pools (deduplicated across active and archive cards) ----
FA, DR = {}, {}
for r in R + HL:
    ab = r.get("abbr")
    for x in (r.get("allx_fa") or (r.get("allx") or {}).get("fa") or []):
        if x[6] is None or x[2] is None or not x[7]: continue
        k = (str(x[7]), x[0])
        if k in FA: continue
        yr = int(x[0][:4]); end_yr = yr + (1 if int(x[0][5:7]) >= 10 else 0) + int(x[2]) - 1
        FA[k] = dict(pid=str(x[7]), d=x[0], yr=yr, ab=ab, who=x[1], yrs=int(x[2]), tot=float(x[3]), prod=x[4], typ=x[5], net=x[6],
                     cost=float(x[8]) if len(x) > 8 and x[8] is not None else None, done=end_yr <= 2026,
                     age=age_at(x[7], yr + 1), pit=is_pit(x[7]))
    for x in ((r.get("allx") or {}).get("draft") or []):
        if x[6] is None or not x[7]: continue
        k = (str(x[7]), x[0][:4])
        if k in DR: continue
        DR[k] = dict(pid=str(x[7]), yr=int(x[0][:4]), ab=ab, who=x[1], pick=int(x[2]), ctrl=x[3], exp=x[5], net=x[6])
EX = {}
for e in EXT:
    if not e.get("pid") or not e.get("n"): continue
    yr = int(e["s"][:4])
    EX[(str(e["pid"]), e["s"])] = dict(pid=str(e["pid"]), s=e["s"], yr=yr, ab=e["ab"], who=e["p"], yrs=e["yrs"], tot=e["tot"], cls=e["cls"],
                                       net=e["net"], n=e["n"], pf=e.get("pf"), cost=e.get("cost") or 0.0, age=age_at(e["pid"], yr))
print(f"comp pools: {len(FA)} signings, {len(EX)} extensions, {len(DR)} picks")
FAL, EXL, DRL = list(FA.values()), list(EX.values()), list(DR.values())

def lg(x): return math.log(max(x, 0.2))
def fa_comps(d):
    pid = str((d.get("pids") or [None])[0]); yr = int(d["d"][:4]); cost = d.get("st") or 0.0
    me = FA.get((pid, d["d"])) or {}
    age, pit = me.get("age"), me.get("pit", is_pit(pid))
    out = []
    for c in FAL:
        if c["pid"] == pid or c["cost"] is None: continue
        sc = abs(lg(c["cost"]) - lg(cost)) * 2.0 + 0.04 * abs(c["yr"] - yr) + (0 if c["pit"] == pit else 0.8)
        sc += 0.12 * abs((c["age"] or 30) - (age or 30)) + (0 if c["done"] else 0.5)
        out.append((sc, c))
    out.sort(key=lambda t: t[0])
    res, seen = [], set()
    for _, c in out:
        if c["pid"] in seen: continue
        seen.add(c["pid"])
        res.append(dict(k="fa", yr=c["yr"], ab=c["ab"], who=c["who"][:28], what=f"{c['yrs']} yr / ${c['tot']:.0f}M" + (f", age {c['age']}" if c["age"] else "") + ("" if c["done"] else ", still running"),
                        a=round(c["prod"], 1), b=round(c["net"], 1)))
        if len(res) >= 3: break
    return res
def ext_comps(d, cls):
    pid = str((d.get("pids") or [None])[0]); yr = int(d["d"][:4]); cost = d.get("st") or 0.0
    me = next((e for e in EXL if e["pid"] == pid and e["s"] == d["d"][:7]), None)
    age = me["age"] if me else None
    out = []
    for c in EXL:
        if c["pid"] == pid or c["cls"] != cls: continue
        sc = abs(lg(c["cost"]) - lg(cost)) * 2.0 + 0.03 * abs(c["yr"] - yr) + 0.1 * abs((c["age"] or 27) - (age or 27))
        sc += 0.25 * max(0, 3 - c["n"])
        out.append((sc, c))
    out.sort(key=lambda t: t[0])
    res, seen = [], set()
    for _, c in out:
        if c["pid"] in seen: continue
        seen.add(c["pid"])
        res.append(dict(k="ext", yr=c["yr"], ab=c["ab"], who=c["who"][:28], what=f"{c['yrs']} yr / ${c['tot']:.0f}M ({c['cls']})" + (f", projected to finish {c['pf']:+.1f}" if c["pf"] is not None else ""),
                        a=f"{c['n']} of {c['yrs']}", b=round(c["net"], 1)))
        if len(res) >= 3: break
    return res
def draft_comps(d):
    pid = str((d.get("pids") or [None])[0]); yr = int(d["d"][:4])
    import re
    m = re.search(r"#(\d+) overall", d.get("h", ""))
    if not m: return []
    pk = int(m.group(1))
    out = []
    for c in DRL:
        if c["pid"] == pid or c["yr"] == yr or c["yr"] > 2019: continue   # a pick needs time to play out
        sc = abs(math.log(c["pick"]) - math.log(pk)) * 6 + 0.02 * abs(c["yr"] - yr)
        out.append((sc, c))
    out.sort(key=lambda t: t[0])
    return [dict(k="draft", yr=c["yr"], ab=c["ab"], who=c["who"][:28], what=f"#{c['pick']} overall", a=round(c["ctrl"], 1), b=round(c["net"], 1)) for _, c in out[:3]]

def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
def attach(res, path):
    n = 0; done = set()
    for o in walk(res):
        ch = o.get("ch")
        if ch not in ("fa", "ext", "draft") or "h" not in o or id(o) in done: continue
        done.add(id(o))
        if ch == "fa": c = fa_comps(o)
        elif ch == "ext":
            import re
            m = re.search(r"\((pre-debut|early|arb|veteran)\)", o["h"]); c = ext_comps(o, m.group(1)) if m else []
        else: c = draft_comps(o)
        if c: o["comps"] = c; n += 1
    json.dump(res, open(path, "w"), indent=1)
    print(f"{path}: comps on {n} signing, extension and draft decisions")
attach(R, "/work/sweep_results.json")
attach(H, "/work/hist_results.json")
