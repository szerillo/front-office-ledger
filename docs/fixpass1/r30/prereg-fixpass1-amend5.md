# Fix pass 1, amendment 5 (Nov 12, 2026, before the spelling fix is coded)

## Finding
Rule 12b (amendment 3: archive spelling when an archive row exists) changes 13 player display names against what
the live site shows today (/work/trade_book.json names, the production build): 6 accent-only (Iván Rodríguez for
live's Ivan Rodriguez), 2 initial spacing (R. A. Dickey, A. J. Burnett for R.A. Dickey, A.J. Burnett), 5 other
(Mike Morse for Michael Morse, Jerry Hairston for Jerry Hairston Jr., John Mayberry for John Mayberry Jr., Mike
Gonzalez for Michael Gonzalez, Ramón Ramírez for Ramon E Ramirez). Production's own names follow read order (some
archive, some feed), so no content rule reproduces them.

## Rule 12b (replaced again)
A player's display name is the name the live site shows today (data/names_pinned.json: the 5,534 names of the
production trade book, fixed). A player not in it takes the latest feed name, else the archive spelling.

## Pre-registered expectations
1. Exactly 13 display names change against the current candidate (the 13 above), all back to the live spelling;
   0 others.
2. Names against live: 0 of 5,534 differ.
3. Winter headlines: the 4 spelling-only differences against live go to 0; no headline value changes.
4. Determinism: names_pinned.json is a fixed input; the output still has one md5 on X0 and X6 (reversed reads).
