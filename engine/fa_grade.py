"""
FA CHANNEL GRADING: contracts meet the ledger.
Sources: ESPN free-agent tables 2006-2021 (contracts_espn.csv, 1,506 signed
deals) + curated majors for the 2022-2024 winters (contracts_recent.py,
verify pass pending). 2025-26 winter ungraded (season in progress).

Rule (documented): for a matched signing, implied wins = sum over elapsed
contract seasons of AAV / $-per-win(season); realized = LVM on the signing
org over those seasons; net = realized - implied. Traded-away or released
players keep accruing 'paid' but stop accruing 'realized' on your ledger,
which is the honest cost of a bad signing. Unmatched major-league signings
(depth deals below reporting radar, name mismatches) stay ungraded and are
counted. A regime's FA channel gets a letter only when >= 8 signings
matched; below that it stays pending.
"""
import csv, json, sqlite3
from collections import defaultdict
from contracts_recent import RECENT
from contracts_ext import QO, FA_CBT
from fa_grade_lib import norm, DPW

QO_CHARGE = 1.0  # wins: the draft pick forfeited signing another club's QO'd free agent
                 # (v5.9: QO table complete for the 2012-13 to 2025-26 offseasons)
MOVE_POP = []   # v5.5: (cost in wins, net) for every graded signing
                 # (second-round-pick value on our pick curve; flat v1)

POS = json.load(open("/work/positions.json"))
PITPOS = {"RHP", "LHP", "SP", "RP"}
cfg = json.load(open("/work/regimes.json"))
ALIAS = {int(k): set(v) for k, v in cfg["aliases"].items()}
REG = {r["teamId"]: r for r in cfg["regimes"]}
ABBR2TID = {r["abbr"]: r["teamId"] for r in cfg["regimes"]}
LVM = {k: v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}

# contracts: key (player_norm, offseason) -> (tid, years, total)
contracts = defaultdict(list)
def short_to_tid(short):
    for r in cfg["regimes"]:
        names = ALIAS.get(r["teamId"], {r["team"]})
        if any(short and short.lower() in nm.lower() for nm in names):
            return r["teamId"]
    return None
with open("/work/repo/data/contracts_espn.csv") as f:   # v5.9: the one maintained copy
    for row in csv.DictReader(f):
        tid = short_to_tid(row["to_team"])
        if tid: contracts[(row["player_norm"], int(row["offseason"]))].append(
            (tid, int(row["years"]), float(row["total_m"]), "espn"))
for off, pl, ab, yrs, tot in RECENT:
    contracts[(norm(pl), off)].append((ABBR2TID[ab], yrs, float(tot), "curated"))
print(f"contract book: {sum(len(v) for v in contracts.values())} deals")

con = sqlite3.connect("/work/ledger.sqlite"); con.row_factory = sqlite3.Row
res = json.load(open("/work/sweep_results.json"))

def grade(nps):
    for thr, g in [(2.6,80),(1.8,75),(1.2,70),(0.8,65),(0.5,60),(0.2,55),
                   (-0.2,50),(-0.6,45),(-1.0,40),(-1.6,35)]:
        if nps >= thr: return g
    return 30
def grade_comp(nps):
    for thr, g in [(8.0,80),(5.5,75),(3.5,70),(2.2,65),(1.2,60),(0.4,55),
                   (-0.4,50),(-1.2,45),(-2.2,40),(-3.5,35)]:
        if nps >= thr: return g
    return 30

# v5.8: priced from the contract book (contract_book.py): the seasons a deal
# OWNS (a later contract owns its own), held by the signing club until it
# trades him (the trade carries the rest, salary included); a release keeps
# the dead money on the club. Expectation per season = cost at market $/win
# (salary above the minimum) x what a typical club gets back for free-agent
# money IN THAT CONTRACT YEAR (early years return more than late ones), so an
# in-progress deal is judged against the years it has played.
CB = json.load(open("/work/contract_book.json"))
CB_DPW = {int(k): v for k, v in CB["dpw"].items()}
TYP = {int(k): v for k, v in CB["typical_fa"].items()}
ERA = CB.get("era_adj_pre2006", 1.0); LMIN = CB.get("league_min", 0.75)
BAND = {int(k): v for k, v in CB.get("band_mult", {}).items()}
def typical(k, y, b=None):
    """v5.9: by contract year AND deal size (contract_book.py band multipliers)"""
    return TYP.get(min(k, 5), CB["typical_fa_all"]) * (ERA if y < 2006 else 1.0) * (BAND.get(b, 1.0) if b is not None else 1.0)
# v5.9: posting fees are part of the price of a posted player (charged as
# year-one money; public reports of the fee paid to the NPB/KBO club)
POSTING_FEE = {   # (player id, signing club) -> fee $M
    (493137, "BOS"): 51.11,  # Daisuke Matsuzaka, Dec 2006
    (506432, "NYY"): 26.0,   # Kei Igawa, Dec 2006
    (506433, "TEX"): 51.7,   # Yu Darvish, Jan 2012
    (547888, "NYY"): 20.0,   # Masahiro Tanaka, Jan 2014
    (547943, "LAD"): 25.7,   # Hyun Jin Ryu, Dec 2012
    (628317, "LAD"): 20.0,   # Kenta Maeda, Jan 2016
    (660271, "LAA"): 20.0,   # Shohei Ohtani, Dec 2017 (signing as an international pro: IFA channel)
    (579328, "SEA"): 10.275, # Yusei Kikuchi, Jan 2019
    (673548, "CHC"): 14.6,   # Seiya Suzuki, Mar 2022
    (807799, "BOS"): 15.4,   # Masataka Yoshida, Dec 2022
    (808967, "LAD"): 50.6,   # Yoshinobu Yamamoto, Dec 2023
    (684007, "CHC"): 9.825,  # Shota Imanaga, Jan 2024
    (808982, "SF"): 18.825, # Jung Hoo Lee, Dec 2023
    (673490, "SD"): 5.3,    # Ha-Seong Kim, Jan 2021
    (628356, "PIT"): 5.0,    # Jung Ho Kang, Jan 2015
    (457292, "MIN"): 5.33,   # Tsuyoshi Nishioka, Dec 2010
}
FA_BOOK = defaultdict(list)
for c in CB["book"]:
    if c["kind"] == "fa": FA_BOOK[(int(c["pid"]), c["club"])].append(c)
TID2AB = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
def priced(tid, start, end="9999-12-31"):
    rows = con.execute("""select date, person_id, person_name from sweep_tx
        where team_id=? and date>=? and date<=? and type_desc='Signed as Free Agent'
        and lower(description) not like '%minor league%' and person_id is not null""",
        (tid, start, end)).fetchall()
    seen = set(); used = set(); out = []
    for x in rows:
        k = (x["date"], x["person_id"])
        if k in seen: continue
        seen.add(k)
        ty, tm = int(x["date"][:4]), int(x["date"][5:7])
        offs = (ty, ty - 1) if tm >= 10 else (ty - 1, ty)     # v5.8: Nov/Dec re-signings belong to that winter
        c = None
        for off in offs:
            for cc in FA_BOOK.get((int(x["person_id"]), TID2AB[tid]), []):
                if cc["start"] == off + 1 and id(cc) not in used: c = cc; break
            if c: break
        if not c:
            out.append(dict(x=x, hit=None)); continue
        used.add(id(c))
        off = c["start"] - 1
        held = [h for h in c.get("held", []) if h[1] <= 2026]
        if not held: out.append(dict(x=x, hit=(off, c["yrs"], c["tot"], c["src"]), open=True)); continue
        realized = sum(h[2] for h in held)
        b = c.get("band")
        cost = sum(max(0.0, c["aav"] - LMIN) / CB_DPW.get(h[1], 9.7) * h[3] for h in held)
        expected = sum(max(0.0, c["aav"] - LMIN) / CB_DPW.get(h[1], 9.7) * h[3] * typical(h[0], h[1], b) for h in held)
        fee = POSTING_FEE.get((int(x["person_id"]), TID2AB[tid]), 0.0)
        if fee:
            fc = fee / CB_DPW.get(held[0][1], 9.7)
            cost += fc; expected += fc * typical(1, held[0][1], b)
        # v5.9: per-season increments (value-time), so the card's cumulative
        # chart carries free agency too
        inc = {}
        for i_, h in enumerate(held):
            e_ = max(0.0, c["aav"] - LMIN) / CB_DPW.get(h[1], 9.7) * h[3] * typical(h[0], h[1], b)
            if i_ == 0 and fee: e_ += fee / CB_DPW.get(held[0][1], 9.7) * typical(1, held[0][1], b)
            inc[h[1]] = inc.get(h[1], 0.0) + h[2] - e_
        out.append(dict(x=x, hit=(off, c["yrs"], c["tot"], c["src"]), pn=norm(x["person_name"]), cbt=None, fee=fee,
                        implied=cost, expected=expected, realized=realized, seasons=[h[1] for h in held], inc=inc))
    return out
TYPICAL = CB["typical_fa_all"]
print(f"typical return by contract year {TYP} (pooled {TYPICAL}), pre-2006 x{ERA}")

print(f"\n{'team':<5}{'FA net':>8}{'matched':>9}{'majors':>8}   best / worst signing")
def grade_file(res, archive=False):
  for r in res:
    tid = r["teamId"]
    if archive:
        start = max(r["startDate"], "1998-01-01"); end = r.get("endDate") or "9999-12-31"
    else:
        start = max(REG[tid]["start"], "1998-01-01"); end = "9999-12-31"   # v5.8: the book now reaches the 1997-98 winter
    sigs = priced(tid, start, end)
    majors = [s["x"] for s in sigs]
    net = 0.0; matched = 0; decs = []; allx = []   # v5.7: every major-league signing, priced or not
    fa_inc = {}
    fa_dna = dict(pit=0.0, bat=0.0)
    for s_ in sigs:
        x = s_["x"]
        if not s_.get("hit"):
            allx.append([x["date"], x["person_name"], None, None, None, None, None, x["person_id"]])
            continue
        if s_.get("open"): continue
        off, yrs, tot, src = s_["hit"]; pn = s_["pn"]; cbt = s_["cbt"]
        implied, realized, expected = s_["implied"], s_["realized"], s_["expected"]
        n = realized - expected
        notes = []
        if cbt: notes.append(f"CBT ${cbt:.0f}M used for cost")
        if s_.get("fee"): notes.append(f"${s_['fee']:.1f}M posting fee charged")
        qo = (pn, off) in QO
        if qo:
            n -= QO_CHARGE
            notes.append("QO signing, draft comp charged")
        note = (", " + ", ".join(notes)) if notes else ""
        net += n; matched += 1
        for _y, _v in s_["inc"].items(): fa_inc[_y] = fa_inc.get(_y, 0.0) + _v
        fa_dna["pit" if POS.get(str(x["person_id"])) in PITPOS else "bat"] += n
        fasides = [["Production (Ledger WAR on club, elapsed seasons)", [[x["person_name"], f"{realized:+.1f}"]]],
                   ["What a typical club gets for this money" + (" (QO draft comp included)" if qo else ""),
                    [[f"${tot:.0f}M over {yrs} yr: {implied:.1f} wins of cost at market $/win x the typical return for those contract years", f"{-(expected + (QO_CHARGE if qo else 0)):+.1f}"]]]]
        MOVE_POP.append([round(implied, 2), round(n, 2)])
        allx.append([x["date"], x["person_name"], yrs, round(tot, 1), round(realized, 1), round(expected + (QO_CHARGE if qo else 0), 1), round(n, 1), x["person_id"], round(implied, 2)])
        decs.append(dict(d=x["date"], ch="fa", net=round(n, 1), st=round(implied, 2),
                         h=f"Signed {x['person_name']} · {yrs} yr / ${tot:.1f}M ({off}-{str(off+1)[2:]} winter{note})",
                         sides=fasides, pids=[x["person_id"]]))
    covered = matched >= 3     # v5.7: the same evidence floor as every other channel (was 8)
    r["allx_fa"] = allx
    r["chan"]["fa"] = dict(net=round(net, 1),   # v5.9: the net always counts; a letter needs three priced deals
                           g=grade(net / r["seasons"]) if covered else None,
                           n=matched, majors=len(majors), typical=round(TYPICAL, 3),
                           raw=r["chan"]["fa"].get("net", r["chan"]["fa"].get("raw", 0)))
    if matched:
        r["total"] = round(r["total"] + net, 1)
        r["forGrade"] = grade_comp(r["total"] / r["seasons"])
        if r.get("cum"):
            y0c = r["start"]
            r["cum"] = [round(v + sum(x for yy, x in fa_inc.items() if yy <= y0c + i), 1) for i, v in enumerate(r["cum"])]
    decs.sort(key=lambda d: -abs(d["net"]))
    r["fa_tops"] = decs[:4]
    r.setdefault("dna", {})["fa"] = {k: round(v, 1) for k, v in fa_dna.items()}
    r["fa_led"] = dict(best=sorted([d for d in decs if d["net"] > 0], key=lambda x: -x["net"])[:5],
                       worst=sorted([d for d in decs if d["net"] < 0], key=lambda x: x["net"])[:5])
    best = decs[0]["h"][:40] + f" ({decs[0]['net']:+.1f})" if decs else "-"
    worst = min(decs, key=lambda d: d["net"])["net"] if decs else 0
    print(f"{r['abbr']:<5}{(net if covered else 0):>+8.1f}{matched:>9}{len(majors):>8}   {best} / worst {worst:+.1f}")

grade_file(res)
H = json.load(open("/work/hist_results.json"))
grade_file(H, archive=True)      # v5.9: archive regimes are graded on free agency too
json.dump(H, open("/work/hist_results.json", "w"), indent=1)
json.dump(res, open("/work/sweep_results.json", "w"), indent=1)
json.dump({"fa": MOVE_POP}, open("/work/move_pop_fa.json", "w"))
print("\nmerged graded FA into sweep_results.json")
