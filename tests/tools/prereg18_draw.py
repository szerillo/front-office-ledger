"""Draw for docs/prereg-round18.md. Run only after that file is committed.
Usage: python3 tests/tools/prereg18_draw.py /tmp/sweep/allfa.json"""
import json, random, sys
rows = sorted(tuple(r[:4]) + (r[5], r[6], r[7]) for r in json.load(open(sys.argv[1]))['A'])
for r in random.Random(20261132).sample(rows, 25): print(r)
