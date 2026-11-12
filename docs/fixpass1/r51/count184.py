# Round 51: how many of the 184 frame players share each cause.
import json, importlib.util, collections, datetime
spec = importlib.util.spec_from_file_location('sf', '/tmp/r48/eng/svc_fetch.py'); SF = importlib.util.module_from_spec(spec); spec.loader.exec_module(SF)
C = json.load(open('/tmp/r45/svc/frame_tx.json'))
ON = ('SE', 'CU', 'CLW', 'R5', 'PUR')
morgan, morgan_days, retro, dfa = [], 0, [], []
for pid, T in C.items():
    T = sorted(T, key=lambda t: t['date'] or '')          # stable: keeps feed order within a date, as the counter does
    by = collections.defaultdict(list)
    for t in T: by[t['date']].append(t)
    for d, L in by.items():
        y = int(d[:4]) if d else 0
        if y not in SF.SEAS or not ((SF.SEAS[y][0] - datetime.timedelta(days=30)).isoformat() <= d <= SF.SEAS[y][1].isoformat()): continue
        codes = [t['typeCode'] for t in L]
        if 'OPT' in codes and any(c in ON for c in codes):
            on = False
            for t in L: on = SF.classify(t, on)
            if on:                                         # counter ends the day on although the player was optioned that day
                nxt = next((t['date'] for t in T if (t['date'] or '') > d), SF.SEAS[y][1].isoformat())
                n = max(0, (min(datetime.date.fromisoformat(nxt), SF.SEAS[y][1]) - max(datetime.date.fromisoformat(d), SF.SEAS[y][0])).days)
                morgan.append([pid, d, codes, n]); morgan_days += n
        for t in L:
            ds = (t['description'] or '').lower()
            if 'injured list' in ds and 'retroactive' in ds and t['toTeam']['id'] in SF.MLB: retro.append([pid, d])
            if t['typeCode'] == 'DES' and t['toTeam']['id'] in SF.MLB: dfa.append([pid, d])
out = {'same_day_option_left_on': {'players': len({m[0] for m in morgan}), 'dates': len(morgan), 'days_overcounted': morgan_days, 'list': morgan},
       'truth_method_blind_spots': {'retroactive_IL_players': len({r[0] for r in retro}), 'retroactive_IL_records': len(retro),
                                    'in_season_DFA_players': len({r[0] for r in dfa}), 'in_season_DFA_records': len(dfa)}}
json.dump(out, open('count184.json', 'w'), indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'list'} for k, v in out.items()}))
for m in morgan[:12]: print(m)
