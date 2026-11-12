# Round 34 (Nov 12, ~02:00 ET): stamps verified from bytes, GM-line bug fixed, tags traced. Nothing deployed

## 1. The cards2 name is computed, not pasted
split_cards.py: js2 = part(p2) (line 24); h2 = md5(js2)[:10] (line 25); name2 = 'cards2.' + h2 + '.js' (line 29);
the loader string is built from name2 and the same js2 is written to name2 (line 39). New verify_stamps.py runs at the
end of build_site.py and recomputes every stamp from the bytes on disk: each index.html ?v= (md5 or sha1 prefix),
and the cards2 name in cards.js against its file's md5. Exit 4 on a mismatch.
- good6: 7 stamps green. rb5: 5 stamps green (its winter files are ?v=1, as on live).
- Seed: one byte changed in good6's cards2.d7fb83c8d5.js: RED (md5 54f719e8b8). Same seed on rb5's
  cards2.bc21eaa482.js: RED (md5 3a29f713af). Originals untouched.
- Live eb310ee: RED as expected (cards.js names no part), so the check also tells an unsplit build apart.

## 2. Old parts: never deleted
Written into the checklist. About 2 MB a deploy in the repo; no owner or later check needed.

## 3. Athletics "trade grade F over 1 deal": a pre-existing page bug, exposed by data. Not a rule change
Raw row: ledger sweep_tx tx_id 947273, 2026-10-29, "Athletics traded RHP Jareth Rayo to Boston Red Sox for LF Nate
Eaton." Engine: sweep_score.py:371 nets the trade (Rayo out 0.4, Eaton in 0.0: -0.4); sweep_score.py:441 counts n=1
and sets g = grade(-0.4 / seasons) = 30 for a seat that began 2026-10-19. Page: applyGradePolicy
(index.html:12521-12528) nulls the grade, because the site grades a channel only with 3+ deals (MIN_N.trade = 3,
index.html:12458, same on live) and never in a new seat (isNew, seat < 0.25). The report card shows no trade grade.
The Deal Desk GM line (index.html:7980; live 7963, identical code) checks only n > 0 and prints g2letter(null),
and g2letter (index.html:2124) falls through to "F". Live never showed it because no current GM had 1 or 2 trades.
So: data (a new trade) exposed a display bug; the grading rule is unchanged. Fix in build_site.py: the line reads
"Taylor Smith (ATH): 1 deal so far, too few to grade." Desk check good5 vs good6: only T08, T10, T16 change, all
letters the same. Of the other 13 g2letter call sites, most are null-guarded; the rest print overall or success grades.
ATH's overall grade is null on live too, so anything those show for a new seat already shows on live; not traced here.

## 4. Style tags: tag rule unchanged, inputs changed
Tag code is build_styles() in ingest/regen_v3.py. Diff between the live engine (/tmp/fix/a, = repo main) and the
candidate (/tmp/fix/f): 2 changed lines, neither in build_styles (line 319 swap marker, line 541 ORDER BY). Tag
rule: 0 lines. All 8 changed tag lists (6 swaps, 2 reorders: CIN, SD) already match the candidate at the data stage
(RV3). The input that moves is dna.draftRoom (archetype.py:198-214: signed round 1-10 picks with bonus and slot
value). Live counted one draft class per GM (PHI, CWS, KC, DET, NYM n equal to their 2026 class alone); the rebuilt
ledger has bonus and slot for 2017 to 2026, so n grows (PHI 11 to 58, ATL 19 to 88). More complete data; the
public tags for 6 GMs follow from it.

## 5. Retry cannot double-merge
Merge count = 'cards-loaded' events (cardsMerge fires it once per real merge):
- part 2 delayed 6 s (no error, so no retry): 1 request, 1 merge, 152 clubs.
- part 2 fails once, retry served: 2 requests, 1 merge, 152 clubs.
- part 2 executed a second time after ready: CARD_PARTS 3, still 1 merge (gate needs exactly 2, and cardsMerge
  returns once CARDS_READY).

## 6. Deploy-day assumptions
Tested: the post-deploy checks can reach the live site from this workspace. TARGET=live t_cards ran against today's
live page (cards ready, every card merged) and is red only on the split checks, as expected before the deploy.
Cannot test before the go: that four upload calls on one page make one commit with all 8 files at the right bytes.
A test needs a real commit of the site files, which is the step the permission check stops. Covered by step 2.1
(md5 at the commit SHA) and by the design: a missing cards2 file shows the banner, never mixed data.

## Also found: t_build skipped long code lines
t_build treated every line of 400+ characters as data, so 176 code lines (105 KB, including the Desk GM line) were
outside the page-code hash; it passed the GM-line change. Rule now: data = a literal or JSON.parse declaration.
Seeds: GM-line change RED, the 339-line build RED, good2 (different data) differs only in the two intended stamp
lines. Full live vs good6 code audit: 5 intended changes (re-sign rule, winterFA tree text, arb caveat line, data
stamps, GM line). Fixture regenerated with a reason on good5, then on good6.
