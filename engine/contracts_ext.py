"""Curated major contract extensions, materiality-first, limited to deals
signed inside CURRENT regime windows (the window filter in ext_grade.py
excludes anything else automatically). Terms are guaranteed totals from
contemporaneous public reporting; the 2025-26 wave was verified by web
search this session (Basallo, Anthony, Baz, Emerson, Griffin, PCA, Luzardo,
Soderstrom, Wilson, Pratt confirmed against ESPN/MLB.com/CBS/Banner
reports). cbt_m: CBT/present-value total where deferrals famously diverge
from nominal (Betts ~$306.7M PV of $365M). Format:
(sign "YYYY-MM", player, team abbr, years, total $M, cbt $M or None
[, first covered season when it differs from the default: a deal signed by
March covers that season, a later one starts the next]).
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
    ('2023-12', 'Tyler Glasnow', 'LAD', 4, 110.0, None, 2025),  # 4 yr / $110M added on top of his 2024 salary: covers 2025-2028
    # ---- 2027 club options exercised or plainly in-the-money (the 2026-27
    # winter reality pass; sources: the league option tracker, Nov 2026).
    # Encoded as one-year coverage at the option price.
    ('2026-11', 'William Contreras', 'MIL', 1, 14.5, None),
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
 # LAD (Friedman 2014-)
 ("2020-07","Mookie Betts","LAD",12,365,306.7),
 ("2024-03","Will Smith","LAD",10,140,None),
 ("2025-01","Tommy Edman","LAD",5,74,None),
 # TOR (Atkins 2015-)
 ("2021-11","Jose Berrios","TOR",7,131,None),
 ("2025-03","Alejandro Kirk","TOR",5,58,None),
 ("2025-04","Vladimir Guerrero Jr.","TOR",14,500,None),
 # ATL (Anthopoulos 2017-)
 ("2019-04","Ronald Acuna Jr.","ATL",8,100,None, 2019),
 ("2019-04","Ozzie Albies","ATL",7,35,None, 2019),
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
 ("2025-04","Jackson Merrill","SD",9,135,None, 2025),
 # KC (current regime)
 ("2024-02","Bobby Witt Jr.","KC",11,288.7,None),
 # SEA (Dipoto 2015-)
 ("2019-11","Evan White","SEA",6,24,None),
 ("2022-04","J.P. Crawford","SEA",5,51,None, 2022),
 ("2022-08","Julio Rodriguez","SEA",12,209.3,None),
 ("2025-03","Cal Raleigh","SEA",6,105,None),
 ("2026-03","Colt Emerson","SEA",8,95,None),
 # CHC (Hoyer 2020-)
 ("2023-04","Ian Happ","CHC",3,61,None),
 ("2023-04","Nico Hoerner","CHC",3,35,None),
 ("2026-03","Pete Crow-Armstrong","CHC",6,115,None),
 # PIT (Cherington 2019-)
 ("2022-04","Ke'Bryan Hayes","PIT",8,70,None, 2022),
 ("2023-04","Bryan Reynolds","PIT",8,106.75,None, 2023),
 ("2024-02","Mitch Keller","PIT",5,77,None),
 ("2026-04","Konnor Griffin","PIT",9,140,None, 2026),
 # PHI (Dombrowski 2020-)
 ("2024-06","Cristopher Sanchez","PHI",4,22.5,None),
 ("2026-03","Jesus Luzardo","PHI",5,135,None),
 # CIN / DET / MIN / HOU
 ("2023-04","Hunter Greene","CIN",6,53,None, 2023),
 ("2024-01","Colt Keith","DET",6,28.6,None),
 ("2021-11","Byron Buxton","MIN",7,100,None),
 ("2024-02","Jose Altuve","HOU",5,125,None, 2025),
 # CLE
 ("2017-04","Jose Ramirez","CLE",5,26,None, 2017),
 ("2022-04","Jose Ramirez","CLE",7,141,None, 2022),
 ("2023-04","Andres Gimenez","CLE",7,106.5,None),
 # NYY (Cashman)
 ("2019-02","Luis Severino","NYY",4,40,None),
 ("2019-02","Aaron Hicks","NYY",7,70,None),
 # BOS (Breslow 2023-)
 ("2024-04","Ceddanne Rafaela","BOS",8,50,None,2024),   # in-season deal that starts that season
 ("2025-04","Garrett Crochet","BOS",6,170,None),
 ("2025-04","Kristian Campbell","BOS",8,60,None,2025),
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
 ("2025-04","Ketel Marte","ARI",6,116.5,None),     # signed April 2025, covers 2026-31
 # coverage audit v5.4 (pre-regime deals carried for payroll and control)
 ("2024-03","Ezequiel Tovar","COL",7,63.5,None),    # 2024-2030
 ("2024-03","Brayan Bello","BOS",6,55,None),        # 2024-2029
 # MIL (Arnold window filters)
 ("2023-12","Jackson Chourio","MIL",8,82,None),
 ("2026-03","Cooper Pratt","MIL",8,50.75,None),
 # ATH (Forst)
 ("2025-01","Brent Rooker","ATH",5,60,None),
 ("2025-03","Lawrence Butler","ATH",7,65.5,None),
 ("2025-12","Tyler Soderstrom","ATH",7,86,None),
 ("2026-02","Jacob Wilson","ATH",7,70,None),
    # ---- v5.7: the full extension book, 2015-2026 (MLB Trade Rumors'
    # extension tracker through Jul 2022, then deal-by-deal reports; headline
    # guaranteed terms). First covered season: a deal through March covers that
    # season; April-June covers it for players within 3 seasons of debut;
    # otherwise the next season.
    ("2015-01", "Lance Lynn", "STL", 3, 22.0, None, 2015),
    ("2015-01", "Gregor Blanco", "SF", 2, 7.5, None, 2015),
    ("2015-01", "Devin Mesoraco", "CIN", 4, 28.0, None, 2015),
    ("2015-02", "Wade Miley", "BOS", 3, 19.25, None, 2015),
    ("2015-02", "Mike Dunn", "MIA", 2, 5.8, None, 2015),
    ("2015-02", "Todd Frazier", "CIN", 2, 12.0, None, 2015),
    ("2015-02", "Jon Jay", "STL", 2, 10.975, None, 2015),
    ("2015-02", "Kelvin Herrera", "KC", 2, 4.15, None, 2015),
    ("2015-02", "Eric Hosmer", "KC", 2, 13.9, None, 2015),
    ("2015-03", "Christian Yelich", "MIA", 7, 49.57, None, 2015),
    ("2015-03", "Adam Eaton", "CWS", 5, 23.5, None, 2015),
    ("2015-03", "Brian Dozier", "MIN", 4, 20.0, None, 2015),
    ("2015-04", "Juan Lagares", "NYM", 4, 23.0, None, 2015),
    ("2015-04", "Yordano Ventura", "KC", 5, 23.0, None, 2015),
    ("2015-04", "Carlos Carrasco", "CLE", 4, 22.0, None, 2016),
    ("2015-04", "Corey Kluber", "CLE", 5, 38.5, None, 2016),
    ("2015-04", "Rick Porcello", "BOS", 4, 82.5, None, 2016),
    ("2015-04", "Josh Harrison", "PIT", 4, 27.3, None, 2016),
    ("2015-05", "Huston Street", "LAA", 2, 18.0, None, 2016),
    ("2015-11", "Brandon Crawford", "SF", 6, 75.0, None, 2016),
    ("2015-12", "Nate Jones", "CWS", 3, 8.0, None, 2016),
    ("2016-01", "Adam Ottavino", "COL", 3, 10.4, None, 2016),
    ("2016-01", "Dee Gordon", "MIA", 5, 50.0, None, 2016),
    ("2016-01", "Logan Forsythe", "TB", 2, 10.25, None, 2016),
    ("2016-01", "Lorenzo Cain", "KC", 2, 17.5, None, 2016),
    ("2016-01", "Chris Stewart", "PIT", 2, 3.0, None, 2016),
    ("2016-01", "Josh Tomlin", "CLE", 2, 5.5, None, 2016),
    ("2016-02", "A.J. Pollock", "ARI", 2, 10.25, None, 2016),
    ("2016-02", "Josh Donaldson", "TOR", 2, 28.65, None, 2016),
    ("2016-02", "J.D. Martinez", "DET", 2, 18.5, None, 2016),
    ("2016-02", "Mike Moustakas", "KC", 2, 14.3, None, 2016),
    ("2016-02", "DJ LeMahieu", "COL", 2, 7.8, None, 2016),
    ("2016-03", "Salvador Pérez", "KC", 5, 52.5, None, 2016),
    ("2016-03", "Kolten Wong", "STL", 5, 25.5, None, 2016),
    ("2016-04", "Gregory Polanco", "PIT", 5, 35.0, None, 2016),
    ("2016-04", "Brandon Belt", "SF", 5, 72.8, None, 2017),
    ("2016-04", "Adrián Beltré", "TEX", 2, 36.0, None, 2017),
    ("2016-05", "Stephen Strasburg", "WSH", 7, 175.0, None, 2017),
    ("2016-05", "Francisco Cervelli", "PIT", 3, 31.0, None, 2017),
    ("2016-07", "Justin Smoak", "TOR", 2, 8.25, None, 2017),
    ("2016-08", "David Freese", "PIT", 2, 11.0, None, 2017),
    ("2016-10", "Jim Johnson", "ATL", 2, 10.0, None, 2017),
    ("2016-10", "Martín Prado", "MIA", 3, 40.0, None, 2017),
    ("2016-12", "Odúbel Herrera", "PHI", 5, 30.5, None, 2017),
    ("2016-12", "Ender Inciarte", "ATL", 5, 30.525, None, 2017),
    ("2017-01", "Yangervis Solarte", "SD", 2, 7.5, None, 2017),
    ("2017-01", "Nolan Arenado", "COL", 2, 29.5, None, 2017),
    ("2017-01", "Danny Duffy", "KC", 5, 65.0, None, 2017),
    ("2017-01", "Wil Myers", "SD", 6, 83.0, None, 2017),
    ("2017-01", "Kole Calhoun", "LAA", 3, 26.0, None, 2017),
    ("2017-01", "Brandon Guyer", "CLE", 2, 5.0, None, 2017),
    ("2017-02", "Carlos Martínez", "STL", 5, 51.0, None, 2017),
    ("2017-02", "Will Harris", "HOU", 2, 5.0, None, 2017),
    ("2017-02", "Pedro Strop", "CHC", 2, 11.85, None, 2017),
    ("2017-03", "Kevin Kiermaier", "TB", 6, 53.5, None, 2017),
    ("2017-03", "Tim Anderson", "CWS", 6, 25.0, None, 2017),
    ("2017-03", "Rougned Odor", "TEX", 6, 49.5, None, 2017),
    ("2017-04", "Roberto Pérez", "CLE", 4, 9.0, None, 2017),
    ("2017-04", "Yadier Molina", "STL", 3, 60.0, None, 2018),
    ("2017-04", "Stephen Piscotty", "STL", 6, 33.5, None, 2017),
    ("2017-06", "Jean Segura", "SEA", 5, 70.0, None, 2018),
    ("2017-09", "Clayton Richard", "SD", 2, 6.0, None, 2018),
    ("2017-09", "Marco Estrada", "TOR", 1, 13.0, None, 2018),
    ("2017-09", "Tucker Barnhart", "CIN", 4, 16.0, None, 2018),
    ("2017-10", "Chase Anderson", "MIL", 2, 11.75, None, 2018),
    ("2017-11", "Justin Upton", "LAA", 5, 106.0, None, 2018),
    ("2017-12", "Dan Otero", "CLE", 2, 2.5, None, 2018),
    ("2018-01", "Brad Hand", "SD", 3, 19.75, None, 2018),
    ("2018-01", "Felipe Vázquez", "PIT", 4, 22.0, None, 2018),
    ("2018-02", "George Springer", "HOU", 2, 24.0, None, 2018),
    ("2018-03", "Paul DeJong", "STL", 6, 26.0, None, 2018),
    ("2018-03", "José Altuve", "HOU", 5, 151.0, None, 2020),
    ("2018-03", "Eugenio Suárez", "CIN", 7, 66.0, None, 2018),
    ("2018-03", "Christian Vázquez", "BOS", 3, 13.55, None, 2018),
    ("2018-03", "Scott Kingery", "PHI", 6, 24.0, None, 2018),
    ("2018-04", "Charlie Blackmon", "COL", 6, 108.0, None, 2019),
    ("2018-10", "Eduardo Escobar", "ARI", 3, 21.0, None, 2019),
    ("2018-11", "Clayton Kershaw", "LAD", 3, 93.0, None, 2019),
    ("2018-11", "Raisel Iglesias", "CIN", 3, 24.125, None, 2019),
    ("2018-12", "Carlos Carrasco", "CLE", 4, 47.0, None, 2019),
    ("2019-01", "Sonny Gray", "CIN", 3, 30.5, None, 2019),
    ("2019-01", "Whit Merrifield", "KC", 4, 16.25, None, 2019),
    ("2019-02", "Aaron Nola", "PHI", 4, 45.0, None, 2019),
    ("2019-02", "Jorge Polanco", "MIN", 5, 25.75, None, 2019),
    ("2019-02", "Max Kepler", "MIN", 5, 35.0, None, 2019),
    ("2019-02", "José Martínez", "STL", 2, 3.25, None, 2019),
    ("2019-02", "Miles Mikolas", "STL", 4, 68.0, None, 2019),
    ("2019-03", "José Leclerc", "TEX", 4, 14.75, None, 2019),
    ("2019-03", "Alex Bregman", "HOU", 5, 100.0, None, 2019),
    ("2019-03", "Ryan Pressly", "HOU", 2, 17.5, None, 2019),
    ("2019-03", "Eloy Jiménez", "CWS", 6, 43.0, None, 2019),
    ("2019-03", "Blake Snell", "TB", 5, 50.0, None, 2019),
    ("2019-03", "Chris Sale", "BOS", 5, 145.0, None, 2020),
    ("2019-03", "Paul Goldschmidt", "STL", 5, 130.0, None, 2020),
    ("2019-03", "Justin Verlander", "HOU", 2, 66.0, None, 2020),
    ("2019-03", "Kyle Hendricks", "CHC", 4, 55.5, None, 2019),
    ("2019-03", "Jacob deGrom", "NYM", 5, 137.5, None, 2019),
    ("2019-04", "Xander Bogaerts", "BOS", 6, 120.0, None, 2020),
    ("2019-04", "Randal Grichuk", "TOR", 5, 52.0, None, 2020),
    ("2019-04", "Germán Márquez", "COL", 5, 43.0, None, 2019),
    ("2019-04", "David Bote", "CHC", 5, 15.0, None, 2019),
    ("2019-04", "Matt Carpenter", "STL", 2, 39.0, None, 2020),
    ("2019-04", "Khris Davis", "ATH", 2, 33.5, None, 2020),
    ("2019-09", "Miguel Rojas", "MIA", 2, 10.25, None, 2020),
    ("2019-11", "Aroldis Chapman", "NYY", 3, 48.0, None, 2020),
    ("2019-12", "Scott Oberg", "COL", 3, 13.0, None, 2020),
    ("2020-01", "Luis Robert", "CWS", 6, 50.0, None, 2020),
    ("2020-01", "David Peralta", "ARI", 3, 22.0, None, 2020),
    ("2020-01", "Miguel Sanó", "MIN", 3, 30.0, None, 2020),
    ("2020-01", "Trevor Story", "COL", 2, 27.5, None, 2020),
    ("2020-02", "Marco Gonzales", "SEA", 4, 30.0, None, 2020),
    ("2020-02", "Max Muncy", "LAD", 3, 26.0, None, 2020),
    ("2020-02", "Chris Taylor", "LAD", 2, 13.4, None, 2020),
    ("2020-02", "Andrew Benintendi", "BOS", 2, 10.0, None, 2020),
    ("2020-02", "Nick Ahmed", "ARI", 4, 32.5, None, 2020),
    ("2020-02", "Brent Suter", "MIL", 2, 2.5, None, 2020),
    ("2020-02", "Aaron Bummer", "CWS", 5, 16.0, None, 2020),
    ("2020-02", "Freddy Peralta", "MIL", 5, 15.5, None, 2020),
    ("2020-03", "Yoán Moncada", "CWS", 5, 70.0, None, 2020),
    ("2020-11", "Mike Clevinger", "SD", 2, 11.5, None, 2021),
    ("2021-02", "Shohei Ohtani", "LAA", 2, 8.5, None, 2021),
    ("2021-02", "Walker Buehler", "LAD", 2, 8.0, None, 2021),
    ("2021-02", "Austin Barnes", "LAD", 2, 4.3, None, 2021),
    ("2021-03", "Hunter Dozier", "KC", 4, 25.0, None, 2021),
    ("2021-03", "Salvador Pérez", "KC", 4, 82.0, None, 2021),
    ("2021-03", "Lance McCullers Jr.", "HOU", 5, 85.0, None, 2021),
    ("2021-03", "Randy Dobnak", "MIN", 5, 9.25, None, 2021),
    ("2021-04", "David Fletcher", "LAA", 5, 26.0, None, 2021),
    ("2021-07", "Matt Barnes", "BOS", 2, 18.75, None, 2022),
    ("2021-07", "Lance Lynn", "CWS", 2, 38.0, None, 2022),
    ("2021-08", "Jonathan Schoop", "DET", 2, 15.0, None, 2022),
    ("2021-08", "Brandon Crawford", "SF", 2, 32.0, None, 2022),
    ("2021-08", "Travis d'Arnaud", "ATL", 2, 16.0, None, 2022),
    ("2021-08", "Yadier Molina", "STL", 1, 10.0, None, 2022),
    ("2021-09", "Charlie Morton", "ATL", 1, 20.0, None, 2022),
    ("2021-09", "Michael A. Taylor", "KC", 2, 9.0, None, 2022),
    ("2021-10", "Adam Wainwright", "STL", 1, 17.5, None, 2022),
    ("2021-10", "Antonio Senzatela", "COL", 5, 50.5, None, 2022),
    ("2021-10", "C.J. Cron", "COL", 2, 14.5, None, 2022),
    ("2021-10", "Miguel Rojas", "MIA", 2, 10.0, None, 2022),
    ("2021-11", "Elias Díaz", "COL", 3, 14.5, None, 2022),
    ("2021-11", "Sandy Alcantara", "MIA", 5, 56.0, None, 2022),
    ("2021-11", "Orlando Arcia", "ATL", 2, 3.0, None, 2022),
    ("2021-12", "Andrés Muñoz", "SEA", 4, 7.5, None, 2022),
    ("2022-03", "Richard Bleier", "MIA", 2, 6.0, None, 2022),
    ("2022-03", "Ryan McMahon", "COL", 6, 70.0, None, 2022),
    ("2022-03", "Darin Ruf", "SF", 2, 6.25, None, 2022),
    ("2022-03", "Matt Chapman", "TOR", 2, 25.0, None, 2022),
    ("2022-03", "Max Stassi", "LAA", 3, 17.5, None, 2022),
    ("2022-03", "Ketel Marte", "ARI", 5, 76.0, None, 2022),
    ("2022-04", "Merrill Kelly", "ARI", 2, 18.0, None, 2022),
    ("2022-04", "Harrison Bader", "STL", 2, 10.4, None, 2023),
    ("2022-04", "Emmanuel Clase", "CLE", 5, 20.0, None, 2022),
    ("2022-04", "Ryan Pressly", "HOU", 2, 30.0, None, 2023),
    ("2022-04", "Manuel Margot", "TB", 2, 19.0, None, 2023),
    ("2022-04", "Myles Straw", "CLE", 5, 25.0, None, 2023),
    ("2022-04", "Garrett Whitlock", "BOS", 4, 18.75, None, 2022),
    ("2022-04", "Kyle Freeland", "COL", 5, 64.5, None, 2023),
    ("2022-05", "John Means", "BAL", 2, 5.925, None, 2023),
    ("2022-06", "Jesse Winker", "SEA", 2, 14.5, None, 2023),
    ("2022-07", "Austin Barnes", "LAD", 2, 7.0, None, 2023),
    ("2022-07", "Aaron Ashby", "MIL", 5, 20.5, None, 2023),
    ("2022-07", "Daniel Bard", "COL", 2, 19.0, None, 2023),
    ("2022-08", "Tyler Glasnow", "TB", 2, 30.35, None, 2023),
    ("2022-08", "Max Muncy", "LAD", 1, 13.5, None, 2023),
    ("2022-09", "Luis Castillo", "SEA", 5, 108.0, None, 2023),
    ("2022-11", "Tyler Kinley", "COL", 3, 6.25, None, 2023),
    ("2022-11", "Tyler Matzek", "ATL", 2, 3.1, None, 2023),
    ("2023-01", "Jeff McNeil", "NYM", 4, 50.0, None, 2023),
    ("2023-01", "Tony Gonsolin", "LAD", 2, 6.65, None, 2023),
    ("2023-01", "Yandy Díaz", "TB", 3, 24.0, None, 2023),
    ("2023-01", "Pete Fairbanks", "TB", 3, 12.0, None, 2023),
    ("2023-01", "Jeffrey Springs", "TB", 4, 31.0, None, 2023),
    ("2023-01", "Dylan Moore", "SEA", 3, 8.875, None, 2023),
    ("2023-02", "Cristian Javier", "HOU", 5, 64.0, None, 2023),
    ("2023-11", "Max Muncy", "LAD", 2, 24.0, None, 2024),
    ("2024-01", "Shane McClanahan", "TB", 2, 7.2, None, 2024),
    ("2024-08", "Víctor Robles", "SEA", 2, 9.75, None, 2025),
    ("2024-11", "Michael Wacha", "KC", 3, 51.0, None, 2025),
    ("2025-01", "Drew Rasmussen", "TB", 2, 8.5, None, 2025),
    ("2025-02", "Cole Ragans", "KC", 3, 13.25, None, 2025),
    ("2025-03", "Tanner Bibee", "CLE", 5, 48.0, None, 2025),
    ("2025-03", "Justin Martínez", "ARI", 5, 18.0, None, 2025),
    ("2025-03", "Brandon Pfaadt", "ARI", 5, 45.0, None, 2025),
    ("2025-07", "Seth Lugo", "KC", 2, 46.0, None, 2026),
    ("2025-08", "Aroldis Chapman", "BOS", 1, 13.3, None, 2026),
    ("2025-11", "Salvador Pérez", "KC", 2, 25.0, None, 2026),
    ("2025-12", "Maikel Garcia", "KC", 5, 57.5, None, 2026),
    ("2026-01", "José Ramírez", "CLE", 7, 175.0, None, 2026),
    ("2026-02", "Max Muncy", "LAD", 1, 10.0, None, 2026),
    ("2026-02", "Chris Sale", "ATL", 1, 27.0, None, 2026),
    ("2026-03", "Cristopher Sánchez", "PHI", 6, 107.0, None, 2026),
    ("2026-03", "Nico Hoerner", "CHC", 6, 141.0, None, 2026),
    ("2026-04", "Kevin McGonigle", "DET", 8, 150.0, None, 2026),
    ("2026-05", "Luis Torrens", "NYM", 2, 11.5, None, 2027),
    ("2026-06", "Luis Lara", "MIL", 7, 31.0, None, 2026),
    ("2026-07", "JJ Wetherholt", "STL", 8, 112.5, None, 2027),
    ("2026-07", "Chase Burns", "CIN", 7, 105.0, None, 2027),
    ("2026-07", "Kyle Bradish", "BAL", 5, 90.0, None, 2027),
    ("2026-07", "Yennier Cano", "BAL", 2, 7.5, None, 2027),
    ("2026-08", "Mickey Moniak", "COL", 2, 16.25, None, 2027),
    ("2026-09", "Cade Cavalli", "WSH", 4, 47.0, None, 2027),
    ("2022-04", "Bryan Reynolds", "PIT", 2, 13.5, None, 2022),
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
 ("christian walker",2024),("nick pivetta",2024),("luis severino",2024),
 ("kyle tucker",2025),("dylan cease",2025),("bo bichette",2025),
 ("framber valdez",2025),("ranger suarez",2025),("edwin diaz",2025),
}

# CBT/present-value totals for FA deals where deferrals famously diverge
# from nominal: (normalized name, offseason) -> CBT total $M.
# Ohtani: $700M nominal, $46.08M/yr x 10 CBT per MLB's own calculation.
FA_CBT = {("shohei ohtani", 2023): 460.8}
