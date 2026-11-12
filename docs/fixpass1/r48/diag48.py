# Round 48 diagnosis: classify the 13 untraced I1 changes as tracer reach or recalibration. Reads saved runs only; no re-score.
import json, re, sys, unicodedata
sys.path.insert(0, '/tmp/fix/f/engine'); import asset_rules as AR
B, I = '/tmp/sbx/runs/Z_X6/work/', '/tmp/sbx/runs/I1/work/'
fold = lambda s: unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
PUB = {int(k): v['ctrl_end'] for k, v in json.load(open('/tmp/fix/i/engine/published_service.json')).items()}
L = json.load(open('/work/lvm_cache.json')); CH = {}
for pid, end in PUB.items():
    rec = L.get(str(pid))
    if isinstance(rec, dict):
        sp = AR.control_span(rec, pid)
        if sp and sp[1] != end: CH[str(pid)] = fold(rec.get('name'))
def recs(p):
    o = {}
    for f in ('sweep_results.json', 'hist_results.json'):
        for r in json.load(open(p + f)): o[r['id']] = r
    return o
RB, RI = recs(B), recs(I)
R = json.load(open('i1_result.json'))['examples']
items = [tuple(x) for x in R['untraced_letters']] + [(i, None) for i in R['untraced_overall']]
out = []
def ents(r, ch):
    return r.get('allx_ext') if ch == 'ext' else (r.get('allx') or {}).get(ch)
for fid, ch in items:
    chans = [ch] if ch else [k for k in RB[fid]['chan'] if RB[fid]['chan'][k].get('net') != RI[fid]['chan'].get(k, {}).get('net')]
    hit, moved = [], 0
    for c in chans:
        a, b = ents(RB[fid], c) or [], ents(RI[fid], c) or []
        for x, y in zip(a, b):
            if x != y:
                moved += 1
                t = fold(json.dumps(x, ensure_ascii=False))
                if any(n and n in t for n in CH.values()) or any(i in CH for i in re.findall(r'"(\d{6})"', t)): hit.append(x[1])
    cause = 'tracer reach' if hit else 'recalibration'
    out.append({'fid': fid, 'chan': ch or 'overall:' + ','.join(chans), 'entries_moved': moved, 'ch_players_found_after_accent_fold': hit, 'cause': cause,
                'net': [RB[fid]['chan'][c]['net'] for c in chans], 'net_I1': [RI[fid]['chan'][c]['net'] for c in chans]})
json.dump(out, open('/tmp/r47/eval/diag48.json', 'w'), indent=1)
for o in out: print(o['cause'].ljust(14), o['fid'], o['chan'], o['entries_moved'], o['ch_players_found_after_accent_fold'], o['net'], o['net_I1'])
print({c: sum(o['cause'] == c for o in out) for c in ('tracer reach', 'recalibration')})
