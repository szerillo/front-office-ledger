"""Known issue check: seasons past the engine's control end with no contract on
file are charged $0 in trades (Nov 11 audit, section 7). Each case below had a
real salary (arbitration award or club option). This check fails until the
control end comes from service time and options are in the contract book.

Run: python3 tests/t_known_salary.py [engine dir, default /work]
Exit 0 always unless STRICT=1, so the known issue is reported, not hidden, and
does not block the other suites. Flip STRICT=1 once the fix lands."""
import os, sys
ENG = sys.argv[1] if len(sys.argv) > 1 else '/work'
sys.path.insert(0, ENG)
import asset_rules as AR

# (name, MLBAM id, season, club that acquired him, real salary $M, source of the salary)
CASES = [
    ('Brandon Lowe', 664040, 2026, 'PIT', 11.5, 'club option'),
    ('Kyle Tucker', 663656, 2025, 'CHC', 16.5, 'arbitration'),
    ('Trea Turner', 607208, 2022, 'LAD', 21.0, 'arbitration'),
    ('Chris Sale', 519242, 2018, 'BOS', 12.5, 'club option'),
    ('Chris Sale', 519242, 2019, 'BOS', 15.0, 'club option'),
]

res = {}
for name, pid, y, club, sal, src in CASES:
    cost = AR.contract_cost(pid, y, played=True)
    res[f'{name} {y}'] = cost > 0
    print(f"{'ok  ' if cost > 0 else 'KNOWN'} {name} {y} ({club}, {src} ${sal}M): charged {cost:.2f} wins, control end {AR.control_end(pid)}")

bad = [k for k, v in res.items() if not v]
print('PASS' if not bad else 'KNOWN ISSUE: ' + ', '.join(bad))
sys.exit(1 if (bad and os.environ.get('STRICT') == '1') else 0)
