# Round 42: notes fixed BEFORE the pre-registered rank-threshold run (prereg_rank_threshold.md, r41)
Found before the run (Check C, full join of 41,960 player-team-seasons against Baseball-Reference):
- The r41 spot-check compared single cache ROWS; the cache keeps batting and pitching as separate rows, so a pitcher
  season was split (Phil Hughes 2015: batting row -0.08 + pitching row +0.68 = 0.61, not -0.08). Corrected unit
  here: player-team-season with rows summed. Corrected disagreement: mean +0.05, SD 0.60 (not -0.22 / 0.64).
- Independence: within team-season correlation 0.023 (about independent); a player's consecutive seasons 0.18.
Interpretation choices the prereg left open (fixed now, before results):
1. Unit = player-team-season, stint rows summed (the cache's batting and pitching rows added).
2. Playing time = B-R PA + IPouts for the stint; thirds = tercile cut points of the matched sample.
3. A winter player's third = mean playing time over all his terms; his residual vector (his sample seasons in year
   order, usually one) is cycled over his seasons. This applies one residual to all of a player's seasons, which is
   MORE correlated than the measured 0.18; the decision still uses it, as written.
4. Totals move by sum(coef x residual): trade seats and signings are sums of WAR less costs that do not move with WAR;
   calibration curves held fixed. The term list (build_spec.py) takes each piece's seasons in the receiving club's
   window, as the prereg says; it misses flip returns credited to a club after it trades the piece on, so exposure
   is understated for flip-heavy winters (2012-13 Marlins most of all).
5. Sensitivity reported, not used for any decision: an independent residual for every season (column p_indep).
