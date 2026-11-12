MLB = {108,109,110,111,112,113,114,115,116,117,118,119,120,121,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,158}
import json, os
MINORS = set(json.load(open(os.environ.get("SVC_ROOT", "/work") + "/minors_ids.json")))
def team_id(t):
    return (t or {}).get("id")

def classify(t, on):
    c = t.get("typeCode", ""); d = (t.get("description") or "").lower()
    to = team_id(t.get("toTeam")); to_mlb = to in MLB; to_minors = to in MINORS
    if c in ("NUM", "SGN"): return on            # draft/amateur signings never put a player on an MLB roster
    if "rehab" in d: return on                   # rehab assignments: still on the MLB injured list
    if c == "OPT": return False
    if c in ("OUT", "REL", "RET"): return False
    if c in ("SE", "CU"): return True
    if c in ("R5", "CLW"): return True if to_mlb else on
    if c == "SFA":
        if "minor league" in d: return False
        return True if to_mlb else on
    if c == "DES" or c == "TR": return on
    if c in ("ASG", "SC"):
        if to_minors:
            return False if (c == "ASG" or "activated" in d or "placed" in d or "injured list" in d) else on
        if not to_mlb: return on                 # All-Star, Futures, WBC, AFL: not a roster move
        if c == "ASG": return on                 # spring assignment to the big-league camp
        if "restricted list" in d and "placed" in d: return False
        if "injured list" in d and ("placed" in d or "transferred" in d): return True
        if "activated" in d or "reinstated" in d: return True
        # end-of-season "reassigned to the minor leagues" is paperwork for 40-man
        # players, not a demotion; an in-season demotion is filed as an option
        if "reassigned" in d and "minor" in d: return on
        return on
    return on

