"""Round 44: last season of club control from MLB service time (pre-registered: docs/fixpass1/r44/prereg_control_end.md).
Service = days on the active roster or the MLB injured list during each regular season, counted from the MLB Stats
API transaction history (svc_fetch.classify), actual days capped at 172 (no rescaling); 2020 x 172/67; 2022 + 7
lockout days if active on opening day; option stints under 20 days in a season count. Control ends in the season
service reaches 6.000 years (1,032 days); short of that at the end of 2026, projected at 172 a season.
Players whose debut is before 2009 (no transactions in the feed) return None: callers keep the old rule."""
import json, os
from datetime import date, timedelta
ROOT = os.environ.get('SVC_ROOT', '/work')
SEAS = {int(k): (date.fromisoformat(a), date.fromisoformat(b)) for k, (a, b) in json.load(open(f'{ROOT}/season_calendar.json')).items()}
TX = json.load(open(f'{ROOT}/svc_tx_full.json'))
DEB = json.load(open(f'{ROOT}/debuts.json'))
import svc_classify as C
def season_days(txs, debut):
    txs = sorted(txs, key=lambda t: t.get('date') or ''); by = {}; on = False; i = 0
    for y in sorted(SEAS):
        a, b = SEAS[y]; days = 0; opt_days = 0; opt_run = 0; opened = None
        while i < len(txs) and (txs[i].get('date') or '') < a.isoformat(): on = C.classify(txs[i], on); i += 1
        on_opening = on; d = a; last_opt = False
        while d <= b:
            ds = d.isoformat(); was = on; opt_today = False
            while i < len(txs) and (txs[i].get('date') or '') <= ds:
                t = txs[i]; on = C.classify(t, on); i += 1
                if t.get('typeCode') == 'OPT': opt_today = True
            if on: days += 1; last_opt = False
            elif opt_today or last_opt: opt_days += 1; last_opt = True
            d += timedelta(days=1)
        if 0 < opt_days < 20 and days: days += opt_days        # option stints under 20 days in aggregate count
        if y == 2020: days = round(days * 172 / 67)
        if y == 2022 and on_opening: days += 7
        if days: by[y] = min(172, days)
    return by
def control_end(pid):
    d = DEB.get(str(pid)); tx = TX.get(str(pid))
    if not d or int(d[:4]) < 2009 or tx is None: return None
    by = season_days(tx, d); run = 0
    for y in sorted(by):
        run += by[y]
        if run >= 1032: return y
    need = 1032 - run
    return max(SEAS) + -(-need // 172)           # still short after the last season: 172 a season from here
