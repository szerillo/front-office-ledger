# Round 46: add the club each report is about (rows[5]) and the date it was last confirmed (rows[6]); all else kept.
import json, sys
R = json.load(open(sys.argv[1])); D = json.load(open('/tmp/r46/pub/desk.json'))
club = {p[1]: p[2] for p in D['players']}
day = R['checked'][:10]
for r in R['rows']:
    while len(r) < 5: r.append(0)
    if len(r) < 7:
        r[5:7] = [club[r[0]], day]
R['_about'] = R['_about'].replace('1 if a long shot].', '1 if a long shot (0 if not), club abbreviation the report is about, date the report was last confirmed on file (YYYY-MM-DD)]. The page drops a report if the player is now with another club or moved after that date.')
assert 'club abbreviation' in R['_about']
json.dump(R, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)
print('rows', len(R['rows']), R['rows'][0])
