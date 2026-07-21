"""
Front Office Ledger, decision assembler v0.1
=============================================
Raw transaction rows are not decisions. This module turns the ingested feed
(ledger.sqlite, from ingest_transactions.py) into the ledger's unit of
account: one row per DECISION, attributed to a focal team and regime, with
assets in/out and unresolved pieces flagged for human review.

Grouping rules
  TRADE       rows sharing (date, description) are one deal. The description
              text is identical across every row of a deal, so it is the
              natural grouping key. Assets split into in/out by to_team /
              from_team relative to the focal team. Rows with person_id NULL
              are picks, PTBNLs, or cash: kept, flagged unresolved.
  FA SIGNING  'Signed as Free Agent' rows; major vs minor league split by
              contract wording in the description. 'Signed' rows (extensions,
              int'l amateur deals) kept as a separate channel for review.
  WAIVER      'Claimed Off Waivers': a claim when to_team is focal, a loss
              when from_team is focal.
  RULE 5      'Rule 5 Selection' (and minors phase, logged separately).
  PASSIVE     'Declared Free Agency' when from_team is focal: the walk-year
              ledger. 'Released' likewise.
  NOISE       Status changes, options, recalls, assignments, number changes:
              excluded from the decision ledger (they are roster mechanics,
              not front-office value decisions).

Entity resolution
  person_id is the MLBAM id; resolve() joins it to the Chadwick Bureau
  register (key_mlbam -> key_bbref / key_fangraphs / key_retro) so the
  valuation pass can attach WAR from any licensed or self-computed source.

Output: decisions_<team>.csv plus a console summary, and a two-sided
assembly of any deal matching --show (substring of description).
"""
import argparse, csv, re, sqlite3, sys
from collections import defaultdict

NOISE = {"Status Change", "Assigned", "Optioned", "Recalled", "Number Change",
         "Outrighted", "Designated for Assignment", "Selected", "Returned",
         "Suspension"}

def load(db, team):
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT * FROM transactions WHERE from_team = ? OR to_team = ? ORDER BY date",
        (team, team)).fetchall()
    con.close()
    return [dict(r) for r in rows]

def assemble(rows, team):
    decisions, trades = [], defaultdict(list)
    seen_fa = set()
    for r in rows:
        t = r["type_desc"]
        if t in NOISE: continue
        if t == "Trade":
            trades[(r["date"], r["description"])].append(r)
        elif t == "Signed as Free Agent":
            key = (r["date"], r["person_id"])
            if key in seen_fa: continue
            seen_fa.add(key)
            minor = "minor league" in (r["description"] or "").lower()
            decisions.append(dict(date=r["date"], channel="fa_minor" if minor else "fa_major",
                                  direction="in", assets_in=r["person_name"], assets_out="",
                                  unresolved=0, desc=r["description"]))
        elif t == "Signed":
            decisions.append(dict(date=r["date"], channel="signed_other", direction="in",
                                  assets_in=r["person_name"], assets_out="", unresolved=0,
                                  desc=r["description"]))
        elif t == "Claimed Off Waivers":
            claim = r["to_team"] == team
            decisions.append(dict(date=r["date"], channel="waiver_claim" if claim else "waiver_loss",
                                  direction="in" if claim else "out",
                                  assets_in=r["person_name"] if claim else "",
                                  assets_out="" if claim else r["person_name"],
                                  unresolved=0, desc=r["description"]))
        elif t in ("Rule 5 Selection", "Rule 5 Draft Minors"):
            pick = r["to_team"] == team
            decisions.append(dict(date=r["date"], channel="rule5" + ("" if t == "Rule 5 Selection" else "_minors"),
                                  direction="in" if pick else "out",
                                  assets_in=r["person_name"] if pick else "",
                                  assets_out="" if pick else r["person_name"],
                                  unresolved=0, desc=r["description"]))
        elif t in ("Declared Free Agency", "Released"):
            # feed quirk: for departures the losing club sits in to_team
            if r["from_team"] == team or r["to_team"] == team:
                decisions.append(dict(date=r["date"], channel="passive_loss", direction="out",
                                      assets_in="", assets_out=r["person_name"], unresolved=0,
                                      desc=r["description"]))
    for (d, desc), rs in trades.items():
        ins  = sorted({x["person_name"] for x in rs if x["to_team"] == team and x["person_name"]})
        outs = sorted({x["person_name"] for x in rs if x["from_team"] == team and x["person_name"]})
        unresolved = sum(1 for x in rs if not x["person_name"])
        # dedupe: the feed often repeats each player row once per club
        decisions.append(dict(date=d, channel="trade", direction="both",
                              assets_in="; ".join(ins), assets_out="; ".join(outs),
                              unresolved=unresolved, desc=desc))
    decisions.sort(key=lambda x: x["date"])
    return decisions

def summarize(decisions, team, label):
    from collections import Counter
    c = Counter(d["channel"] for d in decisions)
    print(f"\n{'=' * 70}\nDECISION LEDGER: {team}  ({label})\n{'=' * 70}")
    print(f"  {len(decisions)} decisions assembled from the raw feed. By channel:")
    for k, v in c.most_common(): print(f"    {v:>4}  {k}")
    unres = sum(1 for d in decisions if d["unresolved"])
    print(f"  trades containing unresolved assets (picks/PTBNL/cash): {unres}")

def show_deal(decisions, team, needle):
    for d in decisions:
        if d["channel"] == "trade" and needle.lower() in (d["desc"] or "").lower():
            print(f"\n  [{team}]  {d['date']}")
            print(f"    IN : {d['assets_in'] or '(none listed)'}")
            print(f"    OUT: {d['assets_out'] or '(none listed)'}")
            if d["unresolved"]:
                print(f"    ⚑ {d['unresolved']} unresolved asset row(s): pick / PTBNL / cash, needs human link")
            return

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="ledger.sqlite")
    ap.add_argument("--show", default=None)
    a = ap.parse_args()
    REGIMES = [("Baltimore Orioles", "Mike Elias regime, Nov 2018 to present"),
               ("Milwaukee Brewers", "Matt Arnold regime, Oct 2022 to present")]
    all_out = {}
    for team, label in REGIMES:
        rows = load(a.db, team)
        ds = assemble(rows, team)
        all_out[team] = ds
        summarize(ds, team, label)
        slug = team.split()[-1].lower()
        with open(f"decisions_{slug}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(ds[0].keys())); w.writeheader(); w.writerows(ds)
    if a.show:
        print(f"\n{'=' * 70}\nTWO-SIDED ASSEMBLY: deals matching '{a.show}'\n{'=' * 70}")
        for team, _ in REGIMES:
            show_deal(all_out[team], team, a.show)
