# winter tier labels the page shows (offsStamp(r.tot), index.html: function offsStamp), live vs candidate offseasons.json
import json, sys
def stamp(v): return 'All-timer' if v >= 20 else 'Great winter' if v >= 10 else 'Good winter' if v >= 3 else 'A wash' if v > -3 else 'Bad winter' if v > -10 else 'Disaster' if v > -20 else 'Catastrophe'
a = {(r[0], r[1], r[3]): r for r in json.load(open(sys.argv[1]))['rows']}; b = {(r[0], r[1], r[3]): r for r in json.load(open(sys.argv[2]))['rows']}
ch = [(k, a[k][9], b[k][9], stamp(a[k][9]), stamp(b[k][9])) for k in a if k in b and a[k][9] is not None and b[k][9] is not None and stamp(a[k][9]) != stamp(b[k][9])]
print(f"winters {len(a)} vs {len(b)}; tier labels changed: {len(ch)}")
for c in sorted(ch, key=lambda c: -abs(c[2] - c[1])): print(' ', c[0][0], c[0][1], c[1], '->', c[2], c[3], '->', c[4])
sys.exit(1 if ch else 0)
