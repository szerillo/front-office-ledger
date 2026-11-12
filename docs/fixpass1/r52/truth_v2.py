# Round 52 truth method v2 (prereg_kinley_truth_v2.md). A season day counts as service if, for an MLB club, the player
# is on the active roster (daily roster service), or on the MLB injured list (from the retroactive date when the filing
# gives one, else the filing date, to activation), or in DFA limbo (from the designation to its resolution), or on
# optional assignment when his option days that season total fewer than 20. Scaled to 186 days and capped at 172 like
# the counter. Inputs: the player's transactions and the clubs' daily active rosters (cached).
import re, datetime
MON = {m: i for i, m in enumerate(['january','february','march','april','may','june','july','august','september','october','november','december'], 1)}
def retro_date(desc):
    m = re.search(r'retroactive to (\w+) (\d+), (\d{4})', desc or '', re.I)
    if m and m.group(1).lower() in MON: return datetime.date(int(m.group(3)), MON[m.group(1).lower()], int(m.group(2)))
    return None
def spans(T, MLB, season):
    """IL, DFA and option spans (start inclusive, end exclusive) from the transactions"""
    T = sorted(T, key=lambda t: t['date'] or ''); a, b = season
    il, dfa, opt = [], [], []
    cur_il = cur_dfa = cur_opt = None
    for t in T:
        if not t['date']: continue
        d = datetime.date.fromisoformat(t['date']); ds = (t['description'] or '').lower(); c = t['typeCode']; to = t['toTeam']['id']
        on_mlb_il = to in MLB and 'injured list' in ds and ('placed' in ds or 'transferred' in ds)
        if on_mlb_il and cur_il is None: cur_il = min(d, retro_date(t['description']) or d)
        elif cur_il is not None and ('activated' in ds or 'reinstated' in ds or c in ('REL', 'OUT', 'OPT', 'DES') or 'elected free agency' in ds):
            il.append((cur_il, d)); cur_il = None
        if c == 'DES' and to in MLB: cur_dfa = d
        elif cur_dfa is not None and (c in ('OUT', 'REL', 'CLW', 'TR', 'OPT', 'SE', 'CU') or 'elected free agency' in ds or 'activated' in ds):
            dfa.append((cur_dfa, d)); cur_dfa = None
        if c == 'OPT': cur_opt = cur_opt or d
        elif cur_opt is not None and (c in ('CU', 'SE', 'DES', 'REL', 'OUT', 'TR', 'CLW') or on_mlb_il or 'elected free agency' in ds):
            opt.append((cur_opt, d)); cur_opt = None
    end = b + datetime.timedelta(days=1)
    for cur, lst in ((cur_il, il), (cur_dfa, dfa), (cur_opt, opt)):
        if cur is not None: lst.append((cur, end))
    return il, dfa, opt
def days_in(sp, a, b):
    out = set()
    for s, e in sp:
        d = max(s, a)
        while d < e and d <= b: out.add(d); d += datetime.timedelta(days=1)
    return out
def truth_v2(pid, T, season, MLB, active_days):
    a, b = season; n = (b - a).days + 1
    il, dfa, opt = spans(T, MLB, season)
    ild, dfad, optd = days_in(il, a, b), days_in(dfa, a, b), days_in(opt, a, b)
    optd_credit = optd if 0 < len(optd) < 20 else set()
    tot = set(active_days) | ild | dfad | optd_credit
    return min(172, round(len(tot) * 186.0 / n)), {'active': len(active_days), 'il': len(ild), 'dfa': len(dfad), 'opt': len(optd), 'opt_credited': len(optd_credit)}
