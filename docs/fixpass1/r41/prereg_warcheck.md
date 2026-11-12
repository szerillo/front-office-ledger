# WAR spot-check, pre-registered 2026-11-12T12:59:00Z (before any outside WAR was fetched)
Sample: sample.json (10 largest rows added at the last cache refresh 46ddec3 to 0a9f2bd, which changed 0 existing values
and added 163 rows; plus 10 random 1998+ rows, seed 20261141).
Reference: Baseball-Reference WAR (bWAR) from its public daily WAR files (war_daily_bat.txt + war_daily_pitch.txt),
version = the file date. Player-team-season WAR = batting WAR + pitching WAR for that stint, matched on mlb_ID.
Ledger WAR is our own build (own run values, parks, replacement level), so it is not expected to equal bWAR.
A row FAILS if any of:
 (a) team: Baseball-Reference has no stint for that player, season and club;
 (b) size: |Ledger - bWAR| > 1.0 win;
 (c) sign: opposite signs with both values at least 0.5 in size.
Why 1.0: chosen before looking, not measured. Most rows here are part-time seasons where two WAR systems should
land within a win; a gap past that, or a wrong club, is where a data error (wrong player, wrong club, missed stint)
would show. Measuring the real disagreement is the job of the check in B.
