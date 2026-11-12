# Every number and named change in the correction note, recomputed from the live build and the candidate.
# Red (exit 5) on any mismatch, and when an overall grade changes that the table does not list.
# Usage: note_check.py <note.md>   (inputs: page dumps from dump.mjs, t_grades dumps per stage, letters censuses,
#        offseasons.json of both builds; paths below)
import json, re, sys, subprocess
from collections import Counter
note = open(sys.argv[1], encoding='utf-8').read(); bad, ok = [], []
def check(name, cond, detail=''):
    (ok if cond else bad).append(f'{name}{": " + detail if detail else ""}')
D = '/tmp/deploy'; LIVE = '/home/claude/fol-main'; CAND = D + '/good7'
g2l = lambda g: '·' if g is None else 'A+' if g >= 80 else 'A' if g >= 70 else 'A−' if g >= 65 else 'B+' if g >= 60 else 'B' if g >= 55 else 'C+' if g >= 50 else 'C' if g >= 45 else 'D+' if g >= 40 else 'D' if g >= 35 else 'F'
L = {x['id']: x for x in json.load(open('/tmp/note/cur_live.json'))}; C = {x['id']: x for x in json.load(open('/tmp/note/cur_g7.json'))}
# 1. overall grade table: every row right, and no overall change left out
rows = re.findall(r'^\| ([A-Z]{2,3}) \| (\S+) to (\S+) \|', note, re.M)
actual = {k.upper(): (g2l(L[k]['forGrade']), g2l(C[k]['forGrade'])) for k in C if k in L and L[k]['forGrade'] != C[k]['forGrade']}
for ab, was, now in rows: check(f'table {ab} {was} to {now}', actual.get(ab) == (was, now), f'build says {actual.get(ab)}')
check('table lists every overall change', set(actual) == {r[0] for r in rows}, f'changed {sorted(actual)}')
# 2. counts moved by the two rules (t_grades population, attributed by stage builds)
out = subprocess.run(['python3', D + '/stage_attr.py'], capture_output=True, text=True).stdout
cnt = {m.group(1) + '|' + m.group(2): int(m.group(3)) for m in re.finditer(r"\('(trade|card)', '([^']+)'\) (\d+)", out)}
rule_trade = cnt.get('trade|re-sign', 0) + cnt.get('trade|2020 fix', 0) + cnt.get('trade|2020 fix+re-sign', 0)
rule_card = cnt.get('card|re-sign', 0) + cnt.get('card|2020 fix', 0) + cnt.get('card|2020 fix+re-sign', 0)
m = re.search(r'moved (\d+) trade entries, (\d+) signing and extension entries and (\d+) grades', note)
check('note has the rule-count sentence', bool(m))
if m:
    check('trade entries', int(m.group(1)) == rule_trade, f'build {rule_trade}')
    check('signing/extension entries', int(m.group(2)) == rule_card, f'build {rule_card}')
    cause = json.load(open(D + '/grade_changes_by_cause.json'))
    Lg, Cg = json.load(open(D + '/L_live.json')), json.load(open(D + '/L_g7.json'))
    diff = {k for k in Lg if k in Cg and Lg[k] != Cg[k]}
    allc = set().union(*[set(x if isinstance(x, str) else x[0] for x in v) for v in cause.values()])
    check('grade causes cover exactly the census diff', allc == diff, f'diff {len(diff)} causes {len(allc)}')
    check('grades moved by the two rules', int(m.group(3)) == len(cause['2020']) + len(cause['resign+page fix']), f"build {len(cause['2020']) + len(cause['resign+page fix'])}")
# 3. Bello: Seattle's international count falls by one
check('Bello to TOR (SEA intl -1)', C['sea']['chan']['intl']['n'] - L['sea']['chan']['intl']['n'] == -1)
# 4. winters: tier changes, named ones, best on record
WORDS = {'Eighteen': 18, 'Seventeen': 17, 'Nineteen': 19, 'Twenty': 20}
ol, oc = json.load(open(LIVE + '/offseasons.json'))['rows'], json.load(open(CAND + '/offseasons.json'))['rows']
st = subprocess.run(['python3', D + '/offs_stamps.py', LIVE + '/offseasons.json', CAND + '/offseasons.json'], capture_output=True, text=True).stdout
n_t = int(re.search(r'tier labels changed: (\d+)', st).group(1))
m = re.search(r'(\w+) winters change tier', note); check('tier count', bool(m) and WORDS.get(m.group(1)) == n_t, f'build {n_t}')
for ab in re.findall(r'among them (\w+) and (\w+) 2019', note)[0] if re.search(r'among them (\w+) and (\w+) 2019', note) else []:
    check(f'{ab} 2019 Catastrophe to Disaster', f'{ab} 2019' in st and re.search(ab + r' 2019 [^\n]*Catastrophe -> Disaster', st) is not None)
best = sorted([r for r in oc if r[9] is not None], key=lambda r: -r[9])[:2]
m = re.search(r"Washington's 2014-15 winter \(\+([\d.]+)\) now edges Oakland's 2011-12 \(\+([\d.]+)\) as the best on record", note)
if m:   # optional: round 37 dropped this sentence (the new #1 rests on a pre-season release credit, see wsh-trace.md)
    check('#1 is WSH 2014', (best[0][0], best[0][1]) == ('WSH', 2014) and abs(best[0][9] - float(m.group(1))) < 0.05, str(best[0][:2] + [best[0][9]]))
    check('#2 is OAK/ATH 2011', best[1][1] == 2011 and best[1][0] in ('ATH', 'OAK') and abs(best[1][9] - float(m.group(2))) < 0.05, str(best[1][:2] + [best[1][9]]))
    bl = sorted([r for r in ol if r[9] is not None], key=lambda r: -r[9])[0]; check('live #1 was OAK/ATH 2011', bl[1] == 2011)
# 5. headlines: some winter headline names a different player for the same move value
hl = 0
for a in ol:
    b = next((x for x in oc if x[0] == a[0] and x[1] == a[1]), None)
    if not b: continue
    A = {(mv[0], mv[1], mv[3]): mv[2] for mv in a[12] or []}
    hl += sum(1 for mv in b[12] or [] if (mv[0], mv[1], mv[3]) in A and A[(mv[0], mv[1], mv[3])] != mv[2])
check('some headlines name a different player', ('Some trade headlines' in note) == (hl > 0), f'{hl} found')
print('note check:', len(ok), 'ok,', len(bad), 'wrong')
for x in bad: print('  WRONG', x)
if bad: sys.exit(5)
print('NOTE CHECK GREEN')
