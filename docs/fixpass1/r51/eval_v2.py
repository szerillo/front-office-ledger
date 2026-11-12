# Round 51 evaluator (prereg_r51). Usage: eval_v2.py <base work dir> <run work dir> [out.json]
# Letters use the live (Z_X6) spread and cutoffs. Attribution: an entry is attributed if it carries the id or the
# accent-folded name of a changed-control player (CH, /tmp/r51/ch.json); a trade is attributed if any seat of that
# trade (same date and same set of clubs) holds a CH id; a winter move is attributed if its player is CH or, for a
# trade move, the trade that day for that club is attributed; aggregates are attributed if every moved part is.
import sys, json, re, unicodedata, collections; sys.path.insert(0, '/tmp/r49/eval'); from common import *
BASE, RUNP = sys.argv[1], sys.argv[2]
fold = lambda x: ''.join(c for c in unicodedata.normalize('NFKD', x or '') if not unicodedata.combining(c)).lower()
CHI = set(json.load(open('/tmp/r51/ch.json'))); L = json.load(open('/work/lvm_cache.json'))
CHN = {fold(L[i].get('name')) for i in CHI if isinstance(L.get(i), dict) and L[i].get('name')}
def hit(obj):
    s = json.dumps(obj, ensure_ascii=False)
    return any(i in CHI for i in re.findall(r'"?(\d{6})"?', s)) or any(n and n in fold(s) for n in CHN)
A, B = snapshot(BASE), snapshot(RUNP)
def trades(p):
    out = collections.defaultdict(list)
    for d, seats in json.load(open(p + 'trade_book.json'))['trades']:
        out[(d, tuple(sorted(st[0] for st in seats)))].append(seats)
    return out
TA, TB = trades(BASE), trades(RUNP)
def ids(seats): return {str(x[0]) for st in seats for part in st[2:] for x in (part or [])}
trade_moved, trade_un = 0, []
club_day_attr = {}
for k in set(TA) | set(TB):
    a, b = TA.get(k, []), TB.get(k, [])
    att = any(ids(s) & CHI for s in a + b)
    for s in b:
        for st in s: club_day_attr[(k[0], st[0])] = club_day_attr.get((k[0], st[0]), False) or att
    if json.dumps(a) != json.dumps(b):
        trade_moved += 1
        if not att: trade_un.append(list(k))
def ents(r, ch):
    if ch == 'ext': return r.get('allx_ext') or []
    if ch == 'fa': return r.get('allx_fa') or []
    if ch == 'intl': return r.get('allx_intl') or []
    return (r.get('allx') or {}).get(ch) or []
chan, un_entries = {}, 0
for i in A['R']:
    ra, rb = A['R'][i], B['R'].get(i)
    if rb is None: continue
    for ch in set(ra.get('chan') or {}) | set(rb.get('chan') or {}):
        ea, eb = ents(ra, ch), ents(rb, ch)
        moved = [y for x, y in zip(ea, eb) if x != y] + eb[len(ea):]
        un = [m for m in moved if not (hit(m) or (ch == 'trade' and club_day_attr.get((str(m[0])[:10], ra.get('abbr')))))]
        un_entries += len(un)
        nc = A['nets'].get((i, ch)) != B['nets'].get((i, ch))
        chan[(i, ch)] = {'moved': len(moved), 'un': len(un), 'nc': nc, 'att': (not un) and (bool(moved) or not nc)}
d = diff(A, B)
unl = [k for k in d['letters'] if not chan.get(k, {}).get('att')]
def fo_att(i): 
    ks = [s for k, s in chan.items() if k[0] == i and (s['nc'] or s['moved'])]
    return bool(ks) and all(s['att'] for s in ks)
uno = [i for i in d['overall'] if not fo_att(i)]
un_nets = [k for k in d['nets'] if not chan.get(k, {}).get('att')]
WA = {(r[0], r[1]): r for r in json.load(open(BASE + 'offseasons.json'))['rows']}
WB = {(r[0], r[1]): r for r in json.load(open(RUNP + 'offseasons.json'))['rows']}
un_w = []
for k in d['winters']:
    ma, mb = (WA.get(k) or [None] * 13)[12] or [], (WB.get(k) or [None] * 13)[12] or []
    moved = [y for x, y in zip(ma, mb) if x != y] + mb[len(ma):]
    ok = bool(moved) and all(str(m[-1]) in CHI or (m[0] == 't' and club_day_attr.get((m[1], k[0]))) for m in moved)
    if not ok: un_w.append(list(k))
def band(W):
    s = sorted(W, key=lambda k: W[k]); r = s.index(('TOR', 2012)) + 1
    return r, round(W[s[20]] - W[('TOR', 2012)], 2)
bA, bB = band(A['winters']), band(B['winters'])
pages = {k[0] for k in unl} | set(uno) | {k[0] for k in un_nets} | {f'{a}-{y}' for a, y in un_w} | {f'trade {k[0]}' for k in trade_un}
res = {'letters_changed': len(d['letters']), 'overall_changed': len(d['overall']), 'nets_changed': len(d['nets']), 'trades_changed': trade_moved,
       'winters_changed': len(d['winters']), 'untraced_letters': len(unl), 'untraced_overall': len(uno), 'unattributed_nets': len(un_nets),
       'unattributed_entries': un_entries, 'unattributed_trades': len(trade_un), 'unattributed_winters': len(un_w), 'untraced_pages': len(pages),
       'TOR_base': bA, 'TOR_run': bB,
       'examples': {'letters': [list(k) for k in unl[:6]], 'overall': uno[:6], 'nets': [list(k) for k in un_nets[:6]], 'trades': trade_un[:6], 'winters': un_w[:6]}}
res['all_attributed'] = res['untraced_letters'] == 0 and res['untraced_overall'] == 0 and res['unattributed_nets'] == 0 and un_entries == 0 and not trade_un and not un_w
if len(sys.argv) > 3: json.dump(res, open(sys.argv[3], 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'examples'}))
