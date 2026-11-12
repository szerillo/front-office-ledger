# Round 48 plant for published figures: same-name rows must resolve by the team heading they sit under.
# Usage: python3 plant_heading.py <published_service.json>; exit 1 if any plant fails.
import sys, json
P = json.load(open(sys.argv[1]))
has = lambda pid, y: any(a == y for a, _, _ in (P.get(str(pid)) or {}).get('all', []))
plants = {
  'garcia_jr_nationals_2026': has(671277, 2026),     # Luis Garcia Jr., Nationals heading
  'garcia_astros_2026': has(677651, 2026),           # Luis Garcia, Astros heading (same normalized name)
  'carter_astros_2015': has(474892, 2015),           # Chris Carter, Astros heading
}
print(json.dumps(plants)); sys.exit(0 if all(plants.values()) else 1)
