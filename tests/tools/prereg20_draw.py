"""Draw for docs/prereg-round20.md. Run only after that file, this script and prereg20_frame.json are committed.
Usage: python3 tests/tools/prereg20_draw.py tests/tools/prereg20_frame.json"""
import json, random, sys
rows = json.load(open(sys.argv[1]))["rows"]
key = lambda r: (r["date"], r["pid"], r["club"])
fa97 = sorted([r for r in rows if r["src"] == "fa97"], key=key)
espn = sorted([r for r in rows if r["src"] == "espn"], key=key)
rng = random.Random(20261134)
for stratum, pool, n in (("fa97", fa97, 20), ("espn", espn, 5)):
    for r in rng.sample(pool, n):
        print(stratum, json.dumps(r, ensure_ascii=False))
