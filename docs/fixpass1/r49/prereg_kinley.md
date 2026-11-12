# Prereg (round 49): re-signings filed as "assigned to <MLB club>" after electing free agency

Written Nov 12, 2026. Prereg only: no build, no lookup of the test sample, no run. Build needs a separate GO.

## Problem
Round 48's rule takes a player off the roster when he elects free agency (feed code DFA, "elected free agency").
Counter-example found in the dry run: Tyler Kinley elected free agency on Nov 6, 2025 and returned to Atlanta, but the
feed files the return only as "assigned to Atlanta Braves" (code ASG, to an MLB club). The counter reads an ASG to an
MLB club as a spring-camp assignment and leaves him off, so he loses 65 days of 2026 (172 to 107). A non-roster
invitee gets the same ASG record, so the code alone cannot tell the two apart.

## Proposed rule (v1)
When a player is off because he elected free agency, and the next record is an ASG to an MLB club dated between
Nov 1 and Opening Day, the counter asks the league roster service for that club's 40-man roster on the day after
the ASG (statsapi /teams/{club}/roster?rosterType=40Man&date=...). On the 40-man: on (a major league deal).
Not on it: stays off (a non-roster invite). Nothing else changes. One roster call per such record, cached.

## Frame and sample (drawn after this file is committed)
- Frame: every player in the service pool with the sequence "elected free agency" then ASG to an MLB club before the
  next Opening Day, seasons 2015 to 2026.
- Sample: 20 players, seed 20261249, at least 8 known major league returns and 8 known non-roster invites if the
  frame allows (strata by whether the 40-man answer is yes or no, so the rule's input does not pick its own truth).
- Truth: published service time (MLB Trade Rumors arbitration lists, the year before and after) where both exist;
  otherwise the player's major league games and IL placements that season against the counter's days.

## Bars
- At least 19 of 20 correct (counter within 10 days of truth for the season in question).
- Kinley 2026 counted 172.
- Every existing plant still passes (round 47 Rule 5 and purchase, round 48 elected free agency and DFA limbo).
- On the 184-player frame, every player whose count changes is listed and each change is explained by the rule.
Fail: report and stop, no variants. No regrade either way; a regrade needs its own prereg.
