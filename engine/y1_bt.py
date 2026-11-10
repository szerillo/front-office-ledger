"""Nov 10: is the year-one projection too low for stars? Walk-forward 2016-2026 with the page's own rule
(desk_data.py: rate x expected playing time, the 27+ playing-time steps, the aging step), every player who
appeared in T-1, target = Ledger WAR in T (zero if he did not play). Grouped by the projection itself and by
what the player had just done."""
import json, sys
from collections import defaultdict
exec(open("/work/proj_bt.py").read().split("def rows(T):")[0])      # PT, WAR, AGES, CUR, CAP, role, ptv, POP
D = json.load(open("/work/desk_data.json")); CURVE = D["curves"]
W = {1: 5, 2: 3, 3: 2}
def proj(pid, T, K=None, mid_w=0.15, cutlo=None):
    prev = [y for y in (T - 1, T - 2, T - 3) if y in PT[pid]]
    if (T - 1) not in PT[pid]: return None
    rl = role(pid, prev); Kd = {"bat": 1800.0, "SP": 900.0, "RP": 675.0}; Kr = (K or Kd)[rl]
    age = T - 1 - AGES.get(pid, T - 28)        # age in T-1, like p[4]
    num = den = ptw = ptd = 0.0; pts = []
    for k in (1, 2, 3):
        y = T - k
        if y not in PT[pid] and k > 1 and not any(yy in PT[pid] for yy in range(2013, y)): continue
        pt = ptv(pid, y, rl); w = W[k]; ptw += w * pt; ptd += w; pts.append(pt)
        if pt > 0: num += w * WAR.get(pid, {}).get(y, 0.0); den += w * pt
    if ptd == 0: return None
    pop = POP[T - 1].get(rl, 0.0)
    rate = (num + Kr * pop) / (den + Kr)
    top2 = sorted(pts, reverse=True)[:2]
    l = ptv(pid, T - 1, rl); p2 = max(ptv(pid, T - 2, rl), ptv(pid, T - 3, rl))
    inj = l < 0.5 * CAP[rl] and p2 >= 0.8 * CAP[rl]
    a = 0.6 if age <= 26 else 0.4 if inj else 0.2
    pt_exp = min(a * (sum(top2) / len(top2)) + (1 - a) * (ptw / ptd), CAP[rl])
    if age <= 26 and l >= 0.6 * CAP[rl]: pt_exp = min(max(pt_exp, 0.85 * l), CAP[rl])
    if age >= 26 and rl in ("bat", "SP"):
        mid = 350.0 if rl == "bat" else 0.5 * CAP[rl]; pe0 = pt_exp
        pt_exp = (1 - mid_w) * pt_exp + mid_w * mid
        full = rate * (600.0 if rl == "bat" else CAP[rl])
        m, c, lo, thr = (3.5, 0.12, 0.7, 300.0) if rl == "bat" else (3.0, 0.10, 0.75, 0.45 * CAP[rl])
        if pe0 >= thr: pt_exp *= max(lo, min(1.0, 1 + c * (full - m)))
        if l >= 0.75 * CAP[rl]: pt_exp = min(CAP[rl], max(pt_exp, (0.75 if rl == "bat" else 0.70) * l))
    cur = CURVE["pit" if rl != "bat" else "bat"]
    val = rate * pt_exp + cur.get(str(min(max(age + 1, 20), 41)), -0.3)
    recent = num / den * (600.0 if rl == "bat" else CAP[rl]) if den else 0     # what he had just done, per full season
    return rl, age + 1, max(val, 0), rate * (600.0 if rl == "bat" else 180.0), pt_exp, recent
def table(K=None, mid_w=0.15, title="current rule"):
    G = defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0])
    for T in range(2016, 2027):
        for pid in list(PT):
            r = proj(pid, T, K, mid_w)
            if not r: continue
            rl, age, val, rate, pte, recent = r
            act = WAR.get(pid, {}).get(T, 0.0) * (162 / 60 if T == 2020 else 1); apt = ptv(pid, T, rl) * (162 / 60 if T == 2020 else 1)
            kind = "bat" if rl == "bat" else rl
            tier = "proj 5+" if val >= 5 else "proj 4-5" if val >= 4 else "proj 3-4" if val >= 3 else "proj 2-3" if val >= 2 else None
            if tier:
                g = G[(kind, tier)]; g[0] += 1; g[1] += val; g[2] += act; g[3] += pte; g[4] += apt
            if rl != "RP" and recent >= (6.0 if rl == "bat" else 5.5) and ptv(pid, T - 1, rl) >= 0.7 * CAP[rl]:
                g = G[(kind, "just played like a star")]; g[0] += 1; g[1] += val; g[2] += act; g[3] += pte; g[4] += apt
    print("\n" + title)
    for k in sorted(G):
        n, v, a, pe, ap = G[k]
        if n >= 12: print(f"  {k[0]:4s} {k[1]:24s} n{n:4d}  projected {v/n:4.2f}  actual {a/n:4.2f}  bias {(v-a)/n:+.2f}   playing time projected {pe/n:5.0f}  actual {ap/n:5.0f}")
if __name__ == "__main__":
    table()
