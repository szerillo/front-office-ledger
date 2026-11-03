"""Statcast Fielding Run Value ingest (Baseball Savant, native MLBAM ids).

Per season 2015-2026, one all-positions request (season total + outs at
each position) and one request per position 2..9 (runs AT that position,
which is what the Ledger WAR defense rule needs for players who split time
between the infield, where DRS is used, and C/OF, where FRV is used).

Catcher FRV (catching_runs) = framing + throwing + blocking where Savant
publishes each piece. Coverage by year is recorded in __coverage__ so the
WAR build can fill a missing framing piece from the Savant framing
leaderboard (savant_runs.json "frame", 2015+) without double counting.

Output: frv_runs.json
  {pid: {year: {"tot": all-pos FRV, "pos": {"2": r, ..., "9": r},
                "outs": {"2": n, ...}, "c": {"frame": r, "throw": r, "block": r}}}}
"""
import csv, io, json, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
URL = ("https://baseballsavant.mlb.com/leaderboard/fielding-run-value?gameType=Regular"
       "&seasonStart={y}&seasonEnd={y}&type=fielder&position={p}&minInnings=0&minResults=1&csv=true")

def get_csv(url, tries=3):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            d = urllib.request.urlopen(req, timeout=60).read().decode("utf-8-sig", "ignore")
            return list(csv.DictReader(io.StringIO(d)))
        except Exception as e:
            print("  retry", a, e, flush=True)
            time.sleep(3 + 3 * a)
    return []

def f(x):
    try: return float(x)
    except (TypeError, ValueError): return None

OUT, COV = {}, {}
for yr in range(2015, 2027):
    ys = str(yr)
    rows = get_csv(URL.format(y=yr, p=""))
    n_tot = 0
    for r in rows:
        pid = r.get("id")
        if not pid: continue
        rec = OUT.setdefault(str(int(float(pid))), {}).setdefault(ys, {"pos": {}, "outs": {}})
        t = f(r.get("total_runs"))
        if t is not None: rec["tot"] = t; n_tot += 1
        for p in range(2, 10):
            o = f(r.get(f"outs_{p}"))
            if o: rec["outs"][str(p)] = o
    time.sleep(1.0)
    cov = {"all_rows": len(rows), "all_with_runs": n_tot}
    for p in range(2, 10):
        prow = get_csv(URL.format(y=yr, p=p))
        n = 0
        for r in prow:
            pid = r.get("id"); t = f(r.get("total_runs"))
            if not pid or t is None: continue
            rec = OUT.setdefault(str(int(float(pid))), {}).setdefault(ys, {"pos": {}, "outs": {}})
            rec["pos"][str(p)] = t; n += 1
            if p == 2:
                c = {}
                for k, src in (("frame", "framing_runs"), ("throw", "throwing_runs"), ("block", "blocking_runs")):
                    v = f(r.get(src))
                    if v is not None: c[k] = v
                rec["c"] = c
        cov[f"p{p}"] = n
        if p == 2:
            cov["c_frame"] = sum(1 for r in prow if f(r.get("framing_runs")) is not None)
            cov["c_throw"] = sum(1 for r in prow if f(r.get("throwing_runs")) is not None)
            cov["c_block"] = sum(1 for r in prow if f(r.get("blocking_runs")) is not None)
        time.sleep(1.0)
    COV[ys] = cov
    print(yr, cov, flush=True)

OUT["__coverage__"] = COV
json.dump(OUT, open("/work/frv_runs.json", "w"))
print(f"saved frv_runs.json: {len(OUT)-1} players, "
      f"{sum(len(v) for k, v in OUT.items() if not k.startswith('__'))} player-seasons")
