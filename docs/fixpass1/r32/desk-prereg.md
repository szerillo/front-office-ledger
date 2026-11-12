# Deal Desk check: pre-registration (written Nov 12, before the deal set, the runner or any result exists)

## What it closes
The census tools grade report cards, moves, trades, tiers and the Wire. None of them grades a deal typed into
the Deal Desk, so a change to DESK data or Desk code could ship unseen (the Nov 12 seeds showed "caught by nothing").

## The deal set (fixed before any grading)
50 deals, generated once by deals_gen.py with seed 20261112 and saved as deals50.json (its md5 is recorded
before the first run):
- 30 trades: 20 one-for-one and 10 two-for-one, MLB players only, two different clubs.
- 12 free-agent signings: free agents only, years 1 to 6, total from the player's own Desk fair value
  times a fixed factor in 0.7 to 1.4, signing club drawn at random.
- 8 draft-room packages: 2027 picks only, 1 or 2 picks a side.
Eligible players are only those whose Desk row, status and QO flag are identical in both builds, on clubs whose
payroll row is identical. So every input typed is the same on both builds.

## What is recorded per deal
The letter(s) (trade: your side and theirs; FA: one; draft: one), every number in the verdict tiles, and the
full verdict text.

## Builds
L = live (eb310ee files), C = candidate (good4, cards split). Also R = split rollback set (rb_split).

## Expected results, stated now
E1. R vs L: all 50 verdicts byte-identical (full HTML). The split must change nothing.
E2. Free-agent signings, C vs L: 0 letter differences, 0 tile-number differences. Their inputs (player rows,
    DESK.market, QO list) are identical and the FA letter does not read MOVE_BANDS. Text outside the tiles may
    differ only in comp lines and GM grade lines.
E3. Trades and draft packages, C vs L: 0 tile-number differences (same inputs). Letters MAY differ, because the
    trade letter is a percentile against MOVE_BANDS.trade, and MOVE_BANDS changed with the re-sign rule and the
    2020 fix. Every such letter difference must vanish when the live MOVE_BANDS is put into C (control C').
E4. C' (candidate with live MOVE_BANDS and live DESK.deals) vs L: 0 letter differences and 0 tile-number
    differences on all 50.
Any difference outside E1 to E4 is a red result to trace before deploy, not to explain after.

## Seed (to show the check can go red)
S = C with DESK.market.dpw['2027'] raised 10%. Expected: E2 fails (FA tile numbers move), so the check is RED.
