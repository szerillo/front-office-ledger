"""v5.9 (chain step, before the scorers): calibrate the expected value of a
prospect received in a trade. Every prospect (no MLB season before the deal)
received in a 2011-2018 trade: realized discounted window value (the same
trade_window, open part off) against the rank curve at the time of the deal
(ranked) or per piece (unranked), and the share realized N seasons after the
deal's first season. Writes trade_calib.json."""
import json, sys
from collections import defaultdict
sys.path.insert(0, "/work")
import asset_rules as A
cfg = json.load(open("/work/regimes.json"))
AB2N = {r["abbr"]: set(cfg["aliases"].get(str(r["teamId"]), [])) | {r["team"]} for r in cfg["regimes"]}
TB = json.load(open("/work/trade_book.json"))
seen = set(); rk_v = rk_r = 0.0; n_r = 0; un_r = 0.0; n_u = 0
cum = defaultdict(float); tot = 0.0
for d, seats in TB["trades"]:
    if not ("2011-01-01" <= d <= "2018-12-31"): continue
    for s in seats:
        ab = s[0]
        if ab not in AB2N: continue
        for pid, _ in s[2]:
            if (pid, d) in seen or not A.is_prospect(pid, d): continue
            seen.add((pid, d))
            t, ser = A.trade_window(pid, AB2N[ab], d, open_exp=False)
            y0 = int(d[:4]) + (1 if int(d[5:7]) >= 10 else 0)
            rk = A.rank_at(pid, d)
            if rk: rk_v += A.vrank(rk); rk_r += t; n_r += 1
            else: un_r += t; n_u += 1
            for y, v in ser.items(): cum[y - y0] += v
            tot += t
k_ranked = rk_r / rk_v if rk_v else 0.6
unranked = un_r / n_u if n_u else 0.1
run = 0.0; m = {}
for i in range(0, 13):
    run += cum.get(i, 0.0); m[str(i)] = round(min(1.0, max(0.0, run / tot)), 3) if tot else 0
# monotone
last = 0
for i in range(0, 13):
    m[str(i)] = max(last, m[str(i)]); last = m[str(i)]
out = dict(k_ranked=round(k_ranked, 3), unranked=round(unranked, 3), m=m, n_ranked=n_r, n_unranked=n_u)
json.dump(out, open("/work/trade_calib.json", "w"))
print(out)
