"""
Scenario Room data pack: historic GM decision points generated from the
ledger's own archive. Writes scenarios.json.

Each scenario carries: the seat (team, exec, date, phase), at-the-time
context (record/GB/division rank from the standings API, win-curve leverage,
computed roster-need groups, era $/win), the offer (pieces each way with
age, platform WAR, at-the-time prospect rank), a deliberately crude ex-ante
expectation per side (last full season's rate times typical control for the
bucket; prospects at rank expectation; unranked minors at the 0.41 empirical
mean), the market read that follows, deterministic counter adjudication, and
the realized outcome from the deal archive.
"""
import json, sqlite3, urllib.request, time, sys
from collections import defaultdict

sys.path.insert(0, "/work")

LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
AGES = json.load(open("/work/ages.json"))
POS = json.load(open("/work/positions.json"))
PITPOS = {"RHP", "LHP", "SP", "RP", "P"}
cfg = json.load(open("/work/regimes.json"))
hist = json.load(open("/work/regimes_hist.json"))
ARCH = json.load(open("/work/deal_archive.json"))
DESK = json.load(open("/work/desk_data.json"))
RANKS = defaultdict(dict)   # year -> pid -> rank
for rr in json.load(open("/work/prospect_ranks.json")):
    RANKS[rr["year"]][rr["pid"]] = rr["rank"]

DPWH = DESK["market"]["dpwHist"]
VRANK = DESK["vrank"]
RATIO = {k: v["ratio"] for k, v in DESK["market"]["buckets"].items()}
BUST = {k: v["bust"] for k, v in DESK["market"]["buckets"].items()}
CTRLMULT = {"rental": 0.6, "+1": 1.6, "+2": 2.6, "3+": 3.5}

TID2AB = {r["teamId"]: r["abbr"] for r in cfg["regimes"]}
TID2TEAM = {r["teamId"]: r["team"] for r in cfg["regimes"]}
TEAMNAMES = {r["teamId"]: set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in cfg["regimes"]}
NAME2TID = {}
for tid, names in TEAMNAMES.items():
    for nm in names: NAME2TID[nm] = tid

BYPID = {}
for pid, rec in LVM.items():
    d = defaultdict(float)
    for (y, tm, v) in rec["rows"]: d[y] += v
    BYPID[pid] = dict(d)

def vrank_ev(rank):
    pts = VRANK
    if rank <= pts[0][0]: return pts[0][1]
    for (r1, v1), (r2, v2) in zip(pts, pts[1:]):
        if rank <= r2:
            return v1 + (v2 - v1) * (rank - r1) / (r2 - r1)
    return pts[-1][1]

def leverage(w):
    import math
    return 0.5 + 1.3 * math.exp(-((w - 89) ** 2) / 200.0)

def get(u, tries=3):
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
        except Exception as e:
            if a == tries - 1: print("FETCH FAIL", e, u[:110])
            time.sleep(2 + 2 * a)
    return {}

def standings(season, date=None, tid=None):
    u = f"https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season={season}&standingsTypes=regularSeason"
    if date: u += f"&date={date}"
    d = get(u)
    for g in d.get("records", []):
        for t in g.get("teamRecords", []):
            if t["team"]["id"] == tid:
                return dict(w=t["wins"], l=t["losses"], gb=t.get("gamesBack", "-"), rank=t.get("divisionRank"))
    return None

def exec_at(tid, date):
    cands = []
    for r in hist if isinstance(hist, list) else hist.get("regimes", []):
        if r.get("teamId") == tid and r.get("start", "9999") <= date <= r.get("end", "9999"):
            cands.append(r.get("exec"))
    for r in cfg["regimes"]:
        if r["teamId"] == tid and r.get("start", "9999") <= date:
            cands.append(r["exec"])
    return cands[0] if cands else None

def needs(tid, season):
    tot = defaultdict(float)
    names = TEAMNAMES[tid]
    for pid, rec in LVM.items():
        for (y, tm, v) in rec["rows"]:
            if y == season and tm in names:
                p = POS.get(str(pid))
                g = "P" if p in PITPOS else ("C" if p == "C" else ("OF" if p in ("LF","CF","RF","OF","DH") else ("IF" if p in ("1B","2B","3B","SS") else None)))
                if g: tot[g] += v
    groups = sorted(tot.items(), key=lambda x: x[1])
    return [[g, round(v, 1)] for g, v in groups[:2]]

# The Pipeline rank archive starts in 2011. For the pre-2011 scenarios the
# prospect pieces carry a curated consensus tier (rank-equivalent on our own
# curve), flagged as curated on the page. Tier only, no false precision.
CURATED_TIER = {
    "Hanley Ramirez": 8, "Cameron Maybin": 8, "Andrew Miller": 15,
    "Matt LaPorta": 30, "Michael Brantley": 75, "Anibal Sanchez": 40,
    "Jake Odorizzi": 75, "Jeremy Jeffress": 90,
}

def piece_info(pid, name, yr, month):
    pid = int(pid) if pid else None
    d = BYPID.get(pid, {}) if pid else {}
    plat_season = yr if month >= 9 else yr - 1
    plat = round(d.get(plat_season, 0.0), 1)
    cur = round(d.get(yr, 0.0), 1)
    by = AGES.get(str(pid), 0)
    age = yr - by if by and 14 < yr - by < 50 else None
    has_mlb = any(y <= yr and abs(v) > 0.05 for y, v in d.items())
    rank = RANKS.get(yr, {}).get(pid, 0)
    curated = 0
    import unicodedata
    plain = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    if not rank and not has_mlb and yr < 2011 and plain in CURATED_TIER:
        rank, curated = CURATED_TIER[plain], 1
    return dict(pid=pid, name=name, age=age, plat=plat, cur=cur, rank=rank, mlb=1 if has_mlb else 0, cur8d=curated)

def exp_value(pieces, ck, headline):
    tot = 0.0
    for pc in pieces:
        if not pc["mlb"]:
            tot += vrank_ev(pc["rank"]) if pc["rank"] else 0.41
        else:
            base = max(pc["plat"], 0.0)
            tot += base * (CTRLMULT[ck] if pc["name"] == headline else 1.5)
    return round(tot, 1)

con = sqlite3.connect("/work/ledger.sqlite")
def deal_pieces(date, buyer_tid, like):
    rows = con.execute(
        "SELECT DISTINCT person_id, person_name, from_team, to_team FROM sweep_tx "
        "WHERE date=? AND description LIKE ? AND type_desc LIKE '%rade%'", (date, f"%{like}%")).fetchall()
    buyer_names = TEAMNAMES[buyer_tid]
    recv, sent, seller_tid = [], [], None
    for pid, nm, ft, tt in rows:
        if tt in buyer_names: recv.append((pid, nm)); seller_tid = seller_tid or NAME2TID.get(ft)
        elif ft in buyer_names: sent.append((pid, nm))
    return recv, sent, seller_tid

# ---------------- trade scenarios ----------------
# (date, buyer_abbr, headline, seat, one-line computed-adjacent setup)
TRADES = [
    ("2007-12-04", "DET", "Miguel Cabrera", "buyer",
     "Florida is holding an open auction for a 24-year-old MVP-track bat with two arb years left."),
    ("2005-11-24", "BOS", "Josh Beckett", "buyer",
     "Florida will move its 25-year-old ace, but only for your best position prospect."),
    ("2016-07-25", "CHC", "Aroldis Chapman", "buyer",
     "You are chasing the franchise's first title in 108 years and the bullpen is the soft spot. New York wants your top infield prospect for three months of the best closer alive."),
    ("2014-07-31", "BAL", "Andrew Miller", "buyer",
     "Deadline day. You lead the division and want a shutdown lefty for October; Boston's price is a 21-year-old pitching prospect."),
    ("2016-07-31", "CLE", "Andrew Miller", "buyer",
     "You lead the division with the best rotation in the league; New York is selling a dominant reliever with two and a half controlled years."),
    ("2017-08-31", "HOU", "Justin Verlander", "buyer",
     "August 31, minutes before the postseason-eligibility deadline. Detroit will finally move its franchise ace, cash included, for prospects."),
    ("2010-12-19", "MIL", "Zack Greinke", "buyer",
     "You are a mid-market club two wins short of contention; Kansas City will move a former Cy Young winner with two controlled years for a package of your young core."),
    ("2008-07-07", "MIL", "CC Sabathia", "buyer",
     "Early July, wild-card race. Cleveland is selling the reigning Cy Young winner as a pure three-month rental."),
    ("2020-02-10", "LAD", "Mookie Betts", "seller",
     "Ownership wants the payroll reset and the superstar has one year left before free agency. Los Angeles is offering a major-league outfielder and a pitching prospect."),
    ("2022-08-02", "SD", "Juan Soto", "buyer",
     "The franchise bat of his generation is somehow available at 23 with two and a half controlled years. Washington wants your entire prospect shelf."),
]

scenarios = []
for date, ab, headline, seat, setup in TRADES:
    yr, mo = int(date[:4]), int(date[5:7])
    cand = [x for x in ARCH if x["d"] == date and x["ab"] == ab and headline.lower() in x["who"].lower()]
    if not cand: print("MISS archive", date, ab, headline); continue
    deal = cand[0]
    buyer_tid = deal["tid"]
    recv_raw, sent_raw, seller_tid = deal_pieces(date, buyer_tid, headline.split()[-1])
    if not recv_raw or not sent_raw or not seller_tid: print("MISS pieces", date, headline); continue
    recv = [piece_info(p, n, yr, mo) for p, n in recv_raw]
    sent = [piece_info(p, n, yr, mo) for p, n in sent_raw]
    seat_tid = buyer_tid if seat == "buyer" else seller_tid
    # context
    deadline = deal["ph"] == "deadline"
    season = yr if (deadline or mo >= 9) else (yr - 1 if mo <= 3 else yr)
    st = standings(season, date=f"{mo:02d}/{int(date[8:10]):02d}/{yr}" if deadline else None, tid=seat_tid)
    if not st: print("MISS standings", date, ab); continue
    wproj = round(st["w"] / max(st["w"] + st["l"], 1) * 162)
    nd = needs(seat_tid, season)
    ck = deal["ck"]
    exp_recv = exp_value(recv, ck, headline)
    exp_sent = exp_value(sent, ck, headline)
    # seat-relative views
    if seat == "buyer":
        my_recv, my_sent = recv, sent
        my_exp_in, my_exp_out = exp_recv, exp_sent
        out_in, out_out = deal["recv"], deal["paid"]
    else:
        my_recv, my_sent = sent, recv
        my_exp_in, my_exp_out = exp_sent, exp_recv
        out_in, out_out = deal["paid"], deal["recv"]
    exp_market_price = round((my_exp_in if seat == "buyer" else my_exp_out) * RATIO[ck], 1)
    # ex-ante call from the BUYER's price regardless of seat
    buyer_out = my_exp_out if seat == "buyer" else my_exp_in
    buyer_in = my_exp_in if seat == "buyer" else my_exp_out
    exp_price = round(buyer_in * RATIO[ck], 1)
    r = buyer_out / max(exp_price, 0.3)
    call = "BELOW" if r < 0.7 else ("ABOVE" if r > 1.4 else "MARKET")
    scenarios.append(dict(
        id=f"tr-{yr}-{ab}-{headline.split()[-1].lower()}", kind="trade", seat=seat,
        team=TID2AB[seat_tid], teamName=TID2TEAM.get(seat_tid, ""), opp=TID2AB.get(buyer_tid if seat == "seller" else seller_tid, "?"),
        exec_=exec_at(seat_tid, date), date=date, phase=deal["ph"], setup=setup,
        ctx=dict(w=st["w"], l=st["l"], gb=st["gb"], rank=st["rank"], season=season,
                 lev=round(leverage(wproj if deadline else st["w"]), 2), dpw=DPWH.get(str(min(yr, 2026)), 9.7),
                 needs=nd),
        recv=my_recv, send=my_sent, ck=ck, bust=BUST[ck],
        exante=dict(expIn=my_exp_in, expOut=my_exp_out, expPrice=exp_price, call=call, ratio=RATIO[ck]),
        outcome=dict(recv=out_in, paid=out_out, net=round(out_in - out_out, 1), settled=1),
    ))
    print("built", scenarios[-1]["id"], "call", call, "net", scenarios[-1]["outcome"]["net"])

# ---------------- contract scenarios (FA + extensions) ----------------
BOOK = DESK["book"]   # [pl, off, ab, yrs, tot, age, pit, plat1, plat2, realized, elapsed, pid, typ]

def implied_cost(off, yrs, tot, span):
    aav = tot / yrs
    return sum(aav / DPWH.get(str(min(off + i, 2026)), 9.7) for i in range(1, span + 1))

def surplus(row):
    pl, off, ab, yrs, tot, age, pit, p1, p2, realized, elapsed, pid, typ = row
    if realized == "" or elapsed < yrs: return None
    return realized - implied_cost(off, yrs, tot, yrs)

def comp_terms(row):
    """Market-comp terms at that winter from strictly earlier FA deals (same logic as dkSuggest)."""
    pl, off, ab, yrs, tot, age, pit, p1, p2 = row[:9]
    pBlend, pPeak = p1 * 0.65 + p2 * 0.35, max(p1, p2)
    cands = []
    for c in BOOK:
        if c[1] >= off or c[12] == 1 or c[6] != pit: continue   # same player type only
        cBlend, cPeak = c[7] * 0.65 + c[8] * 0.35, max(c[7], c[8])
        s = abs(cBlend - pBlend) + abs(cPeak - pPeak) * 0.5 + abs(c[5] - age) * 0.45
        cands.append((s, c))
    cands.sort(key=lambda x: x[0])
    comps = [c for _, c in cands[:8]]
    if not comps: return None
    yr1 = min(off + 1, 2026)
    med = lambda a: sorted(a)[len(a) // 2]
    mY = med([c[3] for c in comps])
    mA = med([(c[4] / c[3]) * (DPWH[str(yr1)] / DPWH[str(min(c[1] + 1, 2026))]) for c in comps])
    return dict(mktY=mY, mktTot=round(mY * mA), comps=[[c[0], c[1], c[3], round(c[4], 1)] for c in comps[:4]])

FA_PICKS = [("Max Scherzer", 2014), ("Albert Pujols", 2011), ("Chris Davis", 2015), ("Jon Lester", 2014)]
FA_SETUP = {
    "Max Scherzer": "Your window is open and the rotation needs a true one. The best arm on the market wants seven years, half of it deferred.",
    "Albert Pujols": "The best hitter of his generation is a free agent at 31. Ownership wants the splash.",
    "Chris Davis": "Your own slugger, fresh off a 47-homer platform year, is a free agent. The fan base wants him back.",
    "Jon Lester": "A playoff-proven ace at 30, and signing him announces the rebuild is over.",
}
EXT_PICKS = [("Jose Ramirez", 2017)]
EXT_SETUP = {"Jose Ramirez": "A 24-year-old utility infielder just broke out. Lock him up now through his arb years, or wait for a second season of proof?"}

for picks, kindlbl, setups in ((FA_PICKS, "fa", FA_SETUP), (EXT_PICKS, "ext", EXT_SETUP)):
    for nm, off in picks:
        rows = [r for r in BOOK if r[0] == nm and r[1] == off]
        if not rows: print("MISS book", nm, off); continue
        row = rows[0]
        pl, off, ab, yrs, tot, age, pit, p1, p2, realized, elapsed, pid, typ = row
        tid = {v: k for k, v in TID2AB.items()}.get(ab)
        st = standings(off, tid=tid)
        sur = surplus(row)
        ct = comp_terms(row)
        scenarios.append(dict(
            id=f"{kindlbl}-{off}-{nm.split()[-1].lower()}", kind=kindlbl, seat="club",
            team=ab, teamName=TID2TEAM.get(tid, ""), opp=None, exec_=exec_at(tid, f"{off}-12-01"),
            date=f"{off}-12-01" if kindlbl == "fa" else f"{off+1}-03-01", phase="offseason",
            setup=setups[nm],
            ctx=dict(w=st["w"] if st else None, l=st["l"] if st else None, gb=st["gb"] if st else "-",
                     rank=st["rank"] if st else None, season=off,
                     lev=round(leverage(st["w"]), 2) if st else 1.0, dpw=DPWH.get(str(min(off + 1, 2026)), 9.7),
                     needs=needs(tid, off) if tid else []),
            player=dict(name=pl, age=age, pit=pit, plat=p1, prev=p2),
            terms=dict(yrs=yrs, tot=round(tot, 1)),
            market=ct,
            outcome=dict(realized=realized, surplus=round(sur, 1) if sur is not None else None,
                         perYear=round(realized / max(elapsed, 1), 1), elapsed=elapsed, settled=1 if elapsed >= yrs else 0),
        ))
        print("built", scenarios[-1]["id"], "surplus", scenarios[-1]["outcome"]["surplus"])

# ---------------- live scenario (unsettled, 2026) ----------------
rawranks = json.load(open("/work/prospect_ranks.json"))
rojas = [(rr["pid"], rr["rank"]) for rr in rawranks if rr["year"] == 2026 and rr["name"] == "Jefferson Rojas"]
def pid_by_name(nm):
    for pid, rec in LVM.items():
        if rec["name"] == nm: return pid
    return None
st = standings(2026, date="08/03/2026", tid=121)
holmes = piece_info(pid_by_name("Clay Holmes"), "Clay Holmes", 2026, 8)
scenarios.append(dict(
    id="live-2026-rojas", kind="trade", seat="seller",
    team="NYM", teamName="New York Mets", opp="CHC", exec_=exec_at(121, "2026-08-03"),
    date="2026-08-03", phase="deadline",
    setup="Deadline day, and you are hanging at the edge of the wild-card race. Chicago wants your closer and a veteran outfielder, and offers its shortstop prospect back.",
    ctx=dict(w=st["w"] if st else 57, l=st["l"] if st else 54, gb=st["gb"] if st else "-",
             rank=st["rank"] if st else None, season=2026, lev=round(leverage(round((st["w"]/(st["w"]+st["l"]))*162)), 2) if st else 1.0,
             dpw=9.7, needs=needs(121, 2026)),
    recv=[dict(pid=None, name="Jefferson Rojas", age=21, plat=0.0, cur=0.0,
               rank=(rojas[0][1] if rojas else 45), mlb=0, cur8d=0)],
    send=[holmes, piece_info(pid_by_name("Tyrone Taylor"), "Tyrone Taylor", 2026, 8)],
    ck="+1", bust=BUST["+1"],
    exante=dict(expIn=round(vrank_ev(rojas[0][1]) if rojas else vrank_ev(45), 1),
                expOut=round(max(holmes["plat"], 0) * 1.6, 1), expPrice=None, call="SELLER", ratio=RATIO["+1"]),
    outcome=dict(recv=None, paid=None, net=-6.4, settled=0,
                 note="Ledger Projection v1 projected final for the Mets' seat; Holmes and Taylor produced for Chicago immediately while Rojas' value is still rank expectation."),
))
print("built live-2026-rojas")

json.dump(scenarios, open("/work/scenarios.json", "w"), separators=(",", ":"))
import os
print("scenarios:", len(scenarios), "|", round(os.path.getsize("/work/scenarios.json")/1024, 1), "KB")
