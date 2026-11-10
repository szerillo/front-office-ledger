# Re-walk of Kirk's launch-day QA, Nov 10 2026 (evening)

Run by Claude against the live site (frontofficeledger.com, the build pushed this evening), not a local copy.
Kirk's original write-up is no longer in my records, so this re-runs my scripted versions of his cases: 16
trade and Assistant GM cases, 8 free-agent cases, 8 offseason-advisor cases, plus the 53-check regression
suite (`tests/t_qa.mjs`, desktop and phone). A second pass by Kirk from his own notes is still worth having.

## Blockers
| Item | What was wrong | Live result |
|---|---|---|
| B1 | Stars priced as liabilities; Ohtani, Soto, Judge available for nothing | Pass. Ohtani trade value +6.1, Soto +4.2, Judge +5.0. SF for Ohtani, LAD for Witt, NYY for Skenes or Kurtz: the other club ends the call (cornerstone, not being shopped). Soto or Judge for Connor Wong: refused, with the asking price shown (+4.2 and +7.5). |
| B2 | "Make it fair" built nonsense or went blank | Pass. Rebuilding clubs (COL, LAA, ATH) start from a sale and say so. A Bogaerts dump adds nobody and explains that dumps close with cash. An overpay (KC sending Witt) asks for more back. No blank notes in 16 cases. |
| B3 | The note and the verdict disagreed | Pass. In all 16 cases "Done" in the note matches "would take it" in the verdict, and the two quote the same prices. |

## Trade cases (16)
All 16 behave as intended. Detail: COL-LAD, LAA-MIL, ATH-NYY (sale first, accepted at matching prices);
NYY for Neto (three pieces added, +9.1 against a +9.6 ask, accepted inside the 5% band); LAD, NYY, SF asking
for Witt, Kurtz, Skenes, Ohtani (blocked, with and without the Assistant GM); KC selling Witt (asks for
De Paula and Henriquez back); SD dumping Bogaerts, with and without a return (refused as built, -8.3 wins of
contract, nobody attached); BOS for Soto and Judge (refused); NYY-HOU Wells for Pena (fair as built);
MIL-COL (fills a 1B need, accepted).

## Free-agent cases (8, graded as a Dodgers signing at the site's own market number)
Skubal 8/$353M: C (fair value $372M). Rogers 4/$81M: C. Morejon 4/$69M: C. Gausman 2/$42M: A+.
Suzuki 4/$92M: F, and the sheet now says the forfeited picks account for 1.5 wins and that the same contract
grades C without them. Arozarena 5/$124M, King 4/$92M, Sato 5/$103M: F, each because the market number sits
well above the Ledger's fair value ($83M, $59M, $75M). One projected-wins total per sheet in all 8.

## Offseason advisor cases (8)
BAL and SEA: qualifying-offer advice follows the player's market (Rogers and Arozarena expected to decline).
COL: one posture in both tabs (rebuilding, 58 wins, 72 projected). DET: one posture in both tabs (fringe, 76
and 86). LAD: camp opens above our number for Skubal. MIL: non-tender calls carry the estimate's caveat.

## Should-fix items
S1 to S15: pass, each has at least one check in `t_qa.mjs` and the suite passes live on desktop and phone.
S5 (a traded star's extension on the trade line) is now complete: "traded BOS to LAD, control years only.
Under the LAD extension that followed: +34.7 WAR in 6 seasons so far." S16 (load size) is the one item still
open; see the worklog.

## Things I would still want a second pair of eyes on
- Three of the eight market-price signings grade F. That is the model saying the market overpays those
  players, and the sheet explains it, but it reads harshly.
- The Assistant GM's non-tender calls lean on an award estimate with a typical miss of $1.6M.
