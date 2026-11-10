# Flatten the game files into one table of shot attempts with what an expected-goals model needs.
import gzip, json, math, numpy as np, pandas as pd
rows = []
for y in range(2010, 2026):
    with gzip.open(f'pbp/{y}.jsonl.gz', 'rt') as f:
        for line in f:
            g = json.loads(line)
            if g.get('none'): continue
            ev = sorted((e for e in g['ev'] if e[2] is not None and e[3]), key=lambda e: (e[1], e[2]))
            # which way each club shoots in each period: the side most of its attempts come from
            side = {}
            for e in ev:
                if e[5] is not None and e[0] != 'b': side.setdefault((e[1], e[3]), []).append(e[5])
            side = {k: (1 if np.median(v) >= 0 else -1) for k, v in side.items()}
            sc = {g['home']: 0, g['away']: 0}; last = None
            for e in ev:
                t, per, sec, team, shooter, x, yy, stype, sit, _, goalie, _z = e
                opp = g['away'] if team == g['home'] else g['home']
                if x is not None and yy is not None and per <= 4:
                    s = side.get((per, team), 1 if x >= 0 else -1)
                    dx, dy = 89 - s * x, yy
                    dist = math.hypot(dx, dy); ang = abs(math.degrees(math.atan2(dy, max(dx, 0.1)))) if dx > 0 else 90 + min(45, -dx * 5)
                    sit = sit or '1551'; home = team == g['home']
                    own, oth, og = (int(sit[2]), int(sit[1]), int(sit[0])) if home else (int(sit[1]), int(sit[2]), int(sit[3]))
                    gap = (per - last[0]) * 1200 + sec - last[1] if last else 99
                    rows.append((g['id'], y, per, sec, team, opp, shooter or 0, goalie or 0, t, x * s, yy, dist, ang, stype or 'none', own, oth, og, int(home),
                                 min(gap, 99) if last else 99, int(bool(last) and last[2] == team), last[3] if last else 'x', sc[team] - sc[opp]))
                last = (per, sec, team, t)
                if t == 'g' and per <= 4 and team in sc: sc[team] += 1
    print(y, len(rows), flush=True)
c = ['game', 'season', 'per', 'sec', 'team', 'opp', 'shooter', 'goalie', 'type', 'x', 'y', 'dist', 'ang', 'stype', 'own', 'oth', 'og', 'home', 'gap', 'sameTeam', 'prev', 'score']
d = pd.DataFrame(rows, columns=c); d.to_pickle('shots.pkl'); print(len(d), d.type.value_counts().to_dict())
