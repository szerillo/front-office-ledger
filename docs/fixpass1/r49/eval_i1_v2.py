# Round 49: tracer fix only (names folded: Unicode NFKD, accents stripped, case folded). Not re-run on I1.
# Round 47: evaluate run I1 against Z_X6 exactly as pre-registered (docs/fixpass1/r47/prereg_published_control.md)
import json, re, sys, statistics, datetime
sys.path.insert(0, '/tmp/fix/f/engine')
import asset_rules as AR
B, I = '/tmp/sbx/runs/Z_X6/work/', '/tmp/sbx/runs/I1/work/'
PUB = {int(k): v['ctrl_end'] for k, v in json.load(open('/tmp/fix/i/engine/published_service.json')).items()}
L = json.load(open('/work/lvm_cache.json'))
CH = set(); NAMES = {}
for pid, end in PUB.items():
    rec = L.get(str(pid))
    if not isinstance(rec, dict): continue
    sp = AR.control_span(rec, pid)
    if sp and sp[1] != end: CH.add(pid); NAMES[pid] = rec.get('name')
print('CH (published players whose control end changes):', len(CH))
CHs = {str(p) for p in CH}
# 1 + 2: letters and overall grades
N = json.load(open('/tmp/r40/a/new.json')); Z = N['Z']; rows = N['rows']
def recs(p):
    out = {}
    for f in ('sweep_results.json', 'hist_results.json'):
        for r in json.load(open(p + f)): out[r['id']] = r
    return out
RB, RI = recs(B), recs(I)
def nets(R): return {(i, k): c['net'] for i, r in R.items() for k, c in (r.get('chan') or {}).items() if isinstance(c, dict) and c.get('net') is not None}
def letter(z):
    for cut, g in Z:
        if z >= cut: return g
    return Z[-1][1] - 5
def grade(n):
    sd = {k: statistics.pstdev([n[(r['id'], k)] / r['S'] for r in rows if r['k'] == k and (r['id'], k) in n]) for k in {r['k'] for r in rows}}
    return {(r['id'], r['k']): letter(n[(r['id'], r['k'])] / (sd[r['k']] * r['S'])) for r in rows if (r['id'], r['k']) in n}
gB, gI = grade(nets(RB)), grade(nets(RI))
lch = [k for k in gB if k in gI and gB[k] != gI[k]]
och = [i for i in RB if i in RI and RB[i].get('forGrade') != RI[i].get('forGrade')]
# tracing
TB = json.load(open(B + 'trade_book.json'))['trades']; TI = json.load(open(I + 'trade_book.json'))['trades']
def trade_ids(seats):
    s = set()
    for st in seats:
        for part in st[2:]:
            for x in part or []: s.add(str(x[0]))
    return s
def seat_window(r):
    a = r.get('startDate') or (str(r.get('start')) + '-10-01'); y = float(r.get('seatSeasons') or r.get('seasons') or 0)
    d0 = datetime.date.fromisoformat(a[:10]); return a[:10], (d0 + datetime.timedelta(days=int(365 * y) + 183)).isoformat()
import unicodedata
def fold(x): return ''.join(c for c in unicodedata.normalize('NFKD', x or '') if not unicodedata.combining(c)).lower()
def traced(fid, ch):
    r = RB.get(fid) or {}
    blob = ''
    if ch == 'fa': blob = json.dumps(r.get('allx_fa'))
    elif ch == 'intl': blob = json.dumps(r.get('allx_intl'))
    elif ch == 'ext':
        txt = fold(json.dumps(r.get('allx_ext'), ensure_ascii=False))
        return any(NAMES[p] and fold(NAMES[p]) in txt for p in CH)
    else: blob = json.dumps((r.get('allx') or {}).get(ch))
    if any(i in CHs for i in re.findall(r'"(\d{6})"', blob)): return True
    if ch == 'trade':
        a, b = seat_window(r); ab = r.get('abbr')
        for d, seats in TB:
            if a <= d <= b and any(st[0] == ab for st in seats) and trade_ids(seats) & CHs: return True
    return False
unl = [k for k in lch if not traced(*k)]
uno = [i for i in och if not any(traced(i, k) for k in ('trade', 'draft', 'fa', 'ext', 'intl', 'waiver', 'walk', 'ret', 'comp'))]
# 4: trade-side nets
def seatnets(T): 
    s = {}
    for d, seats in T:
        for st in seats: s[(d, st[0])] = (s.get((d, st[0]), (0, set()))[0] + st[1], trade_ids(seats))
    return s
sb, si = seatnets(TB), seatnets(TI)
tch = [k for k in sb if k in si and round(sb[k][0], 1) != round(si[k][0], 1)]
tun = [k for k in tch if not (sb[k][1] & CHs) and abs(si[k][0] - sb[k][0]) > 0.2]
# 3: winters and band
rowsW = lambda p: {(r[0], r[1]): r for r in json.load(open(p + 'offseasons.json'))['rows']}
wB, wI = rowsW(B), rowsW(I)
wch = [k for k in wB if k in wI and wB[k][9] != wI[k][9]]
wun = [k for k in wch if not any(str(x[-1]) in CHs for x in (wB[k][12] or []))]
def band(W):
    s = sorted(W, key=lambda k: W[k][9]); r = s.index(('TOR', 2012)) + 1
    return r, round(W[s[20]][9] - W[('TOR', 2012)][9], 2)
bB, bI = band(wB), band(wI)
untraced_pages = {k[0] for k in unl} | set(uno) | {f'{a}-{y}' for a, y in wun}
res = {'CH': len(CH), 'channel_letters_changed': len(lch), 'overall_grades_changed': len(och),
       'untraced_letters': len(unl), 'untraced_overall': len(uno), 'trade_nets_changed': len(tch), 'untraced_trade_nets_gt_0.2': len(tun),
       'winters_changed': len(wch), 'untraced_winters': len(wun), 'TOR_rank_margin_live': bB, 'TOR_rank_margin_I1': bI,
       'untraced_pages': len(untraced_pages)}
bar = {'letters<=150': len(lch) <= 150, 'overall<=40': len(och) <= 40, 'untraced_letters_or_overall<=5': len(unl) + len(uno) <= 5,
       'untraced_trade_nets<=50': len(tun) <= 50, 'band_kept': bI[0] <= 2 and bI[1] >= 0.9 * bB[1], 'untraced_pages<=50': len(untraced_pages) <= 50}
res['bar'] = bar; res['PASS'] = all(bar.values())
res['examples'] = {'untraced_letters': unl, 'untraced_overall': uno[:10], 'untraced_trade_nets': [list(k) for k in tun[:10]], 'untraced_winters': wun[:10]}
print(json.dumps(res, indent=1, default=str))
json.dump(res, open('/tmp/r47/eval/i1_result.json', 'w'), indent=1, default=str)
