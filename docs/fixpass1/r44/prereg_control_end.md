# Pre-registration: service-time control end (round 44, before building or looking up any free-agent year)
Change: a player's last season of club control = the season in which his MLB service reaches 6.000 years (1,032
days), not "six seasons from debut".
Source for service: the MLB Stats API transaction history for each player (statsapi.mlb.com/api/v1/transactions,
the same feed engine/svc_fetch.py reads), counted day by day against each regular season's official start and end
dates (statsapi seasons endpoint): on the active roster or the MLB injured list = service; optioned, outrighted,
released or assigned to the minors = not. Actual days, capped at 172 a season (no rescaling to a 186-day calendar:
that rescaling turns Kris Bryant's 171 days in 2015 into 172). Special seasons: 2020 days x 172/67 (the 60-game
season was credited in proportion); 2022 adds the 7 lockout days to anyone active on opening day. Optioned stints that
total under 20 days in a season count as service (CBA rule). A player still short of 6.000 at the end of 2026 is
projected at 172 days a season.
Coverage: the feed's transactions start in 2009. Players who debuted before 2009 keep the old rule; this is stated on
the methodology page as a remaining limit.
Test sample (draw_sample.py, seed 20261144), fixed before any public free-agent year is looked up:
frame = 184 players with a graded extension, MLB debut 2010-2019, extension signed within 6 seasons of debut (182
after Donaldson and Olson are taken out to be checked on their own); 5 drawn from the 98 optioned in a season after
their debut season, then 15 drawn from the remaining frame. Truth = the free-agent year stated in a public report
(MLB Trade Rumors, MLB.com, ESPN, AP, CBS, The Athletic), searched by name; if none is found in two searches the
player is replaced by the next in the seeded replacement list of his group, and the replacement is reported.
Pass bar: at least 19 of 20 correct, AND Donaldson (free agent after 2018) and Olson (after 2023) correct.
If the bar fails: nothing is built into the regrade; report.
