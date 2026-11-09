import statistics as st
exec(open("/work/pos_bt.py").read().split("K = 1800.0")[0])
W = (5, 3, 2)
def pr(pid, T, K, agemult=1.0):
    num = den = 0.0
    for y, w in zip((T-1, T-2, T-3), W):
        pt = ptv(pid, y, "bat")
        if y not in PT[pid] and y < min(PT[pid]): continue
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    rate = (num + K * POP[T-1]["bat"]) / (den + K); pe = ptv(pid, T, "bat"); p = rate * pe
    if pid in AGES: p += CUR["bat"].get(str(min(max(T - AGES[pid], 20), 41)), -0.3) * agemult * (pe / CAP["bat"])
    return p, den, num / den if den else 0
cells = {}
for T in range(2016, 2027):
    for pid, rl in rows(T):
        if rl != "bat" or pid not in AGES: continue
        y = WAR.get(pid, {}).get(T, 0.0); a = T - AGES[pid]
        p, den, raw = pr(pid, T, 1800); 
        if ptv(pid, T, "bat") < 450: continue
        ab = "<=24" if a <= 24 else "25-27" if a <= 27 else "28-30" if a <= 30 else "31+"
        hb = "hist<2500" if den < 2500 else "hist>=2500"
        # prior level: raw rate per 600
        lb = "low" if raw * 600 < 1.5 else "mid" if raw * 600 < 3.5 else "high"
        cells.setdefault((ab, hb), []).append(p - y); cells.setdefault((ab, "lvl " + lb), []).append(p - y)
for k in sorted(cells): v = cells[k]; print("%-6s %-11s n %4d bias %+.3f rmse %.3f" % (k[0], k[1], len(v), st.mean(v), st.mean(x*x for x in v) ** 0.5))
print("--- K sweep for young regulars (<=25, 450+ PA in T, weighted hist >= 2500)")
for K in (600, 1000, 1400, 1800, 2400):
    e = []
    for T in range(2016, 2027):
        for pid, rl in rows(T):
            if rl != "bat" or pid not in AGES or T - AGES[pid] > 25 or ptv(pid, T, "bat") < 450: continue
            p, den, raw = pr(pid, T, K)
            if den < 2500: continue
            e.append(p - WAR.get(pid, {}).get(T, 0.0))
    print("K", K, "n", len(e), "bias %+.3f rmse %.3f" % (st.mean(e), st.mean(x*x for x in e) ** 0.5))
