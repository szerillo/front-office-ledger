# Round 52 (Nov 12, 2026)

## 1. Plant-run amendment: run as written, stopped at guard (c). F2 not run. Grades held. Launch waits.

Amendment and guard (a) evidence committed first (55394df, 20:28:47 UTC; first run started 20:29 UTC).

Guard (a): baseline championship file md5 0ced72a00e3c083717defa0914a8cea5. Followed through the read and write logs:
one step reads it (regen_v3); downstream of it are cards.js, moves.js, the prototype page and the names cache.
Graded files the evaluator scores downstream of it: 0 (champs_proof.json).

Guard (b), PU (plant +1.0 on 8,783 season values, nothing frozen): TRIPPED. Against live: 308 untraced letters,
587 unattributed nets, 74 untraced overall grades. PU did not finish: regen_v3 (step 28) stopped on a player-name
lookup outside the frozen cache, so trade_parts and offseasons (winters) were not built. The trip bar reads letters
and nets only, and those files were complete; the winter counts in PU_trip.json are from a stale input copy and mean
nothing.

Guard (c), PF (same plant, full freeze): FAIL. It stopped at the same regen_v3 lookup, and on the files it did finish
it already fails its bar against FZ2: 258 untraced letters, 91 untraced overall grades, 487 unattributed nets
(PF_vs_FZ2.json). Per the amendment, F2 was not run. No variant was run.

Why PF failed (read after the verdict): the plant changes players' wins, and some fits depend on wins but not on
control end. Example: the contract book's typical free-agent return per win (typical_fa: 1.024, 0.774, ... by
contract length) moves under the plant and is not frozen; under the real rule change (round 50, F1) it is
byte-identical to live. So this plant tests fits the control-end change never touches, and its failure says little
about F2. A plant that perturbs control spans (not wins) would test the fits that matter. That is a new prereg.

## 2. Launch: F2 not reached. Cheapest honest options (Kirk's call)

A. Cheapest (index.html only, about an hour): on the 108 card pages and 19 winter pages that round 50's frozen run says
would change, a page note: "Control years here are counted from the debut; for many players the true control ran
longer, so some numbers on this page are expected to change." The 58 channel letters and 26 overall grades F1 says
would move show "under review" instead of a letter. Numbers stay, labeled. Cost: no engine run; the lists come from
F1 (a frozen run with known untraced items, so a few letters may be flagged that would not move, or missed).
B. Fix first (a new prereg with a control-span plant, then F2): about two to three hours of runs if every stage passes.

## 3. Kinley: truth v2 built, prereg committed (55394df), re-score PASSES 19 of 19

Truth v2 credits DFA limbo, retroactive injured-list days and option days in seasons under 20. Rule v1 (unchanged)
scores 19 of 19 within 10 days; the old counter 17. Kinley 2026: 172. Anderson 2023: counter 152, truth 151.
Morgan 2026: counter 61, truth 53 (inside the 10-day tolerance only because his 3 DFA days are now credited; the
same-day selection and option order still overcounts him by 11 days).
Under-20-day option rule on the 184 frame: 53 player-seasons (46 players) have 1 to 19 option days; crediting them
changes 28 player-seasons, by at most 28 days (a 2020 season, where days scale by 186/66) and 206 days in all.
The rule is still not built: that needs a build GO.

## 4. Innings decimals: after launch

The 712/315 prediction was measured with every fit re-fitting (round 43, run D2); a frozen re-grade cannot reproduce
it, and it would mix two changes in one diff.

## Challenge A

Assumption: every fit leaves a trace as a module global or a statistics/numpy call. Plant (toy_fit.py): a league mean
computed inside a function and applied to all 800 players, with one input moved by 50. The inventory (inventory.py,
the same code used in round 51) reports 0 numeric globals and 0 estimator calls changed: it misses the fit. A
plant-style output check catches it: 799 of 799 non-target outputs move. So the inventory is a lead list, not proof;
only an output-level plant on the right input (control spans here) can show a freeze is complete. The contract book's
typical_fa is a real example the inventory did not list (it lives in a file written by contract_book and the rule
change does not move it).
