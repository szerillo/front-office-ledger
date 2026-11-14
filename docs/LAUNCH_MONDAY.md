# LAUNCH MONDAY (Nov 16, 2026)

## Status (Sat Nov 14, after round 55)
- Live: index.html md5 0aa79edec616aa9854039c62ae68fc3e (commits 0bde828, redeployed 2b47aca), fixture 791f847,
  t_grades key fix aae64bd. Share pages and previews: og cd66b20 f0307b5 cb9c117 a9aa713, og/t d525d3b,
  og/h 7eaa524 34a6384 f750dad 1b7b963, c/ 8bebd5c cd76fda, t/ a63bcbf, h/ b320e7c c84f973, play f93e846,
  corrections e9f8907, sitemap 8f24e80, generators d9bc375. Round 54 labels unchanged and still pass.
- Post-deploy: live md5 = repo; allsuites_v3 19/19 on a fresh clone; value dumps unchanged (Desk c25bca11a598,
  grades 28cf6541870f); index gate CLEAR; label check PASS (107 cards, 320 winters, 19 winter pages); the six new
  round 55 checks PASS on the live site (one first-run preview_check failure, not captured, three reruns PASS; see
  docs/fixpass1/r55/live_new_checks.txt).
- The first round 55 index deploy went red on t_grades and was rolled back within minutes; see docs/fixpass1/r55/README.md.

## Launch blockers
None open. The three Nov 14 Auditor blockers are fixed:
1. Share text and preview images for all 152 report cards and 30 club pages rebuilt from the live grades (trade
   previews too); preview URLs carry ?v=20261114; preview_check holds every card and club page to the live page.
2. Corrections log at /corrections/, linked from the footer ("Corrections"; feedback is now its own link), from
   every under-review label and the card note, and listed in the sitemap.
3. Trade table line: no longer called rounding. Each card states its rows' sum, the trade grade's total, the gap,
   and where it comes from. Two deals have a player recorded on one side only (Gwynn Jr., Milwaukee May 2009;
   Pena and Hellweg, Angels July 2012); the table includes them and marks the row "record completed", the grade
   does not yet (Melvin's trade total 4.1 too high, the Angels 1.1 too low). Listed as an open item on the log.
   The rest of each gap (up to 1.6 wins, Towers) is the grading run valuing some deals differently from the
   seat-by-seat table plus row rounding; the note says so.

## Should-fix items
- 4. Fixed: "traded player, [name]" and "St. Louis Cardina" tidied at load (cards and player moves).
- 5. Known, listed on the corrections log: winter headlines of the "Cash or a player to be named" / "Got X" class
  (2018-19 Yankees Sonny Gray, 2007-08 Pagan). The 229 + 223 headlines were not re-checked this round.
- 6. Known, listed on the log: postseason series wins come from a feed parse that misreads some series. Yankees:
  2003 and 2004 Division Series wins missing, 2011 Division Series loss counted as a win, so 1998-2005 shows 12
  (should be 14) and 2006 on shows 16 (should be 15; trips 16 incl. 2026 by the feed). Success grades may move;
  fix and re-grade after launch.
- 7. Fixed: methodology text now states the chart's numbers (draft 0.26, free agency 0.22, extensions 0.19,
  waivers 0.10, trades -0.09) and the weights the grades use (0.71, 0.68, 0.66, 0.59, 0.5).
- 8. Fixed: trade previews and cards no longer apply a 1.35x win-now weight (text now says every win counts the
  same); the Heists list ranks on the plain gap; preview header no longer overlaps the logo.
- 9. Fixed: #view=winters&id= opens any of the 816 winters, accepts 2018-19-nyy and old codes (oak), and says so
  when nothing matches.
- 10. Fixed: sitemap lists home, corrections, 152 cards, 30 club, 30 winter-club, 44 winter, 116 trade and 19
  move pages; the noindex Cleveland redirect is out.
- Also noted: club pages rank among 23 ranked front offices, card pages among 28 graded active ones, so the two
  rank numbers differ for the same club (both match their own view).

## Known wrong, labelled (control end counted from the debut)
- 107 report cards, 320 explorer winters, 19 winter share pages, as in round 54 (docs/fixpass1/r54/).
  Card and club previews now carry the label too.

## Known open items, disclosed (not control end)
- On /corrections/: the two one-sided trade records, postseason series counts, winter headline class,
  pre-season release rule (Nov 12), control-end review (Nov 14).
- Innings read as decimals (at most 0.4), Desk control ends estimated where service time is missing.

## Sean does these himself
- X posts for launch (drafts are his; nothing posted). The trade-reports skill card is his to accept.
- X preview cache: card, club and trade previews changed; links shared before today may show the old image until
  X re-crawls (new links use the versioned image URL).

## One-command rollback
    python3 docs/fixpass1/r55/rollback_r55.py rollback_out
Downloads the pre-round-55 version (9d2288c) of every file this round changed into rollback_out and checks the
index md5 (a47cecdea957...). Upload folder by folder (og pngs, c/, t/, h/, play/, corrections/, root, tests/,
engine/). Tested Nov 14 (606 files, md5 OK). Round 54's rollback (docs/fixpass1/r54/rollback_r54.py) still
applies after that.

## After launch, in order
1. Control-span prereg (docs/fixpass1/r54/postlaunch_item1_control_span_prereg_DRAFT.md), F2, then the re-grade
   that removes the labels.
2. Postseason series parse fix and Success re-grade; one-sided trade records (Gwynn Jr., Greinke deal).
3. Winter headline re-check (cash or PTBNL, "Got X").
4. Innings decimals; Kinley rule build; pre-season release rule.
