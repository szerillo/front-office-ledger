# Backtest of the projection walk's shape for star players: does the model age them too fast?
# For every player-season since 1990 whose year-one projection is a star's, walk six seasons forward with the
# page's own rule (weighted 5/3/2 base, aging step, attrition) and set it against what those players produced.
import json, sys
from collections import defaultdict
LVM = {int(k): v for k, v in json.load(open("/work/lvm_cache.json")).items() if not k.startswith("__")}
AGES = json.load(open("/work/ages.json")); POS = json.load(open("/work/positions.json"))
D = json.load(open("/work/desk_data.json")); CUR = D["curves"]; POP = CUR["pop"]
PIT = {"P", "SP", "RP", "RHP", "LHP", "TWP"}
BY = {pid: defaultdict(float) for pid in LVM}
for pid, v in LVM.items():
    for y, _, w in v["rows"]: BY[pid][y] += w * (162 / 60 if y == 2020 else 1)
def surv_step(age, pit, tbl):
    lo = tbl[0] if age <= 26 else tbl[1] if age <= 29 else tbl[2] if age <= 32 else tbl[3] if age <= 35 else tbl[4]
    return max(0.5, lo - (0.06 if pit else 0))
def walk(base, age0, pit, tbl=(0.97, 0.94, 0.89, 0.84, 0.78), n=6, star=None):
    curve = CUR["pit" if pit else "bat"]; val = base; surv = 1; out = []
    for i in range(1, n + 1):
        age = age0 + i
        val += curve.get(str(min(max(age, 20), 41)), -0.3)
        if i >= 2:
            s = surv_step(age, pit, tbl)
            if star: s = star(s, base, age, pit)
            surv *= s
        out.append(max(val, 0) * surv)
    return out
def cohort(star=None, lo=4.0, hi=99, y0=1990, y1=2019):
    rows = []
    for pid, by in BY.items():
        b = AGES.get(str(pid))
        if not b: continue
        pit = POS.get(str(pid)) in PIT
        for Y in range(y0, y1 + 1):
            obs = [(by.get(Y, 0), 5), (by.get(Y - 1, 0), 3), (by.get(Y - 2, 0), 2)]
            obs = [(v, w) for v, w in obs if abs(v) > 0.05]
            if not obs or abs(by.get(Y, 0)) <= 0.05: continue
            base = 0.85 * sum(v * w for v, w in obs) / sum(w for _, w in obs) + 0.15 * POP
            age0 = Y - b
            pred = walk(base, age0, pit, star=star)
            if not (lo <= pred[0] < hi): continue
            act = [by.get(Y + k, 0) for k in range(1, 7)]
            rows.append((pid, Y, age0 + 1, pit, pred, act))
    return rows
def report(rows, title):
    print("\n" + title)
    print(f"{'group':22s} {'n':>4s} | pred y1..y6 / total | actual y1..y6 / total | pred/actual total, y4-6")
    for pit in (False, True):
        for lbl, a, b in (("23-26", 0, 26), ("27-29", 27, 29), ("30-32", 30, 32), ("33-36", 33, 36)):
            g = [r for r in rows if r[3] == pit and a <= r[2] <= b]
            if len(g) < 15: continue
            P = [sum(r[4][k] for r in g) / len(g) for k in range(6)]; A = [sum(r[5][k] for r in g) / len(g) for k in range(6)]
            print(f"{('pit ' if pit else 'bat ') + lbl:22s} {len(g):4d} | " + " ".join(f"{x:4.1f}" for x in P) + f" /{sum(P):5.1f} | " + " ".join(f"{x:4.1f}" for x in A) + f" /{sum(A):5.1f} | {sum(P)/sum(A):.2f}  {sum(P[3:])/max(sum(A[3:]),0.01):.2f}")
if __name__ == "__main__":
    rows = cohort(); report(rows, "STARS (year-one projection 4.0+), current rule")
    rows2 = cohort(lo=2.0, hi=4.0); report(rows2, "REGULARS (2.0 to 4.0), current rule")
    rows3 = cohort(lo=5.5); report(rows3, "SUPERSTARS (5.5+), current rule")
