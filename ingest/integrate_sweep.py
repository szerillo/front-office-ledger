"""Splice sweep_results.json into the prototype as AUTO_REGIMES."""
import json

P = "/home/claude/front-office-ledger-prototype.html"
res = json.load(open("/home/claude/sweep_results.json"))
s = open(P).read()

CH_LABEL = {"trade": "Trade", "draft": "Draft pick vs. slot", "waiver": "Waiver / Rule 5"}
def esc(x): return (x or "").replace("\\", "").replace("'", "\\'").replace("\n", " ")

auto = []
for r in res:
    if r["id"] in ("lad", "bal", "mil"):  # curated cards stay
        continue
    badge = '<span class="badge-real">COMPUTED</span>'
    best_tr, worst_tr, acq, loss = [], [], [], []
    for d in r["top"]:
        e = dict(d=d["d"][:10], war=d["net"], real=True, open=(int(d["d"][:4]) >= 2021),
                 t=(CH_LABEL.get(d["ch"], d["ch"]) + " · Ledger WAR v0 · sweep v1"),
                 h=esc(d["h"]) + " " + badge)
        if d["ch"] == "trade":
            e["note"] = (f"Auto-scored: value in {d.get('vin', 0):+0.1f} LVM vs value out "
                         f"{d.get('vout', 0):+0.1f} over a 5-year window from the deal date. "
                         "Sweep v1 windows are calendar approximations; decision-page precision "
                         "(control windows, leverage, options) comes when a card is promoted to curated.")
            (best_tr if d["net"] >= 0 else worst_tr).append(e)
        else:
            (acq if d["net"] >= 0 else loss).append(e)
    fa = r["chan"]["fa"]
    obj = dict(
        id=r["id"], exec=r["exec"], title="Head of Baseball Operations", team=r["team"],
        start=r["start"], seasons=round(r["seasons"]), titles=0,
        forGrade=r["forGrade"], smallSample=r["seasons"] < 3, realCard=True,
        realBadge="COMPUTED · LEDGER WAR v0 · SWEEP v1",
        success=dict(wpct=r["success"]["wpct"], div=r["success"]["div"], po=None, sw=None,
                     pen=None, ws=None, g=r["success"]["g"]),
        chan=dict(draft=r["chan"]["draft"], trade=r["chan"]["trade"],
                  fa=dict(net=0, g=None, n=fa["n"], raw=fa["net"]),
                  waiver=r["chan"]["waiver"]),
        surplus="≈$%dM" % round(r["total"] * 9.2), decisions=(r["chan"]["trade"]["n"]
                 + r["chan"]["draft"]["n"] + r["chan"]["waiver"]["n"] + fa["n"]),
        cum=None, ledgers=dict(bestTrades=best_tr[:3], worstTrades=worst_tr[:3],
                               bestAcq=acq[:4], losses=loss[:3]),
    )
    auto.append(obj)

js = "const AUTO_REGIMES = " + json.dumps(auto, indent=0) + ";\n\n"
marker = "/* =========================================================\n   helpers"
assert marker in s
s = s.replace(marker, js + marker)

# lbRows: include autos
old = "if(era!=='hist') rows.push(...REGIMES.map(r=>({...r, hasCard:true})), ...LB_EXTRA.map(r=>({...r, hasCard:false})));"
new = "if(era!=='hist') rows.push(...REGIMES.map(r=>({...r, hasCard:true})), ...AUTO_REGIMES.map(r=>({...r, hasCard:true})));"
assert old in s; s = s.replace(old, new)

# team selector + renderReport lookup across both arrays
old = "REGIMES.forEach(r=>{\n  const o = document.createElement('option');"
new = "[...REGIMES, ...AUTO_REGIMES].sort((a,b)=>a.team.localeCompare(b.team)).forEach(r=>{\n  const o = document.createElement('option');"
assert old in s; s = s.replace(old, new)
old = "const r = REGIMES.find(x=>x.id===id) || REGIMES[0];"
new = "const r = REGIMES.find(x=>x.id===id) || AUTO_REGIMES.find(x=>x.id===id) || REGIMES[0];"
assert old in s; s = s.replace(old, new)

# gradeChip null guard
old = "const gradeChip = (g, big) => `<span class=\"grade ${gradeClass(g)}\"${big?' style=\"font-size:13.5px\"':''} title=\"${g} on the 20–80 scouting scale\">${g2letter(g)}</span>`;"
new = ("const gradeChip = (g, big) => g==null ? '<span class=\"grade g50\" title=\"FA grading pending a contracts feed\">·</span>' : "
       "`<span class=\"grade ${gradeClass(g)}\"${big?' style=\"font-size:13.5px\"':''} title=\"${g} on the 20–80 scouting scale\">${g2letter(g)}</span>`;")
assert old in s; s = s.replace(old, new)

# success tile line: tolerate missing playoff detail
old = "<div class=\"dlt\">${s.wpct} W% · ${s.div==='-'?'-':s.div+' div'} · ${s.po} playoffs · ${s.sw} series W · ${s.pen} pennants · ${s.ws} WS</div>"
new = "<div class=\"dlt\">${s.wpct} W% · ${s.div==='-'?'-':s.div+' division titles'}${s.po==null?' · playoff detail in sweep v2':` · ${s.po} playoffs · ${s.sw} series W · ${s.pen} pennants · ${s.ws} WS`}</div>"
assert old in s; s = s.replace(old, new)

# leaderboard success tooltip: guard nulls
old = "const sTip = `${s.wpct} W% · ${s.div==='-'?'pre-division era':s.div+' division titles'} · ${s.po} playoff berths · ${s.sw} series wins · ${s.pen} pennants · ${s.ws} WS`;"
new = "const sTip = s.po==null ? `${s.wpct} W% · ${s.div} division titles (auto-computed)` : `${s.wpct} W% · ${s.div==='-'?'pre-division era':s.div+' division titles'} · ${s.po} playoff berths · ${s.sw} series wins · ${s.pen} pennants · ${s.ws} WS`;"
assert old in s; s = s.replace(old, new)

# cum chart: placeholder when absent; fa bar tooltip notes raw
old = "function renderCumChart(r){"
new = """function renderCumChart(r){
  if(!r.cum){ $('#cumchart').innerHTML = '<div style="color:var(--muted); font-size:12.5px; padding:40px 10px">Per-season decomposition ships in sweep v2. This card was generated automatically by the 30-regime sweep; promote it to curated for full chain detail.</div>'; return; }"""
assert old in s; s = s.replace(old, new)
old = "showTip(`<div class=\"t1\">${c.name} - ${r.team}</div><b>${fmtW(ch.net)} WAR</b> vs. channel expectation<br>${ch.n} decisions graded · grade <b>${g2letter(ch.g)}</b> (${ch.g}/80)`, e.clientX, e.clientY);"
new = "showTip(ch.g==null ? `<div class=\"t1\">${c.name} - ${r.team}</div>raw captured value ${fmtW(ch.raw||0)} LVM · UNGRADED pending a contracts feed · ${ch.n} signings` : `<div class=\"t1\">${c.name} - ${r.team}</div><b>${fmtW(ch.net)} WAR</b> vs. channel expectation<br>${ch.n} decisions graded · grade <b>${g2letter(ch.g)}</b> (${ch.g}/80)`, e.clientX, e.clientY);"
assert old in s; s = s.replace(old, new)

# drop the sample-only SD and NYM curated cards (autos supersede them)
i = s.find("  {\n    id:'sd'")
j = s.find("  {\n    id:'nym'")
k = s.find("];", j)
assert 0 < i < j < k
s = s[:i] + s[j:]           # remove sd block
i2 = s.find("  {\n    id:'nym'")
k2 = s.find("\n];", i2)
s = s[:i2] + s[k2+1:]
# leaderboard sample rows superseded by the sweep
i3 = s.find("const LB_EXTRA = [")
k3 = s.find("];", i3)
s = s[:i3] + "const LB_EXTRA = [" + s[k3:]

s = s.replace("prototype v1.0", "prototype v1.1 · 30-regime sweep")
open(P, "w").write(s)
print(f"integrated {len(auto)} auto regimes")
