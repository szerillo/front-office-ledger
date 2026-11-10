"""Advanced 2026 rates from the BARTOLO tracker (Nov 10 2026): xFIP and SIERA for pitchers,
xwOBA for hitters. The tracker's JSON is read in the browser (it is not reachable from the build
box); the compact dumps live in adv26_pit.txt ("mlbam,xfip,siera,kbb;...") and adv26_hit.txt
("namehash,xwoba*1000,woba*1000;..." where namehash is FNV-1a of the letters-only lowercase name,
mod 1e8). Writes adv26.json {pid: [xfip, siera]} / {pid: [xwoba]}; desk_data.py ships it as DESK.adv26."""
import json, re, unicodedata
R = "/work/"
def nk(s):
    s = unicodedata.normalize("NFKD", s); s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\b(jr|sr|ii|iii)\b\.?", "", s); return re.sub(r"[^a-z]", "", s)
def fnv(s):
    h = 2166136261
    for ch in s:
        h ^= ord(ch); h = (h * 16777619) & 0xFFFFFFFF
    return h % 100000000
d = json.load(open(R + "desk_data.json"))
pit = {}
for rec in open(R + "adv26_pit.txt").read().strip().split(";"):
    a = rec.split(",")
    if len(a) == 4 and a[0].isdigit(): pit[int(a[0])] = (a[1], a[2])
hit = {}
for rec in open(R + "adv26_hit.txt").read().strip().split(";"):
    a = rec.split(",")
    if len(a) == 3: hit.setdefault(int(a[0]), []).append(int(a[1]))
out = {}; seen = {}
for p in d["players"]:
    pid = p[1]
    if p[3]:
        if pid in pit:
            x, s = pit[pid]; out[str(pid)] = ["p", float(x) if x else None, float(s) if s else None]
    else:
        h = fnv(nk(p[0])); seen.setdefault(h, []).append(pid)
for h, pids in seen.items():
    # a name shared by two pool players, or by two tracker rows, is left out rather than guessed
    if len(pids) == 1 and h in hit and len(hit[h]) == 1 and str(pids[0]) in d.get("line26", {}):
        out[str(pids[0])] = ["h", hit[h][0]]
json.dump(out, open(R + "adv26.json", "w"), separators=(",", ":"))
print(f"advanced 2026 rates: {sum(1 for v in out.values() if v[0]=='p')} pitchers of {len(pit)}, {sum(1 for v in out.values() if v[0]=='h')} hitters of {len(hit)}")
