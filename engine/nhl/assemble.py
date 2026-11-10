# One row per skater, season and club (a traded player has a row per club), plus goalie and club tables.
import json, glob, re, pandas as pd
def load(rep):
    rows = []
    for f in glob.glob(f'raw/{rep}_*.json'):
        m = re.search(r'_(\d{8})_(\d+)\.json$', f); s, t = int(m.group(1)), int(m.group(2))
        for r in json.load(open(f)): r['seasonId'] = s; r['teamId'] = t; rows.append(r)
    return pd.DataFrame(rows)
K = ['playerId', 'seasonId', 'teamId']
sm = load('skater_summary')[K + ['skaterFullName', 'positionCode', 'gamesPlayed', 'goals', 'assists', 'points', 'evGoals', 'evPoints', 'ppGoals', 'ppPoints', 'shGoals', 'shPoints', 'shots', 'plusMinus', 'penaltyMinutes']]
toi = load('skater_timeonice')[K + ['timeOnIce', 'evTimeOnIce', 'ppTimeOnIce', 'shTimeOnIce']]
gfa = load('skater_goalsForAgainst')[K + ['evenStrengthGoalsFor', 'evenStrengthGoalsAgainst', 'powerPlayGoalFor', 'powerPlayGoalsAgainst', 'shortHandedGoalsFor', 'shortHandedGoalsAgainst']]
pen = load('skater_penalties')[K + ['penalties', 'minorPenalties', 'majorPenalties', 'penaltiesDrawn']]
rt = load('skater_realtime')[K + ['hits', 'blockedShots', 'takeaways', 'giveaways', 'missedShots', 'shotAttemptsBlocked', 'totalShotAttempts', 'emptyNetGoals']]
ss = load('skater_summaryshooting')[K + ['satFor', 'satAgainst', 'satRelative', 'usatFor', 'usatAgainst', 'usatRelative', 'timeOnIcePerGame5v5']]
sk = sm
for d in (toi, gfa, pen, rt, ss): sk = sk.merge(d, on=K, how='left')
sk['pos'] = sk.positionCode.map(lambda c: 'D' if c == 'D' else 'F')
go = load('goalie_summary')[K + ['goalieFullName', 'gamesPlayed', 'gamesStarted', 'wins', 'losses', 'shotsAgainst', 'saves', 'goalsAgainst', 'timeOnIce', 'shutouts']]
tm = load('team_summary').drop(columns=['teamId']) if False else None
rows = []
for f in glob.glob('raw/team_summary_*_0.json'): rows += json.load(open(f))
tm = pd.DataFrame(rows)
b = []
for f in glob.glob('raw/skater_bios_*_0.json') + glob.glob('raw/goalie_bios_*_0.json'):
    for r in json.load(open(f)): b.append({'playerId': r['playerId'], 'name': r.get('skaterFullName') or r.get('goalieFullName'), 'birthDate': r.get('birthDate'), 'draftYear': r.get('draftYear'), 'draftRound': r.get('draftRound'), 'draftOverall': r.get('draftOverall'), 'nat': r.get('nationalityCode')})
bio = pd.DataFrame(b).drop_duplicates('playerId')
sk.to_pickle('sk.pkl'); go.to_pickle('go.pkl'); tm.to_pickle('tm.pkl'); bio.to_pickle('bio.pkl')
print(len(sk), len(go), len(tm), len(bio))
