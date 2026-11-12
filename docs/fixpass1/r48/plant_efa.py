# Round 48 plant for the service counter: "elected free agency" (feed code DFA) must take an active player off;
# a plain designation for assignment must keep him on (limbo accrues service).
# Usage: python3 plant_efa.py <path to svc_fetch.py>; exit 1 if any plant fails.
import sys, json
src = open(sys.argv[1]).read(); i = src.find('MLB = '); j = src.find('def team_id'); k = src.find('def classify'); e = src.find('\n    return on\n', k) + len('\n    return on\n')
ns = {'MINORS': set()}
exec(src[i:src.find('}', i) + 1], ns); exec(src[j:k] + src[k:e], ns); classify = ns['classify']
T = lambda code, date, to, desc: {'typeCode': code, 'date': date, 'toTeam': {'id': to}, 'description': desc}
plants = {
  'elected_fa_takes_off': classify(T('DFA', '2016-11-03', None, 'RHP Jordan Walden elected free agency.'), True) is False,
  'dfa_limbo_stays_on': classify(T('DFA', '2016-06-01', 138, 'St. Louis Cardinals designated RHP somebody for assignment.'), True) is True,
}
print(json.dumps(plants)); sys.exit(0 if all(plants.values()) else 1)
