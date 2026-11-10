"""Prospect bios (Nov 10 2026): how every prospect in the pool entered pro ball.

  draft : year, round, overall pick, signing bonus, school  (draft_picks table)
  intl  : signing date and club from the transaction feed; the bonus where a
          public signing-day tracker lists it (intl_bonus_src.txt, sources in its header)

Writes prospect_bio.json: {pid: ["d", year, round, pick, bonus$K|None, school]}
                          {pid: ["i", year, clubAbbr, bonus$K|None]}
Read by desk_data.py (shipped as DESK.bio)."""
import json, sqlite3, re, unicodedata
ROOT = "/work"
d = json.load(open(f"{ROOT}/desk_data.json"))
con = sqlite3.connect(f"{ROOT}/ledger.sqlite")
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(jr|sr|ii|iii)\b\.?", "", s)
    return re.sub(r"[^a-z]", "", s)
NICK = {"D-backs": "ARI", "Diamondbacks": "ARI", "Athletics": "ATH", "Braves": "ATL", "Orioles": "BAL", "Red Sox": "BOS", "Cubs": "CHC",
        "White Sox": "CWS", "Reds": "CIN", "Guardians": "CLE", "Indians": "CLE", "Rockies": "COL", "Tigers": "DET", "Astros": "HOU", "Royals": "KC",
        "Angels": "LAA", "Dodgers": "LAD", "Marlins": "MIA", "Brewers": "MIL", "Twins": "MIN", "Mets": "NYM", "Yankees": "NYY", "Phillies": "PHI",
        "Pirates": "PIT", "Padres": "SD", "Mariners": "SEA", "Giants": "SF", "Cardinals": "STL", "Rays": "TB", "Rangers": "TEX", "Blue Jays": "TOR", "Nationals": "WSH"}
def club_of(desc):
    for nick, ab in sorted(NICK.items(), key=lambda x: -len(x[0])):
        if re.search(r"\b" + re.escape(nick) + r" signed", desc): return ab
    return None
# bonus tracker
BON = {}; yr = None
for ln in open(f"{ROOT}/intl_bonus_src.txt", encoding="utf-8"):
    ln = ln.strip()
    if not ln or ln.startswith("#"): continue
    if ln.startswith("@"): yr = int(ln[1:]); continue
    nm, club, k = ln.split("|")
    BON[(yr, NICK[club], norm(nm))] = float(k)
draft = {}
for r in con.execute("select year,round,pick_overall,person_id,bonus,school from draft_picks where person_id is not null and person_id!=''"):
    draft[str(r[3])] = r
sig = {}
for r in con.execute("select person_id,date,description,person_name from sweep_tx where type_desc='Signed as Free Agent' and person_id is not null order by date"):
    sig.setdefault(str(r[0]), r)
pool = [p for p in d["players"] if p[9] > 0 or str(p[1]) in d["pros"] or str(p[1]) in d.get("draft26", {}) or str(p[1]) in d.get("deb26", {})]
out = {}; nb = 0; miss = []
for p in pool:
    pid = str(p[1])
    if pid in draft:
        y, rd, pk, _, bonus, school = draft[pid]
        try: b = round(float(bonus) / 1000, 1) if bonus not in (None, "") else None
        except ValueError: b = None
        try: pk = int(pk)
        except (TypeError, ValueError): pk = None
        out[pid] = ["d", int(y), str(rd), pk, b, school or ""]
    elif pid in sig:
        _, dt, desc, feed_name = sig[pid]
        y = int(dt[:4]); club = club_of(desc)
        # the period opened Jan 15 from 2021 on (the 2020 class was pushed to Jan 2021); earlier classes opened Jul 2
        cls = y
        b = None
        m_ = re.search(r"free agent \S+ (.+?) to a minor", desc or "")
        for nm in (p[0], feed_name or "", m_.group(1) if m_ else ""):
            b = BON.get((cls, club, norm(nm)))
            if b: break
        # only a first pro contract at 16-19 is an amateur signing; older first-contract players are undrafted or released pros
        age_then = p[4] - (2026 - y)
        if age_then > 20 and not b: continue
        out[pid] = ["i", y, club, b]
        if b: nb += 1
        elif p[9] > 0: miss.append((p[9], p[0], club, y))
json.dump(out, open(f"{ROOT}/prospect_bio.json", "w"), separators=(",", ":"), ensure_ascii=False)
nd = sum(1 for v in out.values() if v[0] == "d"); ni = len(out) - nd
print(f"prospect bios: {len(out)} of {len(pool)} ({nd} drafted, {ni} international, {nb} with a bonus)")
print("ranked internationals without a listed bonus:", sorted(miss))
