"""The 2026-27 winter as it actually happened (v5.2 reality pass, Nov 1-2 2026).

Sources: the MLB.com 2027 options and opt-outs tracker (fetched Nov 1), the
league transaction feed (every "elected free agency" filing since Oct 1),
and per-player contract reporting gathered for the 138 six-year veterans the
feed did not list (vet_status.json, each row carries its source URL).

Codes the page reads (DESK.status[pid] = [code, text]):
  fa      a free agent this winter (filed, option declined, opted out, released)
  out     not available: retired, or on the restricted list
  posted  posted by an NPB or KBO club; signs as a free agent with a posting fee
  pendfa  a decision is still open and the Ledger models him as a free agent
  pendin  a decision is still open and the Ledger models him as staying
  ctr     under contract for 2027 by a deal the base contract book lacks
Every option still open on Nov 1 is due on Nov 2 (five days after the World
Series); a scheduled refresh rewrites these rows once the decisions post.
"""

# 2027 terms on file that the base contract book does not carry, as
# (name, club, first season, last season, AAV $M, label). Coverage starts in
# 2027; AAV is the payroll figure the pack uses for every contract.
CONTRACTS = [
    ("Chris Sale", "ATL", 2027, 2027, 27.0, "1 yr / $27M extension (2028 club option $30M)"),
    ("Nico Hoerner", "CHC", 2027, 2032, 23.5, "6 yr / $141M extension, 2027-32"),
    ("Max Muncy", "LAD", 2027, 2027, 10.0, "extension: $10M guaranteed for 2027 (2028 club option)"),
    ("Seth Lugo", "KC", 2027, 2027, 23.0, "final guaranteed year of his extension (2028 vesting option)"),
    ("Aroldis Chapman", "BOS", 2027, 2027, 13.0, "2027 option vested at $13M"),
    ("Salvador Perez", "KC", 2027, 2027, 12.5, "2 yr / $25M, 2026-27"),
    ("Victor Caratini", "MIN", 2027, 2027, 7.0, "2 yr / $14M, 2026-27"),
    ("Willi Castro", "COL", 2027, 2027, 6.4, "2 yr / $12.8M, 2026-27"),
    ("Ryan McMahon", "NYY", 2027, 2027, 10.0, "final year of 7 yr / $70M"),
    ("Reynaldo López", "ATL", 2027, 2027, 10.0, "2027 guaranteed in his restructure"),
    ("Luis Torrens", "NYM", 2027, 2028, 5.75, "2 yr / $11.5M extension, 2027-28"),
    ("Luis Castillo", "CWS", 2027, 2027, 21.6, "final guaranteed year (2028 vesting option)"),
    ("Danny Jansen", "TEX", 2027, 2027, 7.25, "final guaranteed year (2028 mutual option)"),
    ("Giancarlo Stanton", "NYY", 2027, 2027, 25.0, "final guaranteed year (Miami pays $10M of it)"),
    ("Adrian Houser", "SF", 2027, 2027, 11.0, "2 yr / $22M, 2026-27"),
    ("Phil Maton", "CHC", 2027, 2027, 7.25, "2 yr / $14.5M, 2026-27"),
    ("Jose Trevino", "CIN", 2027, 2027, 5.75, "2 yr / $11.5M, 2026-27"),
    ("Kyle Finnegan", "DET", 2027, 2027, 9.5, "2 yr / $19M, 2026-27"),
    ("Tim Mayza", "PHI", 2027, 2027, 2.75, "re-signed Oct 15: 1 yr / $2.75M"),
    ("Jordan Hicks", "CWS", 2027, 2027, 11.0, "final year of 4 yr / $44M"),
    ("Seranthony Domínguez", "SEA", 2027, 2027, 10.0, "2 yr / $20M, 2026-27"),
    ("Steven Matz", "TB", 2027, 2027, 7.5, "2 yr / $15M, 2026-27"),
    ("Shelby Miller", "CHC", 2027, 2027, 1.25, "2 yr / $2.5M, 2026-27"),
    ("Cristian Javier", "HOU", 2027, 2027, 12.8, "final year of 5 yr / $64M"),
    ("Yuki Matsui", "SD", 2027, 2028, 5.6, "5 yr / $28M, 2024-28 (opt-out decision due Nov 2)"),
    ("Peter Lambert", "HOU", 2027, 2027, 4.6, "final arbitration year (public projection $4.6M)"),
    # options already exercised (club) or opted into (player)
    ("Ronald Acuña Jr.", "ATL", 2027, 2027, 17.0, "2027 club option exercised ($17M)"),
    ("Drew Rasmussen", "TB", 2027, 2027, 20.0, "2027 club option exercised ($20M after escalators)"),
    ("Wandy Peralta", "SD", 2027, 2027, 4.45, "2027 player option exercised ($4.45M)"),
]

# known free agents beyond the feed's filings: option declined, opted out,
# released. (Declared filings come from the feed itself.)
FA = {
    "Clay Holmes": "declined his $12M player option",
    "Michael King": "opted out of his Padres deal",
    "Emilio Pagán": "declined his $10M player option",
    "Nick Pivetta": "Padres declined his $14M club option",
    "Carlos Estévez": "Royals declined his $13M club option",
    "Jeff McNeil": "Athletics declined his $15.75M club option",
    "Luis Robert Jr.": "Orioles declined his $20M club option",
    "Victor Robles": "Mariners declined his $9M club option",
    "Jeffrey Springs": "Athletics declined his $15M club option",
    "Trevor Stephan": "Guardians declined his $7.25M club option",
    "Robert Stephenson": "Angels declined his $2.5M club option",
    "Ryan Weiss": "Astros declined his $5M club option",
    "Shawn Armstrong": "mutual option declined", "Matthew Boyd": "mutual option declined",
    "Josh Bell": "mutual option declined", "Zach Eflin": "mutual option declined",
    "Sonny Gray": "mutual option declined", "Kyle Higashioka": "mutual option declined",
    "Pierce Johnson": "mutual option declined", "Jakob Junis": "mutual option declined",
    "Carson Kelly": "mutual option declined", "Nick Martinez": "mutual option declined",
    "Dustin May": "mutual option declined", "Cedric Mullins": "mutual option declined",
    "Joc Pederson": "mutual option declined", "Michael Soroka": "mutual option declined",
    "Eugenio Suárez": "mutual option declined",
    "J.P. Crawford": "contract complete (filed for free agency)",
    "Shota Imanaga": "contract complete (filed for free agency)",
    "Seiya Suzuki": "contract complete (filed for free agency)",
}
# a club option the Mariners declined still leaves a pre-arbitration
# player under club control: not a free agent
CONTROLLED_AFTER_DECLINE = {"Bryce Miller"}

OUT = {
    "Emmanuel Clase": "on the restricted list (federal indictment); his $10M club option is moot",
    "Clayton Kershaw": "retired", "David Robertson": "retired", "Jacob Stallings": "retired",
    "Kyle Gibson": "retired", "Andrew Heaney": "retired", "Charlie Blackmon": "retired",
    "Jason Heyward": "retired", "Ross Stripling": "retired", "Chad Green": "retired",
    "Lance Lynn": "retired", "Kyle Hendricks": "retired", "Jesse Chavez": "retired",
    "Adam Ottavino": "retired", "Jon Berti": "retired", "Gio Urshela": "retired",
}

# open on Nov 1, due Nov 2: (name, kind, $M, buyout $M). Club options are
# modeled by the club's own arithmetic: exercised when the projected 2027
# value at $10M per win clears the option net of the buyout. Mutual options
# are modeled declined (both sides almost never say yes). Player options and
# opt-outs are modeled as the player staying unless his market clearly beats
# the remaining money (none of the open ones do).
PENDING = [
    ("William Contreras", "club", 15.5, 0.0), ("Isaac Paredes", "club", 13.35, 0.0),
    ("Garrett Whitlock", "club", 8.25, 1.0), ("Kenley Jansen", "club", 12.0, 2.0),
    ("Ryan Mountcastle", "club", 7.5, 0.0), ("Colin Rea", "club", 7.5, 1.0),
    ("Antonio Senzatela", "club", 14.0, 0.0), ("Ryne Stanek", "club", 6.0, 1.0),
    ("Myles Straw", "club", 8.0, 1.75), ("Jacob Webb", "club", 2.5, 0.0),
    ("Taylor Walls", "club", 3.1, 0.0), ("Javier Assad", "club", 3.3, 0.0),
    ("Drew Anderson", "club", 10.0, 0.0), ("Dietrich Enns", "club", 3.5, 0.125),
    ("Kyle Hart", "club", 2.5, 0.2),
    ("Miguel Andujar", "mutual", 8.0, 2.5), ("Griffin Canning", "mutual", 5.0, 1.5),
    ("Lucas Giolito", "mutual", 8.0, 1.5), ("Hunter Harvey", "mutual", 8.0, 1.0),
    ("Gary Sánchez", "mutual", 1.75, 0.25), ("Caleb Thielbar", "mutual", 6.0, 0.5),
    ("Joe Ryan", "mutual", 0.0, 0.0),
    ("José Berríos", "player", 0.0, 0.0), ("Luis Severino", "player", 22.0, 0.0),
    ("Yuki Matsui", "player", 0.0, 0.0),
]

# posted players: (mlbam id, display club, league, signing deadline text)
POSTED = {
    831664: ("Hanshin Tigers", "NPB", "Dec 16, 5pm ET (45-day window; pauses if a lockout starts Dec 1)"),
    838343: ("Saitama Seibu Lions", "NPB", "Dec 16, 5pm ET (45-day window; pauses if a lockout starts Dec 1)"),
    808955: ("Hokkaido Nippon-Ham Fighters", "NPB", "Dec 16, 5pm ET (45-day window; pauses if a lockout starts Dec 1)"),
    823574: ("Hanwha Eagles", "KBO", "Dec 1, 5pm ET (30-day window)"),
}

# a player who has received a qualifying offer before can never receive
# another (2022 CBA). This class's QO-caliber names with one on record:
PRIOR_QO = {
    "Michael King": "SD, 2025", "Sonny Gray": "MIN, 2023", "Luis Severino": "NYM, 2024",
    "Nick Pivetta": "BOS, 2024", "Kevin Gausman": "SF, 2020 (accepted)", "Robbie Ray": "TOR, 2021",
    "Chris Bassitt": "NYM, 2022", "George Springer": "HOU, 2020", "Kenley Jansen": "LAD, 2016",
    "Shota Imanaga": "CHC, 2025 (accepted)", "Trent Grisham": "NYY, 2025 (accepted)",
    "Gleyber Torres": "DET, 2025 (accepted)", "Brandon Woodruff": "MIL, 2025 (accepted)",
}
