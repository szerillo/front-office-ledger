import json, sys, re
d = json.load(open(sys.argv[1])); bad = {k: v for k, v in d['calls'].items() if re.search(r'=> "(A\+|A−|A|B\+|B|C\+|C|D\+|D|F|g[0-9]+)"$', k)}
print(sys.argv[1], 'null calls', sum(d['calls'].values()), '| printed a letter or a colour grade:', sum(bad.values()), '| errors', len(d['errors']))
for k, v in sorted(bad.items(), key=lambda x: -x[1])[:12]: print('  ', v, k[:150])
