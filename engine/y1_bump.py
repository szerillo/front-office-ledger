"""Nov 10 night: the prime-age regular adjustment, checked on the same walk-forward. Hitters 30 and under get a
quarter win across a year-one projection of 2.75 to 4.0, fading to nothing at 2.0 and 4.75."""
import math
exec(open("/work/y1_bt.py").read().split('if __name__ == "__main__":')[0])
def bump(val, age, rl, B=0.25): return val + (B * max(0.0, min(1.0, (val - 2.0) / 0.75, (4.75 - val) / 0.75)) if rl == "bat" and age <= 30 else 0.0)
R = []
for T in range(2016, 2027):
    for pid in list(PT):
        r = proj(pid, T)
        if not r or r[0] != "bat": continue
        rl, age, val, rate, pte, recent = r
        act = WAR.get(pid, {}).get(T, 0.0) * (162 / 60 if T == 2020 else 1)
        R.append((T, age, val, bump(val, age, rl), act))
def line(name, rows, k):
    n = len(rows); d = [r[4] - r[k] for r in rows]; m = sum(d) / n; sd = math.sqrt(sum((x - m) ** 2 for x in d) / (n - 1)); mae = sum(abs(x) for x in d) / n
    return f"{name}: n{n} actual minus projected {m:+.2f} (se {sd / math.sqrt(n):.2f}) mean miss {mae:.2f}"
for lo, hi in ((1, 2), (2, 3), (3, 4), (4, 5), (5, 99)):
    print(f"proj {lo}-{hi} before |", line("", [r for r in R if lo <= r[2] < hi], 2)); print(f"proj {lo}-{hi} after  |", line("", [r for r in R if lo <= r[3] < hi], 3))
sub = [r for r in R if r[1] <= 30 and 2.0 < r[2] < 4.75]
print(line("touched hitters, before", sub, 2)); print(line("touched hitters, after ", sub, 3)); print("  2016-20 after:", line("", [r for r in sub if r[0] <= 2020], 3), "| 2021-26 after:", line("", [r for r in sub if r[0] >= 2021], 3))
allr = [r for r in R if r[2] >= 1]; print(line("all hitters projected 1+, before", allr, 2)); print(line("all hitters projected 1+, after ", allr, 3))
