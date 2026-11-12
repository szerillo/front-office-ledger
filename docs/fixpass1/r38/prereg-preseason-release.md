# Pre-registration: pre-season release ends the window with the prior season (written Nov 12, before any run)

## Problem
asset_rules.py:362 ends a trade piece's window in the year of a release whatever the month (`end = yy`). A player
released in January to March, before Opening Day, still has that whole season credited to the club that held him,
even when he played it elsewhere (Ryan Sweeney: released by Boston 2013-03-30, his 2013 Cubs season credited to
Boston). A free-agent signing already uses the month (asset_rules.py:363: Jan-Mar ends the prior season).

## Rule (one line, nothing else changes)
`elif ty == "Released": end = min(end, yy - 1 if int(d[5:7]) <= 3 else yy)`

## Expected, from a static estimate on the live build (estimate.py; Ledger WAR of the dropped season, not the
engine's value, so magnitudes are approximate)
- Pieces whose window end changes: exactly the 52 listed in estimate.json (50 present before the Nov 12 deploy,
  2 more from the re-sign rule, both Ryan Sweeney).
- Trade seats that move: 78 (42 by 0.5 wins or more). Largest about 2.0 (a 2014-15 chain through CHC, ATH, HOU, SD).
- Winter tier labels that change: 5, range 3 to 8 (ARI 1999 Bad winter to A wash; WSH 2001 Disaster to Catastrophe;
  ATL 2006 Bad winter to A wash; CWS 2014 Disaster to Catastrophe; HOU 2015 Bad winter to Disaster).
- Best winter: WSH 2014-15 33.9 vs ATH 2011-12 about 33.8 after the fix. Too close to call; no claim either way.
  (Round 37 said Oakland would return to about 34.2; that missed a second pre-season release in Oakland's same winter,
  Josh Outman, 2013, which goes the other way.)
- Clubs named in the Nov 12 note, net seat change summed over all their trades: CHC +1.0, MIL -1.6, PIT -2.0,
  SEA -1.0, SF -0.3, TOR -0.2, WSH -0.1, PHI 0.0. Overall grades that change among them: expected 0 to 2.

## Pass bar (all must hold, or the rule does not ship)
1. The set of pieces whose window end changes equals the 52 keys exactly (0 missing, 0 extra).
2. Every seat that moves 0.5+ in the run moves in the estimated direction; any seat that moves without a listed piece
   is a fail.
3. Two runs of the final engine give one md5 per published file (determinism bar as for fix pass 1).
4. All suites, t_grades (regenerated with REASON), letters census and offs_stamps run; every changed tier label and
   every changed overall grade traces to a listed piece.
5. Note-style check: if any overall grade of a note club changes, the Nov 12 corrections page gets an addendum
   before deploy.
Deploy needs a separate go.
