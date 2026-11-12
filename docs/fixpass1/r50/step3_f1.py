# Round 49 F1 evaluation, bars exactly as in prereg_calib_freeze.md (b2477dc). Letters use the live spread and cutoffs.
import sys, json, re, unicodedata, datetime; sys.path.insert(0, '/tmp/r49/eval'); from common import *
sys.path.insert(0, '/tmp/fix/f/engine'); import asset_rules as AR
RUNP = sys.argv[1] if len(sys.argv) > 1 else '/tmp/sbx/runs/F1/work/'
fold = lambda x: ''.join(c for c in unicodedata.normalize('NFKD', x or '') if not unicodedata.combining(c)).lower()
PUB = {int(k): v['ctrl_end'] for k, v in json.load(open('/tmp/fix/i/engine/published_service.json')).items()}
L = json.load(open('/work/lvm_cache.json')); CH = {}
for pid, end in PUB.items():
    rec = L.get(str(pid))
    if isinstance(rec, dict):
        sp = AR.control_span(rec, pid)
        if sp and sp[1] != end: CH[str(pid)] = fold(rec.get('name'))
def hit(obj):
    t = fold(json.dumps(obj, ensure_ascii=False))
    return any(i in CH for i in re.findall(r'"(\d{6})"', json.dumps(obj))) or any(n and n in t for n in CH.values())
A, B = snapshot(Z), snapshot(RUNP)
def ents(r, ch):
    if ch == 'ext': return r.get('allx_ext') or []
    if ch == 'fa': return r.get('allx_fa') or []
    if ch == 'intl': return r.get('allx_intl') or []
    return (r.get('allx') or {}).get(ch) or []
TBa = json.load(open(Z + 'trade_book.json'))['trades']; TBb = json.load(open(RUNP + 'trade_book.json'))['trades']
def tids(seats): return {str(x[0]) for st in seats for part in st[2:] for x in (part or [])}
seat_ch = {}
for d, seats in TBb:
    for st in seats: seat_ch[(d, st[0])] = bool(tids(seats) & set(CH))
chan_status = {}
untr_entries = 0
for i in A['R']:
    ra, rb = A['R'][i], B['R'].get(i)
    if rb is None: continue
    for ch in set((ra.get('chan') or {})) | set((rb.get('chan') or {})):
        ea, eb = ents(ra, ch), ents(rb, ch)
        moved = [y for x, y in zip(ea, eb) if x != y] + (eb[len(ea):] if len(eb) > len(ea) else [])
        un = [m for m in moved if not hit(m)]
        untr_entries += len(un)
        net_changed = A['nets'].get((i, ch)) != B['nets'].get((i, ch))
        if ch == 'trade' and not moved and net_changed:
            moved = ['seat']; un = [] if any(seat_ch.get(k) for k in seat_ch if k[1] == ra.get('abbr')) else ['seat']
        chan_status[(i, ch)] = {'moved': len(moved), 'untraced': len(un), 'net_changed': net_changed,
                                'attributed': (not un) and (bool(moved) or not net_changed)}
d = diff(A, B)
lch = d['letters']; och = [i for i in d['overall']]
unl = [k for k in lch if not chan_status.get(k, {}).get('attributed')]
uno = [i for i in och if not all(s['attributed'] for k, s in chan_status.items() if k[0] == i and (s['net_changed'] or s['moved']))
       or not any(s['net_changed'] or s['moved'] for k, s in chan_status.items() if k[0] == i)]
un_nets = [k for k in d['nets'] if not chan_status.get(k, {}).get('attributed')]
un_seats = [k for k in d['seats'] if not seat_ch.get(k)]
wB = {(r[0], r[1]): r for r in json.load(open(RUNP + 'offseasons.json'))['rows']}
un_w = [k for k in d['winters'] if k in wB and not any(str(x[-1]) in CH for x in (wB[k][12] or []))]
def band(W):
    s = sorted(W, key=lambda k: W[k]); r = s.index(('TOR', 2012)) + 1
    return r, round(W[s[20]] - W[('TOR', 2012)], 2)
bA, bB = band(A['winters']), band(B['winters'])
pages = {k[0] for k in unl} | set(uno) | {f'{a}-{y}' for a, y in un_w} | {k[0] for k in un_nets}
res = {'CH': len(CH), 'letters_changed': len(lch), 'overall_changed': len(och), 'untraced_letters': len(unl), 'untraced_overall': len(uno),
       'changed_nets': len(d['nets']), 'unattributed_nets': len(un_nets), 'changed_seats': len(d['seats']), 'unattributed_seats': len(un_seats),
       'changed_winters': len(d['winters']), 'unattributed_winters': len(un_w), 'unattributed_entries': untr_entries,
       'TOR_live': bA, 'TOR_run': bB, 'untraced_pages': len(pages)}
bars = {'untraced_letters==0': len(unl) == 0, 'untraced_overall==0': len(uno) == 0,
        'every_number_attributed': len(un_nets) + len(un_seats) + len(un_w) + untr_entries == 0,
        'letters<=150': len(lch) <= 150, 'overall<=40': len(och) <= 40, 'TOR_top2_90pct': bB[0] <= 2 and bB[1] >= 0.9 * bA[1],
        'untraced_pages<=50': len(pages) <= 50}
res['bars'] = bars; res['PASS'] = all(bars.values())
res['examples'] = {'untraced_letters': [list(k) for k in unl[:8]], 'untraced_overall': uno[:8], 'unattributed_nets': [list(k) for k in un_nets[:8]],
                   'unattributed_seats': [list(k) for k in un_seats[:8]], 'unattributed_winters': [list(k) for k in un_w[:8]]}
print(json.dumps(res, indent=1))
