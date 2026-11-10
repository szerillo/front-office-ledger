# Trade history from Wikipedia's season transaction pages (text is CC BY-SA 4.0; each row there cites the
# club or league announcement). Pulls 2005-06 to 2025-26, parses every trade into two sides of assets, and
# matches players to league ids. Writes trades.json. A prototype: sourcing is Sean's decision.
import json, os, re, time, urllib.request, urllib.parse, unicodedata, pandas as pd
os.makedirs('wiki', exist_ok=True)
def page(y):
    fn = f'wiki/tx_{y}.json'
    if not os.path.exists(fn) and os.environ.get('NOFETCH'): return ''
    if not os.path.exists(fn):
        title = f"{y}–{str(y + 1)[2:]} NHL transactions"
        url = 'https://en.wikipedia.org/w/api.php?action=parse&prop=wikitext&format=json&formatversion=2&redirects=1&page=' + urllib.parse.quote(title)
        req = urllib.request.Request(url, headers={'User-Agent': 'FrontOfficeLedger-research/0.1 (frontofficeledger.com)'})
        for wait in (0, 20, 45, 90):
            time.sleep(wait)
            try: body = urllib.request.urlopen(req, timeout=40).read().decode(); break
            except urllib.error.HTTPError as e:
                if e.code != 429: raise
        else: print('rate limited at', y, flush=True); os.environ['NOFETCH'] = '1'; return ''
        open(fn, 'w').write(body); time.sleep(20)
    d = json.load(open(fn)); return d.get('parse', {}).get('wikitext', '')
tm = pd.read_pickle('tm.pkl'); TEAM = {r.teamFullName: r.teamId for r in tm.itertuples()}
TEAM.update({'Montréal Canadiens': 8, 'Montreal Canadiens': 8, 'St. Louis Blues': 19, 'Utah Hockey Club': TEAM.get('Utah Hockey Club', 59), 'Utah Mammoth': TEAM.get('Utah Mammoth', 68)})
norm = lambda s: re.sub(r'[^a-z ]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip()
bio = pd.read_pickle('bio.pkl'); NAME = {}
for r in bio.itertuples(): NAME.setdefault(norm(str(r.name)), []).append(r.playerId)
ps = pd.read_csv('player_seasons_v1.csv'); ON = {}
for r in ps.itertuples(): ON.setdefault(r.playerId, set()).add((r.seasonId // 10000, r.teamId))
MON = 'January|February|March|April|May|June|July|August|September|October|November|December'
def clean(s):
    s = re.sub(r'<ref[^>]*>.*?</ref>|<ref[^>]*/>', '', s, flags=re.S); s = re.sub(r'\{\{efn[^{}]*(\{\{[^{}]*\}\}[^{}]*)*\}\}', '', s); s = re.sub(r'\{\{[^{}]*\}\}', '', s)
    return s
ORD = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth']
def asset(a, y, teams):
    a = a.strip(" *'\n"); low = a.lower()
    if not a: return None
    m = re.search(r'\b(\d|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth)(?:st|nd|rd|th)?[- ]round\b', a, flags=re.I)
    if m and 'pick' in low:
        yr = re.search(r'\b(19|20)\d{2}\b', a); rd = m.group(1).lower(); rd = int(rd) if rd.isdigit() else ORD.index(rd) + 1
        o = re.search(r'\[\[([^|\]]+)\|[A-Z]{2,3}\]\]', a[:m.start()])
        ov = re.search(r'#\s?(\d{1,3})\b', a)
        return {'k': 'pick', 'round': rd, 'year': int(yr.group(0)) if yr else None, 'orig': TEAM.get(o.group(1)) if o else None, 'cond': 'conditional' in low, 'ov': int(ov.group(1)) if ov else None}
    links = [(t, d or t) for t, d in re.findall(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]', a) if 'draft' not in t.lower() and t not in TEAM and not re.fullmatch(r'\d{4}.*', t)]
    if links and not any(w in low for w in ('future considerations', 'cash')):
        t, d = links[0]; nm = re.sub(r'\s*\(.*?\)\s*$', '', t); ids = NAME.get(norm(nm), []) or NAME.get(norm(d), [])
        if len(ids) > 1:
            near = [i for i in ids if any((yy, tt) in ON.get(i, ()) for yy in (y - 1, y, y + 1) for tt in teams)]; ids = near or ids
        return {'k': 'player', 'name': d if d and len(d) > 3 else nm, 'id': int(ids[0]) if len(ids) == 1 else None, 'rights': 'rights' in low, 'amb': len(ids) > 1}
    return {'k': 'other', 'txt': re.sub(r'\[\[|\]\]', '', a)[:60]}
out = []
for y in range(2005, 2026):
    w = page(y); i = w.find('==Trades=='); i = i if i >= 0 else w.find('== Trades =='); j = len(w)
    for stop in ('==Waivers', '== Waivers', '==Free agen', '== Free agen', '==See also', '== See also', '==Retirement', '== Retirement'):
        k = w.find(stop, i + 10)
        if k > 0: j = min(j, k)
    sec = clean(w[i:j]); date = None; n0 = len(out)
    for row in re.split(r'\n\|-[^\n]*', sec):
        dm = re.search(r'(' + MON + r')\s+(\d{1,2}),?\s+(\d{4})', row.split('To ')[0] if 'To ' in row else row[:200])
        if dm: date = pd.Timestamp(f"{dm.group(1)} {dm.group(2)} {dm.group(3)}").strftime('%Y-%m-%d')
        sides = re.findall(r"To\s+'*\[\[([^|\]]+)(?:\|[^\]]*)?\]\]'*\s*<hr\s*/?>(.*?)(?=\n\|(?!-)|\Z)", row, flags=re.S)
        if len(sides) < 2 or not date: continue
        tids = [TEAM.get(s[0]) for s in sides[:2]]
        S = [{'team': t, 'teamName': s[0], 'gets': [x for x in (asset(a, y, tids) for a in re.split(r'<br\s*/?>|\n', s[1])) if x]} for s, t in zip(sides[:2], tids)]
        out.append({'season': y, 'date': date, 'sides': S, 'three': len(sides) > 2})
    print(y, 'trades', len(out) - n0, flush=True)
json.dump(out, open('trades.json', 'w'))
pl = [a for t in out for s in t['sides'] for a in s['gets'] if a['k'] == 'player']; pk = [a for t in out for s in t['sides'] for a in s['gets'] if a['k'] == 'pick']
print('trades', len(out), '| players', len(pl), 'matched to a league id', sum(1 for a in pl if a['id']), 'ambiguous', sum(1 for a in pl if a['amb'] and not a['id']), '| picks', len(pk), 'conditional', sum(1 for a in pk if a['cond']), '| other', sum(1 for t in out for s in t['sides'] for a in s['gets'] if a['k'] == 'other'), '| unknown clubs', sum(1 for t in out for s in t['sides'] if not s['team']), '| three-club', sum(1 for t in out if t['three']))
print('unmatched sample:', [a['name'] for a in pl if not a['id']][:25])
