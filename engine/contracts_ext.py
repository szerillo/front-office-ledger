"""Curated major contract extensions, materiality-first, limited to deals
signed inside CURRENT regime windows (the window filter in ext_grade.py
excludes anything else automatically). Terms are guaranteed totals from
contemporaneous public reporting; the 2025-26 wave was verified by web
search this session (Basallo, Anthony, Baz, Emerson, Griffin, PCA, Luzardo,
Soderstrom, Wilson, Pratt confirmed against ESPN/MLB.com/CBS/Banner
reports). cbt_m: CBT/present-value total where deferrals famously diverge
from nominal (Betts ~$306.7M PV of $365M). Format:
(sign "YYYY-MM", player, team abbr, years, total $M, cbt $M or None).
Long tail of small arb-buyout deals stays out and is disclosed as such."""

EXT = [
    # Coverage audit (Oct 2026, GM Mode build): long-term deals the book was
    # missing, surfaced when stars appeared in the computed FA class. Dates
    # encode coverage windows under desk_data's off rule (month<=3 -> covers
    # that season; month>3 -> covers next season on).
    ('2021-04', 'Francisco Lindor', 'NYM', 10, 341.0, None),    # 2022-2031
    ('2023-06', 'Rafael Devers', 'BOS', 10, 313.5, None),       # 2024-2033 (signed Jan 2023)
    ('2019-01', 'Mike Trout', 'LAA', 12, 426.5, None),          # 2019-2030
    ('2020-03', 'Christian Yelich', 'MIL', 9, 215.0, None),    # 2020-2028 (coverage audit v4.6)
    ('2023-03', 'Keibert Ruiz', 'WSH', 8, 50.0, None),          # 2023-2030 (coverage audit v4.6)
    ('2023-06', 'Pablo Lopez', 'MIN', 4, 73.5, None),           # 2024-2027 (coverage audit v4.6)
    ('2023-12', 'Tyler Glasnow', 'LAD', 4, 110.0, None),        # 2024-2027 guaranteed (coverage audit v4.6)
    # ---- 2027 club options exercised or plainly in-the-money (the 2026-27
    # winter reality pass; sources: the league option tracker, Nov 2026).
    # Encoded as one-year coverage at the option price.
    ('2026-11', 'William Contreras', 'MIL', 1, 15.5, None),
    ('2026-11', 'Isaac Paredes', 'HOU', 1, 13.35, None),
    ('2026-11', 'Sandy Alcantara', 'MIA', 1, 21.0, None),
    # Emmanuel Clase removed v5.2: restricted list, option moot
    ('2026-11', 'Garrett Whitlock', 'BOS', 1, 8.25, None),
    ('2026-11', 'Yandy Diaz', 'TB', 1, 12.0, None),
    ('2026-11', 'Ozzie Albies', 'ATL', 1, 7.0, None),
    ('2026-11', 'Andres Munoz', 'SEA', 1, 9.0, None),
    ('2026-11', 'Tony Gonsolin', 'KC', 1, 2.5, None),
    ('2024-04', 'Zack Wheeler', 'PHI', 3, 126.0, None),         # 2025-2027
    ('2024-09', 'Matt Chapman', 'SF', 6, 151.0, None),          # 2025-2030
    ('2022-06', 'Yordan Alvarez', 'HOU', 6, 115.0, None),       # 2023-2028
    ('2023-04', 'Logan Webb', 'SF', 5, 90.0, None),             # 2024-2028
    ('2025-04', 'Geraldo Perdomo', 'ARI', 4, 45.0, None),       # 2026-2029
    ('2019-01', 'Nolan Arenado', 'COL', 9, 275.0, None),        # 2019-2027 incl the exercised 2027 (AAV approximation on the 2027 add-on)
    ('2022-12', 'Willson Contreras', 'STL', 5, 87.5, None),     # FA deal absent from the csv; carried here for coverage
 # LAD (Friedman 2014-)
 ("2020-07","Mookie Betts","LAD",12,365,306.7),
 ("2024-03","Will Smith","LAD",10,140,None),
 ("2025-01","Tommy Edman","LAD",5,74,None),
 # TOR (Atkins 2015-)
 ("2021-11","Jose Berrios","TOR",7,131,None),
 ("2025-03","Alejandro Kirk","TOR",5,58,None),
 ("2025-04","Vladimir Guerrero Jr.","TOR",14,500,None),
 # ATL (Anthopoulos 2017-)
 ("2019-04","Ronald Acuna Jr.","ATL",8,100,None),
 ("2019-04","Ozzie Albies","ATL",7,35,None),
 ("2022-03","Matt Olson","ATL",8,168,None),
 ("2022-08","Austin Riley","ATL",10,212,None),
 ("2022-08","Michael Harris II","ATL",8,72,None),
 ("2022-10","Spencer Strider","ATL",6,75,None),
 ("2022-12","Sean Murphy","ATL",6,73,None),
 # SD (Preller 2014-)
 ("2021-02","Fernando Tatis Jr.","SD",14,340,None),
 ("2022-07","Joe Musgrove","SD",5,100,None),
 ("2023-02","Manny Machado","SD",11,350,None),
 ("2023-02","Yu Darvish","SD",6,108,None),
 ("2023-04","Jake Cronenworth","SD",7,80,None),
 ("2025-04","Jackson Merrill","SD",9,135,None),
 # KC (current regime)
 ("2024-02","Bobby Witt Jr.","KC",11,288.7,None),
 # SEA (Dipoto 2015-)
 ("2019-11","Evan White","SEA",6,24,None),
 ("2022-04","J.P. Crawford","SEA",5,51,None),
 ("2022-08","Julio Rodriguez","SEA",12,209.3,None),
 ("2025-03","Cal Raleigh","SEA",6,105,None),
 ("2026-03","Colt Emerson","SEA",8,95,None),
 # CHC (Hoyer 2020-)
 ("2023-04","Ian Happ","CHC",3,61,None),
 ("2023-04","Nico Hoerner","CHC",3,35,None),
 ("2026-03","Pete Crow-Armstrong","CHC",6,115,None),
 # PIT (Cherington 2019-)
 ("2022-04","Ke'Bryan Hayes","PIT",8,70,None),
 ("2023-04","Bryan Reynolds","PIT",8,106.75,None),
 ("2024-02","Mitch Keller","PIT",5,77,None),
 ("2026-04","Konnor Griffin","PIT",9,140,None),
 # PHI (Dombrowski 2020-)
 ("2024-06","Cristopher Sanchez","PHI",4,22.5,None),
 ("2026-03","Jesus Luzardo","PHI",5,135,None),
 # CIN / DET / MIN / HOU
 ("2023-04","Hunter Greene","CIN",6,53,None),
 ("2024-01","Colt Keith","DET",6,28.6,None),
 ("2021-11","Byron Buxton","MIN",7,100,None),
 ("2024-02","Jose Altuve","HOU",5,125,None),
 # CLE
 ("2017-04","Jose Ramirez","CLE",5,26,None),
 ("2022-04","Jose Ramirez","CLE",7,141,None),
 ("2023-04","Andres Gimenez","CLE",7,106.5,None),
 # NYY (Cashman)
 ("2019-02","Luis Severino","NYY",4,40,None),
 ("2019-02","Aaron Hicks","NYY",7,70,None),
 # BOS (Breslow 2023-)
 ("2024-04","Ceddanne Rafaela","BOS",8,50,None),
 ("2025-04","Garrett Crochet","BOS",6,170,None),
 ("2025-04","Kristian Campbell","BOS",8,60,None),
 ("2025-08","Roman Anthony","BOS",8,130,None),
 # BAL (Elias 2019-)
 ("2025-08","Samuel Basallo","BAL",8,67,None),
 ("2026-03","Shane Baz","BAL",5,68,None),
 # TB
 ("2019-03","Brandon Lowe","TB",6,24,None),
 ("2021-11","Wander Franco","TB",11,182,None),   # seasons capped 2023 in engine (deal voided)
 # ARI (Hazen 2016-)
 ("2018-03","Ketel Marte","ARI",5,24,None),
 ("2023-03","Corbin Carroll","ARI",8,111,None),
 ("2024-04","Ketel Marte","ARI",6,116.5,None),
 # MIL (Arnold window filters)
 ("2023-12","Jackson Chourio","MIL",8,82,None),
 ("2026-03","Cooper Pratt","MIL",8,50,None),
 # ATH (Forst)
 ("2025-01","Brent Rooker","ATH",5,60,None),
 ("2025-03","Lawrence Butler","ATH",7,65.5,None),
 ("2025-12","Tyler Soderstrom","ATH",7,86,None),
 ("2026-02","Jacob Wilson","ATH",7,70,None),
]

# Qualifying-offer signings: (normalized player name, offseason year) whose
# signing club forfeited draft compensation. Confident cases only; re-signing
# your own QO'd player costs nothing and is excluded by construction.
QO = {
 ("jason heyward",2015),("justin upton",2015),
 ("dexter fowler",2016),("ian desmond",2016),
 ("jake arrieta",2017),("alex cobb",2017),("lance lynn",2017),
 ("carlos santana",2017),("eric hosmer",2017),
 ("bryce harper",2018),("patrick corbin",2018),
 ("gerrit cole",2019),("anthony rendon",2019),("hyun jin ryu",2019),
 ("madison bumgarner",2019),
 ("george springer",2020),("trevor bauer",2020),
 ("carlos correa",2021),("marcus semien",2021),("corey seager",2021),
 ("robbie ray",2021),("kevin gausman",2021),("trevor story",2021),
 ("nick castellanos",2021),("eduardo rodriguez",2021),
 ("trea turner",2022),("xander bogaerts",2022),("jacob degrom",2022),
 ("carlos rodon",2022),("dansby swanson",2022),("chris bassitt",2022),
 ("blake snell",2023),("matt chapman",2023),("josh hader",2023),
 ("shohei ohtani",2023),("sonny gray",2023),
 ("juan soto",2024),("corbin burnes",2024),("max fried",2024),
 ("willy adames",2024),("alex bregman",2024),("anthony santander",2024),
 ("christian walker",2024),
 ("kyle tucker",2025),("dylan cease",2025),("bo bichette",2025),
 ("framber valdez",2025),("ranger suarez",2025),("edwin diaz",2025),
}

# CBT/present-value totals for FA deals where deferrals famously diverge
# from nominal: (normalized name, offseason) -> CBT total $M.
# Ohtani: $700M nominal, $46.08M/yr x 10 CBT per MLB's own calculation.
FA_CBT = {("shohei ohtani", 2023): 460.8}
