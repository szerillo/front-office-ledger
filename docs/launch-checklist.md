# Launch checklist

Written Nov 11 2026 from `HANDOFF.md`, `worklog.md`, `what-worked.md` and a look at the live site.

## Must fix before launch
- [x] **OPEN / CLOSED is a date rule, not a fact.** Every decision dated 2021 or later is flagged OPEN, everything earlier CLOSED. That is why the Christopher Morel signing (1 year with Miami, played out, he has since left) reads OPEN between two CLOSED rows on his tree, and why the Holmes / Taylor deadline deal reads OPEN on the Cubs' side even though both rentals are free agents. About 250 played-out signings carry the same wrong flag. Fix: decide OPEN from the facts the page already has (who controls each player today, contract years left).
- [x] **Holmes / Taylor net WAR.** After the flag fix the deal stays OPEN, correctly, because Jefferson Rojas is still under the Mets' control. Its -1.7 for the Cubs comes from Rojas's prospect mark, not from anything he has played. The row should say so. Done Nov 11: open trades now say when a piece counts at prospect value.
- [ ] **"Checked" stamps.** `rumors.json` and `wire.json` still have no `checked` time; no scheduled run has uploaded since the prompts changed. Prove the upload path with one real run of each job, then watch the 8:03 and 8:17 AM ET runs. Nov 11: both files stamped 07:51 UTC by hand-run jobs and live; scheduled runs still to be seen.
- [ ] **Link preview cards.** Home and move pages carry full X and Open Graph tags, and pages and images return 200. Only a real post on X confirms the card (Sean).

- [x] Accuracy audit of 40 random moves (Nov 11): 2.7% field error rate, fixes live. `audit-nov11.md`.
- [ ] Prospect value in open trades (Crochet, Holmes and Taylor): waits on Sean.
- [ ] Super Two extensions (Donaldson 2016, Olson 2022): engine rebuild.

## Nice to have
- [ ] Phone load: home content 3.3 s on 4G, 8.2 s on slow 4G. Next step is moving player names and the Desk's player table out of the first download (about 8% and 35% of it), which is risky before launch.
- [ ] Brand final pick: nameplate, wordmark font, palette, logo (six rounds of mockups). `HANDOFF.md` says the masthead is settled; confirm whether that covers all four.
- [ ] Champions color legend and view toggle, Deal Desk swap sides, simulator salary shed (each asked for once).

## After launch
- [x] Up next features: GM battle cards, player career tree card, weekly streak board for Who Won (shipped Nov 11).
- [ ] Backlog in build order (fan vote, puzzles, share cards, stories).
- [ ] NHL edition (no NHL numbers in public until the pick ties are fixed).
- [ ] Which scheduled tasks to keep.
