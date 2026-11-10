# Pull NHL season lines from the league's public stats service, one file per report, season and club.
# Cached under raw/; re-running only fetches what is missing.
import json, os, sys, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
BASE = 'https://api.nhle.com/stats/rest/en/'
SEASONS = [y*10000 + y + 1 for y in range(1998, 2026) if y != 2004]
SK = ['skater/summary', 'skater/timeonice', 'skater/goalsForAgainst', 'skater/penalties', 'skater/realtime', 'skater/summaryshooting']
GO = ['goalie/summary']
os.makedirs('raw', exist_ok=True)
def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read())
        except Exception as e:
            err = e; time.sleep(1.5 * (i + 1))
    raise err
def one(job):
    rep, season, team = job
    fn = f"raw/{rep.replace('/', '_')}_{season}_{team}.json"
    if os.path.exists(fn) and os.path.getsize(fn) > 2: return 0
    exp = f"seasonId={season} and gameTypeId=2" + (f" and teamId={team}" if team else '')
    url = BASE + rep + '?isAggregate=false&isGame=false&start=0&limit=-1&cayenneExp=' + urllib.parse.quote(exp)
    try: d = get(url)
    except Exception as e: print('FAIL', job, e, flush=True); return 0
    json.dump(d.get('data', []), open(fn, 'w')); return 1
# club lists and league-wide bios first
with ThreadPoolExecutor(6) as ex: list(ex.map(one, [('team/summary', s, 0) for s in SEASONS] + [('skater/bios', s, 0) for s in SEASONS] + [('goalie/bios', s, 0) for s in SEASONS]))
jobs = []
for s in SEASONS:
    for t in json.load(open(f'raw/team_summary_{s}_0.json')):
        for rep in SK + GO: jobs.append((rep, s, t['teamId']))
print(len(jobs), 'jobs', flush=True)
with ThreadPoolExecutor(6) as ex: n = sum(ex.map(one, jobs))
print('fetched', n)
