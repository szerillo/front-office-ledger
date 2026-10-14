#!/usr/bin/env python3
"""Application packet: three-page technical summary of the Front Office
Ledger for MLB team applications. reportlab platypus, print-clean."""
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable)

val = json.load(open("/home/claude/validation.json"))
A, P = val["accounting"], val["predictive"]

NAVY = colors.HexColor("#15202e")
BLUE = colors.HexColor("#2a78d6")
MUTE = colors.HexColor("#5a6572")
RULE = colors.HexColor("#c9d1da")

ss = getSampleStyleSheet()
st_title = ParagraphStyle("t", parent=ss["Title"], fontName="Helvetica-Bold",
                          fontSize=26, leading=30, textColor=NAVY, spaceAfter=2, alignment=0)
st_sub = ParagraphStyle("s", parent=ss["Normal"], fontName="Helvetica",
                        fontSize=12, leading=16, textColor=MUTE, spaceAfter=10)
st_h = ParagraphStyle("h", parent=ss["Heading2"], fontName="Helvetica-Bold",
                      fontSize=13, leading=16, textColor=NAVY, spaceBefore=14, spaceAfter=4)
st_b = ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica",
                      fontSize=10, leading=14.5, textColor=colors.HexColor("#1d2630"),
                      spaceAfter=7)
st_small = ParagraphStyle("sm", parent=st_b, fontSize=8.5, leading=12, textColor=MUTE)
st_stat = ParagraphStyle("stat", parent=st_b, fontSize=9.5, leading=13)

doc = SimpleDocTemplate("/home/claude/front-office-ledger-packet.pdf", pagesize=letter,
                        leftMargin=0.85*inch, rightMargin=0.85*inch,
                        topMargin=0.75*inch, bottomMargin=0.7*inch,
                        title="Front Office Ledger: Technical Summary",
                        author="Sean Zerillo")
E = []

E.append(Paragraph("Front Office Ledger", st_title))
E.append(Paragraph("A decision-level accounting system for MLB front offices. Built end to end by Sean Zerillo.", st_sub))
E.append(HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=10))
E.append(Paragraph(
    'Live site: <b>szerillo.github.io/front-office-ledger/prototype</b> &nbsp;·&nbsp; '
    'Code and data: <b>github.com/szerillo/front-office-ledger</b> &nbsp;·&nbsp; '
    'Contact: <b>sean.zerillo@gmail.com</b>', st_stat))
E.append(Spacer(1, 10))
E.append(Paragraph(
    "Every front-office argument eventually reduces to the same missing document: the ledger. Who actually made the "
    "decisions, what did each one return against what it should have returned, and how much of the result was process "
    "versus luck? I built that document for all thirty active MLB regimes, as a working public product: every trade, "
    "draft pick, free-agent signing, extension, waiver claim, and international signing since each executive took "
    "office, graded against the market expectation for that transaction type, attributed to the regime that made it, "
    "and clickable down to the individual decision. Nothing is a vibe: every number is computed from public data by a "
    "versioned, documented methodology, and the parts that are approximations say so on the page.", st_b))

E.append(Paragraph("What the system does", st_h))
E.append(Paragraph(
    "<b>Six graded acquisition channels.</b> Trades are scored from both seats over control windows (value counts "
    "while the player stays with the club), with each delivered season weighted by win-curve leverage at the receiving "
    "club and discounted 10% per year to the deal date. Draft picks grade against a maturity-adjusted slot-expectation "
    "curve. Free agency grades realized value net of contract cost against 1,630 real contracts, with qualifying-offer "
    "signings charged their forfeited draft compensation and deferral-heavy deals costed at CBT present value. "
    "Extensions grade against the extension market for the player's service class, because the pre-arb discount is "
    "structural and the skill is choosing whom to lock up. International signings grade against their bonus-pool "
    "class. Waiver claims grade against zero, the cleanest read on pro scouting.", st_b))
E.append(Paragraph(
    "<b>Two eras, one engine.</b> Beyond the 30 active regimes, the same scorer runs over 71 archive regimes "
    "(2005-2024) with their actual start and end dates: Sabean's draft rooms, Epstein in both cities, late-era "
    "Beane, Luhnow's Houston. Careers are now comparable across eras on identical accounting, and every archive "
    "card carries the same clickable decision ledgers and transaction trees as the active ones.", st_b))
E.append(Paragraph(
    "<b>Three top-level grades per regime.</b> FOR (decision quality vs expectation), DEV (player development: "
    "prospects marked to market yearly on a rank-to-surplus-wins curve built from sixteen seasons of MLB Pipeline "
    "top-100 lists, with credit staying home when the prospect is traded and an inherited screen so new regimes do "
    "not collect predecessors' work), and Success (on-field results: W%, division titles, and full postseason detail). "
    "The gaps between the three are usually the most interesting numbers on the page.", st_b))
E.append(Paragraph(
    "<b>Process separated from outcome.</b> Every trade whose pieces appeared on a top-100 list carries a process "
    "check: the surrendered players priced at their deal-date prospect marks versus what they actually became. San "
    "Diego trading a 19-year-old Trea Turner reads as a 2.4-win process mistake and a 20.7-win outcome, which are "
    "different numbers and should be.", st_b))
E.append(Paragraph(
    "<b>An empirical trade market.</b> From 237 deadline rental deals classified exactly from the transaction feed: "
    "a star rental win costs about 0.8 wins of eventually-realized value, the median deadline rental costs roughly "
    "nothing that ever materializes, and over half of rental buys deliver under 0.3 wins. Boston's return for one "
    "expected year of Mookie Betts was market rate; the ledger's criticism was never the price.", st_b))

E.append(PageBreak())
E.append(Paragraph("Validation", st_h))
tbl = Table([
    [Paragraph("<b>Accounting check</b><br/>A WAR-class metric must sum to team record. Roster-summed Ledger WAR "
               f"vs actual wins above a 48-win baseline, {A['n']} team-seasons (2015-2025).", st_stat),
     Paragraph(f"<b>r = {A['r']}</b> (R<super>2</super> = {A['r2']})<br/>slope {A['slope']}<br/>MAE {A['mae']} wins", st_stat)],
    [Paragraph("<b>Predictive check</b><br/>Does decision quality carry information about future results beyond the "
               f"current record? {P['n']} pooled regime-years: net decision value per season through year t, "
               "predicting the next two seasons' W% after controlling for W% to date.", st_stat),
     Paragraph(f"<b>partial r = {P['partial_r']}</b><br/>R<super>2</super> {P['r2_base']} to {P['r2_full']}<br/>"
               "decision quality is forward information", st_stat)],
], colWidths=[4.7*inch, 2.1*inch])
tbl.setStyle(TableStyle([
    ("BOX", (0,0), (-1,-1), 0.75, RULE), ("INNERGRID", (0,0), (-1,-1), 0.5, RULE),
    ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
]))
E.append(tbl)
E.append(Paragraph(
    "Both checks are reproducible from the repository with no licensed data. The value metric (Ledger WAR v1.5) is "
    "self-built from the MLB Stats API: wOBA-based batting runs with positional adjustments, FIP-based pitching "
    "anchored to league RA9, park factors from home/away run environments (3-yr rolling, halved for the road "
    "split), defense from the SABR Defensive Index where published and Statcast fielding runs plus catcher framing "
    "elsewhere, and Statcast baserunning. Park factors (v1.5) and the archive sweep's full 25,000-player universe "
    "tightened the accounting check from r = 0.80 to r = 0.86 (MAE 6.8 to 5.2 wins): fuller rosters sum closer to "
    "team records, which is itself evidence the metric is additive the way WAR must be. Known gaps (defense coverage thins before "
    "2016) are disclosed on the site rather than patched quietly. Pooled regime-years overlap, so the predictive "
    "check's effect size is the claim, not its p-value.", st_small))

E.append(Paragraph("Findings the consensus did not already have", st_h))
for f in [
    "<b>The best draft room of the data era is Brian Sabean's San Francisco</b>, +127 wins over slot (Posey, "
    "Bumgarner, the dynasty's core), surfaced by the archive sweep. Among active regimes it is Brian Cashman's, "
    "at +53 above slot, while his FA channel grades below water net of cost: the checkbook narrative has the "
    "mechanism backwards. (That number fell from +69 when the system caught itself crediting Gerrit Cole's "
    "free-agent-era production to the 2008 pick that never signed; the unsigned-pick screen is now part of the "
    "methodology, which is how a system like this is supposed to improve.)",
    "<b>The Baltimore gap, quantified:</b> elite grades on decisions and development against a D in results through "
    "2026. Whether you weight the machine or the harvest is a values question; the ledger puts both numbers on one row.",
    "<b>The best extension in the book is Cleveland's 2017 Jose Ramirez deal</b> at about +20 wins against the "
    "class market. Atlanta's famous 2019 pair grades merely good, because the class baseline already expects "
    "extensions to be team-friendly; the skill is picking the right player.",
    "<b>Organizational DNA is measurable.</b> Measuring every player who changed orgs (performance in the two seasons "
    "after arriving vs the two before), the reputations fall out of the data unprompted: Cleveland improves "
    "defenders by about +2.5 runs per season and arms by +0.19 wins; Milwaukee, Tampa Bay, and San Diego profile as "
    "pitching labs; Texas arms regress. None of this was curated.",
    "<b>How titles actually get built, measured across all 21 champions 2005-2025:</b> the median champion was "
    "88% built by its sitting regime and won in year seven of the tenure; nine of 21 titles came in year ten or "
    "later, and free agency has been a majority channel exactly once (the 2009 Yankees). The most inherited title "
    "is 2023 Texas, 85% Jon Daniels' core two seasons after the handoff: the sharpest attribution case in the book.",
    "<b>The system audits its own inputs.</b> Tracing the 2009 Yankees' roster exposed that the MLB transaction "
    "feed is empty before 2009; the fix was joining the Retrosheet archive (22,697 rows, 1998-2008, mapped to "
    "MLBAM ids via the Chadwick register), which put the Beckett-for-Hanley and Cabrera trades into the book and "
    "left the validation studies unchanged. Every graded trade also now carries market comps: the nearest deals "
    "by size and phase from a 5,764-deal archive, so each verdict reads against what deals of that shape cost.",
    "<b>Head-to-head records exist and are lopsided.</b> Every trade between two sitting regimes, netted from each "
    "seat: some relationships run 20+ wins one-sided across a decade of deals. Counterparty selection is a skill "
    "the public conversation does not price.",
]:
    E.append(Paragraph(f, st_b))

E.append(PageBreak())
E.append(Paragraph("What this machinery does inside a club", st_h))
E.append(Paragraph(
    "The public site is the free-data proof. Pointed at internal data, the same architecture is a decision-support "
    "system: <b>deadline pricing</b> (the live rental-market curve says what a win costs this July and whether an "
    "offer clears the market that actually exists), <b>extension pricing</b> (class-market baselines with CBT-aware "
    "deferral valuation), <b>counterparty preparation</b> (every GM's trade record, channel tendencies, buy-low "
    "habits, and development effects before the call), <b>self-audit</b> (which channels actually produce, with "
    "process separated from outcome so scouting is not punished for variance), and <b>regime benchmarking</b> for "
    "ownership. Swap the public value metric for internal projections and the public prospect ranks for pref lists "
    "and every grade sharpens; nothing in the architecture assumes public data.", st_b))

E.append(Paragraph("How it was built", st_h))
E.append(Paragraph(
    "Python ingestion and scoring over the MLB Stats API (244,000+ transaction rows, 30,000+ draft picks, 25,000+ "
    "players valued), SQLite storage, a single-file front end with no frameworks, and zero scraping of licensed "
    "sources: when FanGraphs and Baseball-Reference proved off-limits to programmatic access, the answer was to "
    "build and validate an open value metric rather than take shortcuts. Supplementary archives were solved, not "
    "bought: the Pipeline top-100 history came from reverse-engineering MLB's GraphQL endpoint, prospect-holding "
    "orgs from minor-league season rosters, the SABR Defensive Index from parsing its published tables, rentals "
    "classified exactly from free-agency declarations in the feed. The methodology is versioned (v0.1 through v0.3 "
    "plus sweep v2, Ledger WAR v1.5, and the archive sweep), every revision is documented in the repository with what changed and why, and "
    "the 1873-2022 Retrosheet transaction archive is already ingested for the historical backfill. Schema and "
    "channel definitions are designed to extend to other leagues.", st_b))

E.append(Paragraph("Honest limitations, currently disclosed on the site", st_h))
E.append(Paragraph(
    "Defense coverage thins before 2016 and pre-2014 seasons are bat-plus-position only. Extension class discounts "
    "are documented assumptions pending a larger book. Recent-era rental ratios are right-censored while surrendered "
    "prospects mature. Retention is graded but excluded from the composite until compensation picks are modeled, "
    "because raw leakage scales with how many stars a club employs. Archive regimes grade trade, draft, and waiver "
    "channels; their FA book and development grades await the historical contract and prospect-list backfill, and "
    "regimes seated before the 2005 transaction-feed floor are truncated and flagged with their true start. The 2026 "
    "postseason was in progress at this build. A system like this earns trust by labeling its own soft spots, and "
    "that principle is applied everywhere.", st_b))
E.append(Spacer(1, 6))
E.append(HRFlowable(width="100%", thickness=1, color=RULE, spaceBefore=8, spaceAfter=8))
E.append(Paragraph(
    "<b>Sean Zerillo</b> · sean.zerillo@gmail.com · Live product: szerillo.github.io/front-office-ledger/prototype · "
    "Methodology, code, and data: github.com/szerillo/front-office-ledger. Everything in this document is computed "
    "and current through October 14, 2026.", st_stat))

doc.build(E)
print("packet built")
