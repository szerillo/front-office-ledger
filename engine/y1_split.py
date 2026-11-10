"""Nov 10 night: is the quarter-win under-projection of solid regulars real? Same walk-forward as y1_bt.py,
split into two periods and into odd and even years, with standard errors."""
import math
from collections import defaultdict
exec(open("/work/y1_bt.py").read().split('if __name__ == "__main__":')[0])
R = []
for T in range(2016, 2027):
    for pid in list(PT):
        r = proj(pid, T)
        if not r: continue
        rl, age, val, rate, pte, recent = r
        if rl == "RP" or val < 1.0: continue
        act = WAR.get(pid, {}).get(T, 0.0) * (162 / 60 if T == 2020 else 1)
        R.append((T, rl, val, act, age))
def show(name, rows):
    n = len(rows)
    if n < 20: return f"{name}: n{n}"
    d = [a - v for _, _, v, a, _ in rows]; m = sum(d) / n; sd = math.sqrt(sum((x - m) ** 2 for x in d) / (n - 1))
    return f"{name}: n{n} actual minus projected {m:+.2f} (se {sd / math.sqrt(n):.2f})"
for rl in ("bat", "SP"):
    for lo, hi in ((1, 2), (2, 3), (3, 4), (4, 5), (5, 99), (2.5, 4.25)):
        rows = [r for r in R if r[1] == rl and lo <= r[2] < hi]
        print(rl, f"proj {lo}-{hi}", "|", show("all", rows), "|", show("2016-20", [r for r in rows if r[0] <= 2020]), "|", show("2021-26", [r for r in rows if r[0] >= 2021]), "|", show("odd", [r for r in rows if r[0] % 2]), "|", show("even", [r for r in rows if not r[0] % 2]))
    rows = [r for r in R if r[1] == rl and 2.5 <= r[2] < 4.25]
    for a0, a1 in ((20, 26), (27, 30), (31, 45)): print("   ", rl, "proj 2.5-4.25 ages", a0, a1, show("", [r for r in rows if a0 <= r[4] <= a1]))
print()
rows = [r for r in R if r[1] == "bat" and 2.5 <= r[2] < 4.25 and r[4] <= 30]
print(show("bat 2.5-4.25, 30 and under, 2016-20", [r for r in rows if r[0] <= 2020]), "|", show("2021-26", [r for r in rows if r[0] >= 2021]))
for T0, T1 in ((2016, 2018), (2019, 2021), (2022, 2024), (2025, 2026)): print("  ", T0, T1, show("", [r for r in rows if T0 <= r[0] <= T1]))
allb = [r for r in R if r[1] == "bat"]
for T0, T1 in ((2016, 2020), (2021, 2026)): print("all bats proj 1+", T0, T1, show("", [r for r in allb if T0 <= r[0] <= T1]))
print()
# does the gap last into year two? the page's walk: add the aging step, then the attrition factor from year two on
cur = CURVE["bat"]; rows2 = []
for T in range(2016, 2026):
    for pid in list(PT):
        r = proj(pid, T)
        if not r or r[0] != "bat": continue
        rl, age, val, rate, pte, recent = r
        if not (2.5 <= val < 4.25) or age > 30: continue
        a2 = age + 1; surv = 0.97 if a2 <= 26 else 0.94 if a2 <= 29 else 0.89 if a2 <= 32 else 0.84
        y2 = max(val + cur.get(str(min(max(a2, 20), 41)), -0.3), 0) * surv
        act1 = WAR.get(pid, {}).get(T, 0.0) * (162 / 60 if T == 2020 else 1); act2 = WAR.get(pid, {}).get(T + 1, 0.0) * (162 / 60 if T + 1 == 2020 else 1)
        rows2.append((T, rl, y2, act2, age, val, act1))
r2 = [(t, rl, y2, a2, ag) for t, rl, y2, a2, ag, v, a1 in rows2]
print(show("year two, same hitters", r2), "| year one in the same sample:", show("", [(t, rl, v, a1, ag) for t, rl, y2, a2, ag, v, a1 in rows2]))
print("  ", show("year two 2016-20", [r for r in r2 if r[0] <= 2020]), "|", show("2021-25", [r for r in r2 if r[0] >= 2021]))
