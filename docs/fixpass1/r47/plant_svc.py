# Round 47 plants for the service counter: a Rule 5 draft (DR) and a contract purchase (PUR) by a major league club
# must put an off-roster player on; the same codes to a minor league club, or a DR outside December, must not.
# Usage: python3 plant_svc.py <path to svc_fetch.py>; exit 1 if any plant fails.
import sys, types, importlib.util, json, os
src = open(sys.argv[1]).read(); i = src.find('MLB = '); j = src.find('def team_id'); k = src.find('def classify'); e = src.find('\n    return on\n', k) + len('\n    return on\n')
ns = {}
exec(src[i:src.find('}', i) + 1], ns)                                  # the MLB club id set, as the engine defines it
ns['MINORS'] = set(json.load(open(os.environ.get('MINORS', '/tmp/r44/eng/data/minors_ids.json'))))
exec(src[j:k] + src[k:e], ns); classify = ns['classify']
T = lambda code, date, to, desc: {'typeCode': code, 'date': date, 'toTeam': {'id': to}, 'description': desc}
plants = {
  'rule5_draft_puts_on': classify(T('DR', '2014-12-11', 143, 'Philadelphia Phillies drafted CF Odubel Herrera.'), False) is True,
  'purchase_puts_on': classify(T('PUR', '2010-08-22', 108, 'Los Angeles Angels purchased RHP Jordan Walden from Salt Lake Bees.'), False) is True,
  'june_draft_stays_off': classify(T('DR', '2019-06-03', 143, 'Philadelphia Phillies drafted SS somebody.'), False) is False,
  'purchase_by_minor_club_stays_off': classify(T('PUR', '2010-08-22', 561, 'Salt Lake Bees purchased RHP somebody from an independent club.'), False) is False,
}
print(json.dumps(plants)); sys.exit(0 if all(plants.values()) else 1)
