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

val = json.load(open("/work/validation.json"))
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

doc = SimpleDocTemplate("/work/front-office-ledger-packet.pdf", pagesize=letter,
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
    "<b>Six graded acquisition channels.</b> Trades are scored from both seats over the player's control window "
    "wherever he plays it, net of the salary that moves (arbitration included), discounted 10% per year; a prospect "
    "not yet in the majors carries his at-the-time rank expectation until his real seasons replace it. Draft picks "
    "grade against what the league got from the same slot in the same draft. Free agency grades realized value "
    "against what a typical club gets for the same money in the same contract years on a deal of the same size, from "
    "a book of about 3,600 contracts, with deferral-heavy deals costed at CBT present value and posting fees charged. "
    "Extensions grade against the path they replaced (arbitration in controlled seasons, the free-agent market "
    "after), centered by service class. International signings grade against their bonus-pool class. Waiver claims "
    "grade against zero, net of the contract that moves.", st_b))
E.append(Paragraph(
    "<b>Two eras, one engine.</b> Beyond the 30 active regimes, the same scorer runs over 122 archive regimes "
    "(1998-2026, interim GMs included) with their actual start and end dates: the complete Beane and Sabean windows, Epstein in both "
    "cities, Gillick in three, Cashman's full 29-year seat. Careers are comparable across eras on identical "
    "accounting, and every archive card carries the same clickable decision ledgers, market comps, and "
    "transaction trees as the active ones.", st_b))
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
    "<b>A forward view that never touches the grades.</b> Open deals carry a projected final verdict from a "
    "self-built projection layer: Marcel-style regressed form walked forward on delta-method aging curves computed "
    "from the project's own 28,000-player value cache, prospects at their Pipeline-rank expectation. Backtested at "
    "r = 0.62-0.67 against actual next-season WAR, competitive with public systems, and quarantined: realized value "
    "is the ledger, the projection is the heading.", st_b))
E.append(Paragraph(
    "<b>An empirical trade market.</b> From 224 deadline rental deals classified exactly from the transaction feed: "
    "a rental win costs about 0.8 wins of eventually-realized value (the nine true star rentals ran nearer 1.2), the median deadline rental costs roughly "
    "nothing that ever materializes, and over half of rental buys deliver under 0.3 wins. Boston's return for one "
    "expected year of Mookie Betts was market rate; the ledger's criticism was never the price.", st_b))
E.append(Paragraph(
    "<b>A Deal Desk that does the work first.</b> Propose any trade, signing, or extension and the engine renders a "
    "verdict from the ledger's own machinery: projected value over each piece's control (with a playing-time "
    "durability factor), win-curve leverage at the club's standing, the market rate for deals of that shape with "
    "bust rates, the nearest real comps and how they ended, and counterparty intelligence. For contracts it "
    "proposes the terms itself: a calibrated Ledger offer blending market comps (the eight nearest real contracts "
    "by form, age, and position, with realized outcomes) and the model's fair price, <b>backtested winter by "
    "winter on 1,196 real signings 2010-2025</b> using only information available at the time (typical miss 0.7 "
    "years, $3.2M of AAV; mega-deal pricing carries a pedigree gate, a pitcher scarcity premium, and convex elite pricing with regression shrink, bringing the $200M-class miss to about $91M against $140M for the comp median alone, with no systematic bias; the residual star shortfall the market itself produces is disclosed, not tuned away). "
    "Every verdict shows the club's estimated payroll before and after (book money plus arb/pre-arb estimates) "
    "against the CBT line, and exports as a one-page deal memo. A Scenario Room replays famous decision points from the archive with only at-the-time information, adjudicates counters by deterministic market rules, and grades process separately from outcome. A Horizon view walks every roster forward through "
    "2031 on the aging curves, bounded by control and contract years, with each club's season-by-season salary book: who falls off when, and what any proposed "
    "move does to the window.", st_b))

E.append(Paragraph(
    "<b>The Offseason Simulator: the whole winter, playable and priced.</b> Any club's actual 2026-27 offseason, staged the way the "
    "calendar flows: qualifying offers and arbitration tenders (arbitration priced backward-looking, off the platform "
    "season, so the tender decision is real), the exclusive re-sign window, then an open market where every free agent "
    "negotiates through a deterministic camp that values offers in its own preferred structure, spreading the same "
    "money over extra years is not a raise. Trades price in surplus value net of salary against an ownership capacity "
    "ceiling, so the Witt-for-Soto class of fantasy deal gets refused with the arithmetic shown, and a piece that fills "
    "the counterparty's computed roster hole is worth more in their eyes. An assistant GM reads the same engines out "
    "loud on every screen: tender and QO calls, re-sign or walk advice, negotiation reads against the ask, trade "
    "counsel with named bridge pieces from your own system, and real contract comps tagged with how each aged.", st_b))

E.append(Paragraph(
    "<b>The shopping fingerprint: what each front office actually buys.</b> Every acquisition a sitting regime has "
    "made since 2016 is joined to the player's public Statcast profile in the season the front office evaluated, "
    "z-scored within season. The persistent deviations are the regime's revealed preferences: one desk pays for "
    "velocity, another for strike-zone discipline, a third lives with swing-and-miss for power. On public aggregates "
    "it already reads out in plain language on every counterparty card; pointed at a club's internal evaluations, the "
    "same construction answers the sharper question, what do rivals pay for, and what do they undervalue that you can "
    "sell them.", st_b))

E.append(Paragraph("Validation", st_h))
tbl = Table([
    [Paragraph("<b>Accounting check</b><br/>A WAR-class metric must sum to team record. Roster-summed Ledger WAR "
               f"vs actual wins above a 48-win baseline, {A['n']} team-seasons (2015-2025).", st_stat),
     Paragraph(f"<b>r = {A['r']}</b> (R<super>2</super> = {A['r2']})<br/>slope {A['slope']}<br/>MAE {A['mae']} wins", st_stat)],
    [Paragraph("<b>Predictive check</b><br/>Does decision quality carry information about future results beyond the "
               f"current record? {P['n']} pooled regime-years across {P['regimes']} active and archive regimes: net decision value per season through year t, "
               "predicting the next two seasons' W% after controlling for W% to date.", st_stat),
     Paragraph(f"<b>partial r = {P['partial_r']}</b> (95% CI {P['partial_r_ci'][0]} to {P['partial_r_ci'][1]})<br/>"
               f"out-of-sample R<super>2</super> {P['oos_r2_base']} to {P['oos_r2_full']} (grouped 5-fold CV)<br/>"
               "no out-of-sample gain: reported as such", st_stat)],
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
    "put the accounting check at r = 0.93 (MAE 4.8 wins) across 330 team-seasons: fuller rosters sum closer to "
    "team records, which is itself evidence the metric is additive the way WAR must be. The predictive study: "
    f"{P['n']} pooled regime-years from {P['regimes']} regimes, decision value counted only as it had been realized, a cluster-bootstrap 95% interval on the "
    f"partial correlation of [{P['partial_r_ci'][0]:.2f}, {P['partial_r_ci'][1]:.2f}], and grouped out-of-sample cross-validation (R-squared {P['oos_r2_base']:.3f} without decision value, {P['oos_r2_full']:.3f} with it). "
    "The honest reading: the grades measure what decisions returned against what was expected; they are not a forecast "
    "of next year's standings. (An earlier version of this packet reported 0.27; that figure let later seasons leak into "
    "the predictor.) Known gaps (defense coverage thins before 2016) are disclosed on the site rather than patched quietly.", st_small))

E.append(Paragraph("Findings the consensus did not already have", st_h))
for f in [
    "<b>The best draft room of the data era is Billy Beane's Oakland</b>, +76 wins over what the league got from "
    "the same slots in the same drafts, ahead of John Schuerholz's Atlanta (+66); among sitting regimes it is Chris "
    "Antonetti's Cleveland at +41. Brian Cashman's full 29-year window grades -143 on decisions (trades -75, drafts "
    "-50 against their classes) beside the best results grade in the sport: the ledger prices decisions against what "
    "the same money and picks typically return, and puts both numbers on one row.",
    "<b>The Baltimore gap, quantified:</b> an A- on decisions (+24 in the draft room, +22 on the waiver wire) against "
    "a D in results through 2026. Whether you weight the machine or the harvest is a values question.",
    "<b>The best extension in the book is Detroit's 2008 Miguel Cabrera deal</b> at +27 wins against what that money "
    "typically buys; the worst is his 2014 extension (-23). Extensions are judged against the path they replaced "
    "(arbitration in controlled seasons, the free-agent market after) and centered by class, so the skill graded is "
    "picking the right player.",
    "<b>The ledger measured its own limits.</b> Split each front office's decisions into alternating halves: free "
    "agency repeats (split-half r 0.29), trades, drafts and waivers do not. The letters are an accounting of results "
    "against what a typical club gets from the same move, not a forecast, and the site says so.",
    "<b>Organizational DNA is measurable.</b> Measuring every player who changed orgs (performance in the two seasons "
    "after arriving vs the two before), the reputations fall out of the data unprompted: Cleveland improves "
    "defenders by about +2.5 runs per season and arms by +0.19 wins; Milwaukee, Tampa Bay, and San Diego profile as "
    "pitching labs; Texas arms regress. None of this was curated.",
    "<b>How titles actually get built, measured across all 29 champions 1998-2026:</b> free agency has been a "
    "majority channel exactly once (the 2009 Yankees), and the median title core was 48% built by its sitting "
    "regime in 1998-2009 against 74% in 2010-2026. The handed-down title has not gone away, though: seven of the "
    "seventeen since 2010 came on majority-inherited cores, including three straight (2021 Atlanta, 2022 Houston, "
    "2023 Texas, 85% Jon Daniels' roster). An earlier build read this as the inherited title going extinct; the "
    "corrected roster accounting says otherwise, and the site says so.",
    "<b>The system audits its own inputs.</b> Tracing the 2009 Yankees' roster exposed that the MLB transaction "
    "feed is empty before 2009; the fix was joining the Retrosheet archive (22,697 rows, 1998-2008, mapped to "
    "MLBAM ids via the Chadwick register), which put the Beckett-for-Hanley and Cabrera trades into the book and "
    "left the validation studies unchanged. A second audit (October 2026) caught a subtler hole: the player-value universe was built from transaction-touched players, so career-one-club stars who never hit free agency (Jose Altuve, Jose Ramirez, Salvador Perez, Ronald Acuna Jr., 133 significant players in all) were invisible; restoring them raised the accounting validation to r = 0.86 and put Perez back on the 2015 championship core. Both finds are documented, because a system that grades others must audit itself in public. Every graded trade also now carries market comps: the nearest deals "
    "by size and phase from a 5,804-deal archive, so each verdict reads against what deals of that shape cost.",
    "<b>Head-to-head records exist and are lopsided.</b> Every trade between two sitting regimes, netted from each "
    "seat: some relationships run 20+ wins one-sided across a decade of deals. Counterparty selection is a skill "
    "the public conversation does not price.",
]:
    E.append(Paragraph(f, st_b))

E.append(PageBreak())
E.append(Paragraph("What this machinery does inside a club", st_h))
E.append(Paragraph(
    "The public site is the free-data proof. Pointed at internal data, the same architecture is a decision-support "
    "system, and the Deal Desk tab is that system already running on the free-data versions of its inputs: "
    "<b>deadline pricing</b> (the live rental-market curve says what a win costs this July and whether an "
    "offer clears the market that actually exists), <b>contract pricing</b> (suggested terms calibrated against "
    "1,196 real signings, class-market extension baselines, CBT-aware deferral valuation, payroll and tax "
    "proximity on every proposal), <b>roster-horizon planning</b> (the window, season by season, and what any "
    "move does to it), <b>counterparty preparation</b> (every GM's trade record, channel tendencies, buy-low "
    "habits, and development effects before the call), <b>self-audit</b> (which channels actually produce, with "
    "process separated from outcome so scouting is not punished for variance), and <b>regime benchmarking</b> for "
    "ownership. Swap the public value metric for internal projections and the public prospect ranks for pref lists "
    "and every grade sharpens; nothing in the architecture assumes public data.", st_b))

E.append(Paragraph("How it was built", st_h))
E.append(Paragraph(
    "Python ingestion and scoring over the MLB Stats API and Retrosheet (282,000 transaction rows, 34,000 draft picks, 28,000 "
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
    "prospects mature. Retention joins the active composite as an expectation-conditioned gap (re-signings excluded, "
    "a compensation-pick credit per QO walkaway); archive cards do not carry it yet. Archive regimes grade trade, draft, and waiver "
    "channels; their FA book and development grades await the historical contract and prospect-list backfill, and "
    "regimes seated before the 2005 transaction-feed floor are truncated and flagged with their true start. Payroll "
    "arb and pre-arb figures are estimates (league minimum pre-arb; arbitration from an award model calibrated on 48 real "
    "2026 salaries, about $1.6M typical out-of-sample miss, on service time rebuilt from the transaction feed); the durability factor is a validated heuristic (it improves projection error and bias, at a small cost "
    "in rank correlation, and both numbers are published). The 2026 "
    "season and postseason are final in this build. A system like this earns trust by labeling its own soft spots, and "
    "that principle is applied everywhere.", st_b))
E.append(Spacer(1, 6))
E.append(HRFlowable(width="100%", thickness=1, color=RULE, spaceBefore=8, spaceAfter=8))
E.append(Paragraph(
    "<b>Sean Zerillo</b> · sean.zerillo@gmail.com · Live product: szerillo.github.io/front-office-ledger/prototype · "
    "Methodology, code, and data: github.com/szerillo/front-office-ledger. Everything in this document is computed "
    "and current through October 14, 2026.", st_stat))

doc.build(E)
print("packet built")
