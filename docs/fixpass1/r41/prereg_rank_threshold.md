# Pre-registration (not run): how close is "too close to rank" for winter totals
Written Nov 12 2026 before any of the steps below were run. Replaces the 0.5-win gap used in round 40, which was a
judgment (display rounding of 0.1 plus single model choices moving a total 0.3 to 0.5), not a measured error.

1. Disagreement sample. 300 Ledger player-seasons, 1998 to 2026, drawn with seed 20261150 from lvm_cache.json
   (the cache in use on the day of the run, md5 recorded). Reference: Baseball-Reference WAR from its public daily
   WAR files (batting + pitching WAR per stint, matched on mlb_ID), file date recorded. Residual = Ledger - bWAR.
   Report mean and SD overall and by playing-time third.
2. Simulation. For every settled winter, list the player-seasons behind its total (each trade piece's seasons in
   the club's window and each signing's seasons). 2,000 draws: each player gets one residual vector resampled from
   a sample player in the same playing-time third (keeps a player's seasons correlated), added to his Ledger WAR;
   totals recomputed with the production formula.
3. Rule. A winter's rank is shown only if it finishes ahead of the next winter in at least 90% of draws; otherwise
   the pair reads "too close to rank". Also report the gap at which the flip rate crosses 10% (median over pairs).
4. Fixed in advance: the 90% level, the seed, the sample size and the resampling unit. The result is reported even
   if it makes most published ranks "too close". bWAR is not truth: residuals mix our data errors with honest
   model differences, so this sets an upper-side threshold, said so wherever it is used.
