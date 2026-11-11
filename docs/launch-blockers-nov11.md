# Launch blockers (Nov 11, 5:19 PM round)

Ordered by what has to happen first. Plan and verification steps for items 5 and 6: `docs/plan-items-5-6.md`. "Me" means Claude; "Clear without Sean" means it can be finished
without a decision from Sean (deploys always need his OK). Sizes: S under an hour, M a session, L several.

| # | Item | Why it blocks | Owner | Size | Clear without Sean | Verified when |
|---|---|---|---|---|---|---|
| 1 | **DONE Nov 11 22:40 UTC (Sean approved).** Determinism patch (`4ff51c5`), engine `279379f`, site `13a4570` | The shipped grader reads signings in no fixed order, so a rebuild can change the public winter table (5 shuffles gave 5 different files) | Me to verify (done), Sean to OK the deploy | S | Verification yes; deploy no | 10 shuffled rebuilds give one md5 (`1a4a4a5e`); PRAGMA reverse_unordered_selects, 3 hash seeds and SQLite 3.51 vs 3.53 change nothing; 13 rows change against live, none with a share page (`tests/tools/r21_determinism.json`) |
| 2 | Rounding rule for winter dollar totals | 132 cells sit exactly on .5; the rule has to be written down before anything is rebuilt | Sean (one line) | S | No | Rule in the methodology doc; a rebuild matches it on all 132 |
| 3 | 2020 charge fix, version (a) or (b) | Grades covering 2020 are too low (Cole -1.9, about +1.0 fixed); 7 public winter pages move | Sean decides; me to build | M | No | Regrade on the deterministic build; `t_grades` snapshot updated with a REASON; the 7 pages recomputed |
| 4 | Same-club re-sign rule on the page (`resign-keeps-open.diff`) | 11 trades read CLOSED that are open | Sean OK; me to upload | S | No | 14 suites pass live; OPEN count 721 |
| 5 | Engine side of the re-sign rule | Henriquez 2022 and Eli White 2023 grades miss about 2 wins each | Me, after 4 | M | Build yes; deploy no | Engine rerun; the two grades flip as sized; t_grades diff logged |
| 6 | Service-time control end | 71 grades move a win or more (Olson extension +12.0 to +3.8) | Me to build; Sean OK | L | Build yes | Engine rerun with service-time ends; 6 hand checks against Baseball-Reference service time |
| 7 | One deploy of index.html and data | Items 1 to 6 reach the site only through it | Sean OK; me to upload | S | No | Live md5 equals the built files; all suites pass live |
| 8 | "Require this computer" on the four Ledger tasks | Scheduled refreshes have not run since 07:51 UTC; the wire and trade reports go stale | Sean (desktop app) | S | No | rumors.json and wire.json "checked" under 24 hours on the live site |
| 9 | Caveats on known estimates | Arbitration estimate runs low; trade-season proration by stint rows; $0 post-control seasons | Sean picks fix or caveat; caveat text is built | S | Caveat text yes | Caveats visible in the methodology list after item 7 |
| 10 | 1998-2014 extension file | 3 clear errors in 25 sourced rows | Sean: label or correct | S (label) / L (correct) | No | Label live, or rows corrected from salary tables |
| 11 | Launch posts | Need the final numbers after item 7 | Kirk drafts, Sean posts | S | Drafting yes | Every number matches the live page |

**Step 0 (Nov 11 evening, prereg `3f0018a`): FAIL.** The trade pipeline is order-dependent: every published file
changes md5 under a shuffled `sweep_tx` or reversed reads. What reaches the site: 13 of 30 current regime totals vary
by up to 0.2 (report cards), player order inside trade seats, 2 player display names, 6 settled winter move lists;
no trade grade, no winter number, no share page, nothing 2022+. Details in `tests/tools/step0_results.json`.

**Next blocker I can clear without Sean:** trace every remaining published difference (`moves.js`, desk data,
`cards.js`) to its read, write the order fixes as one patch, and re-run Step 0 on the patched build until all
published files have one md5. Paper only; deploying the patch is Sean's call. Items 5 and 6 wait for it.

Also found, for Sean (not changed):
- `/work/fa_grade.py` and `/work/offseasons_build.py` are still the unpatched copies (`01c80d6b`, `d6692708`), and
  `run_chain.sh` runs the chain from `/work`. A rebuild from `/work` would bring back the order-dependent grader.
  One-step fix: copy `engine/fa_grade.py` and `engine/offseasons_build.py` from main into `/work`.
- The runbook seed misses `data/research/` and a `/work/repo` checkout, `/work/ledger.sqlite` is empty, and the step
  that wraps `TRADE_BOOK` in `JSON.parse(` for `split_book.py` is not in the chain or the runbook.

Not blocking launch, listed so they are not lost:
- fa97 contract terms: the pre-registered re-check passed (`9753a0b`, results `tests/tools/prereg21_results.json`); no label needed. Fassero and Furcal overrides are proposed (grades -1.5 to -1.4 and +4.1 to +3.7; no share page).
- Filler rule and bonus method: 0 live grades read the affected rows today.
- Baseball-Reference salary pull: feeds the shadow runs only; it sizes item 9, it does not change a live grade.
- Brotli through a CDN (about 1.4 s on slow 4G): Sean's call, any time.
