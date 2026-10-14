#!/usr/bin/env python3
"""Per-regime dossiers: one two-page PDF per active club, the counterparty-prep
artifact a front office would actually print before a call. Built from
sweep_results.json (post ret2) + h2h + DNA + validation."""
import json, os, re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)

RES = json.load(open("/home/claude/sweep_results.json"))
NAVY = colors.HexColor("#15202e"); BLUE = colors.HexColor("#2a78d6")
MUTE = colors.HexColor("#5a6572"); RULE = colors.HexColor("#c9d1da")
GOOD = colors.HexColor("#1b7f4d"); BAD = colors.HexColor("#b23a3a")

ss = getSampleStyleSheet()
st_t = ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=19,
                      leading=22, textColor=NAVY, spaceAfter=0, alignment=0)
st_sub = ParagraphStyle("s", parent=ss["Normal"], fontSize=10.5, leading=14, textColor=MUTE, spaceAfter=6)
st_h = ParagraphStyle("h", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
                      leading=14, textColor=NAVY, spaceBefore=10, spaceAfter=3)
st_b = ParagraphStyle("b", parent=ss["Normal"], fontSize=9, leading=12.5,
                      textColor=colors.HexColor("#1d2630"), spaceAfter=4)
st_sm = ParagraphStyle("sm", parent=st_b, fontSize=7.8, leading=10.5, textColor=MUTE)

def letterg(g):
    if g is None: return "·"
    return ("A+" if g>=80 else "A" if g>=70 else "A-" if g>=65 else "B+" if g>=60 else
            "B" if g>=55 else "C+" if g>=50 else "C" if g>=45 else "D+" if g>=40 else
            "D" if g>=35 else "F")
def strip_tags(h): return re.sub(r"<[^>]*>", "", h or "").replace("&quot;", '"').strip()
def fw(v): return f"{v:+.1f}"

OUT = "/home/claude/dossiers"
os.makedirs(OUT, exist_ok=True)

CHN = [("trade","Trades"),("draft","Draft"),("fa","Free agency"),("waiver","Waiver/R5"),
       ("intl","Int'l"),("ext","Extensions"),("ret","Retention v2")]

for r in RES:
    fn = f"{OUT}/dossier-{r['abbr'].lower()}.pdf"
    doc = SimpleDocTemplate(fn, pagesize=letter, leftMargin=0.7*inch, rightMargin=0.7*inch,
                            topMargin=0.6*inch, bottomMargin=0.55*inch,
                            title=f"Counterparty dossier: {r['exec']} ({r['team']})",
                            author="Front Office Ledger · Sean Zerillo")
    E = []
    E.append(Paragraph(f"{r['exec']} · {r['team']}", st_t))
    s = r["success"]
    E.append(Paragraph(f"Counterparty dossier · regime since {r['start']} ({r['seasons']} seasons) · "
                       f"{s.get('w','')}-{s.get('l','')} ({s['wpct']}) · {s.get('ws',0)} WS · "
                       f"FOR {letterg(r['forGrade'])} · net decision value {fw(r['total'])} wins", st_sub))
    E.append(HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=6))

    # channel table
    rows = [["Channel", "Net (wins)", "Grade", "n", "Read"]]
    reads = dict(trade="control windows, leverage, discounted",
                 draft="vs maturity-adjusted slot curve",
                 fa="net of cost vs 1,630 contracts; QO charged",
                 waiver="vs zero: the pro-scouting read",
                 intl="vs bonus-pool class", ext="vs class market, CBT-aware",
                 ret="departures vs expectation + QO comp credit")
    for k, lbl in CHN:
        ch = r["chan"].get(k)
        if not ch: continue
        net = ch.get("net2") if k == "ret" else ch.get("net")
        g = ch.get("g2") if k == "ret" else ch.get("g")
        n = ch.get("n2") if k == "ret" else ch.get("n")
        rows.append([lbl, "·" if net is None else fw(net), letterg(g), str(n or ""), reads[k]])
    dev = r.get("dev")
    if dev:
        rows.append(["Development", fw(dev.get("net", 0)), letterg(dev.get("g")),
                     str(dev.get("n", "")), "Pipeline marks; credit stays home when traded"])
    t = Table(rows, colWidths=[1.05*inch, 0.85*inch, 0.55*inch, 0.45*inch, 3.9*inch])
    t.setStyle(TableStyle([
        ("FONT", (0,0), (-1,0), "Helvetica-Bold", 8.2), ("FONT", (0,1), (-1,-1), "Helvetica", 8.2),
        ("TEXTCOLOR", (0,0), (-1,0), NAVY), ("LINEBELOW", (0,0), (-1,0), 0.75, RULE),
        ("LINEBELOW", (0,1), (-1,-2), 0.25, RULE),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 2),
    ]))
    E.append(t)

    # tendencies
    dna = r.get("dna") or {}
    tags = []
    dd = (dna.get("devDef") or {}).get("v"); dp = (dna.get("devPit") or {}).get("v"); db = (dna.get("devBat") or {}).get("v")
    if dp is not None and dp >= 0.15: tags.append("pitching lab: arms arriving here improve (+%.2f w/season)" % dp)
    if dp is not None and dp <= -0.15: tags.append("arms regress on arrival (%.2f w/season)" % dp)
    if dd is not None and dd >= 1.0: tags.append("defenders improve here (+%.1f runs/season)" % dd)
    if db is not None and db >= 2.0: tags.append("bats improve here (+%.1f runs/season)" % db)
    dr = dna.get("draft", {})
    if dr: tags.append(f"draft room: arms {fw(dr.get('pit',0))} / bats {fw(dr.get('bat',0))} vs slot")
    ti, to = dna.get("trade_in", {}), dna.get("trade_out", {})
    if ti: tags.append(f"trades in: arms {fw(ti.get('pit',0))} / bats {fw(ti.get('bat',0))}; "
                       f"out: arms {fw(to.get('pit',0))} / bats {fw(to.get('bat',0))}")
    bl = dna.get("buyLow")
    if bl and bl.get("n"): tags.append(f"buy-low hit rate {bl.get('rate','?')} on {bl['n']} tries")
    E.append(Paragraph("Tendencies (measured, not scouted)", st_h))
    for tg in tags or ["balanced profile / small sample"]:
        E.append(Paragraph("· " + tg, st_b))

    # head-to-head
    h2h = r.get("h2h") or []
    if h2h:
        E.append(Paragraph("Head-to-head trade record (vs sitting regimes, net wins from this seat)", st_h))
        line = " · ".join(f"vs {x.get('opp','?')} {fw(x.get('net',0))} ({x.get('n',0)} deals)" for x in h2h[:6])
        E.append(Paragraph(line, st_b))

    # best / worst decisions
    def decline(d):
        return f"{d['d'][:10]} · {strip_tags(d['h'])[:95]} · {fw(d['net'])}"
    tops = r.get("top") or []
    best = [d for d in tops if d["net"] > 0][:4]
    worst = sorted([d for d in tops if d["net"] < 0], key=lambda x: x["net"])[:4]
    E.append(Paragraph("Signature wins", st_h))
    for d in best: E.append(Paragraph("· " + decline(d), st_b))
    E.append(Paragraph("Scar tissue", st_h))
    for d in worst: E.append(Paragraph("· " + decline(d), st_b))
    walk = r.get("walk") or []
    if walk:
        E.append(Paragraph("Walkaways that stung", st_h))
        for d in walk[:3]: E.append(Paragraph("· " + decline(d), st_b))

    E.append(Spacer(1, 6))
    E.append(HRFlowable(width="100%", thickness=0.75, color=RULE, spaceBefore=4, spaceAfter=4))
    E.append(Paragraph(
        "Front Office Ledger · Sean Zerillo · sean.zerillo@gmail.com · szerillo.github.io/front-office-ledger/prototype · "
        "All values Ledger WAR v1.5 (park factors, SDI/Statcast defense, framing, baserunning), sweep v2 "
        "(control windows, win-curve leverage, 10%/yr discounting), computed from the MLB Stats API through Oct 14, 2026. "
        "Validation: roster-summed metric vs team records r = 0.80 across 327 team-seasons; decision value predicts "
        "future W% (partial r = 0.36) after controlling for record. Full methodology on the site.", st_sm))
    doc.build(E)

print("dossiers built:", len(os.listdir(OUT)))
