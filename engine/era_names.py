"""Club names as they were in a given season (v5.4): a 2003 title belongs to
the Florida Marlins, not the Miami Marlins."""
def era_team(team, yr):
    yr = int(yr)
    if team == "Miami Marlins" and yr <= 2011: return "Florida Marlins"
    if team == "Los Angeles Angels":
        if yr <= 1996: return "California Angels"
        if yr <= 2004: return "Anaheim Angels"
        if yr <= 2015: return "Los Angeles Angels of Anaheim"
    if team == "Cleveland Guardians" and yr <= 2021: return "Cleveland Indians"
    if team == "Tampa Bay Rays" and yr <= 2007: return "Tampa Bay Devil Rays"
    if team == "Washington Nationals" and yr <= 2004: return "Montreal Expos"
    if team == "Athletics" and yr <= 2024: return "Oakland Athletics"
    return team

# First day of each MLB first-year player draft (v5.4: draft decisions used a
# June 15 placeholder; the drafts moved to July in 2021)
DRAFT_DAY = {1998: "06-02", 1999: "06-02", 2000: "06-05", 2001: "06-05", 2002: "06-04",
             2003: "06-03", 2004: "06-07", 2005: "06-07", 2006: "06-06", 2007: "06-07",
             2008: "06-05", 2009: "06-09", 2010: "06-07", 2011: "06-06", 2012: "06-04",
             2013: "06-06", 2014: "06-05", 2015: "06-08", 2016: "06-09", 2017: "06-12",
             2018: "06-04", 2019: "06-03", 2020: "06-10", 2021: "07-11", 2022: "07-17",
             2023: "07-09", 2024: "07-14", 2025: "07-13", 2026: "07-11"}
def draft_day(yr):
    yr = int(yr)
    return f"{yr}-{DRAFT_DAY.get(yr, '06-15')}"
