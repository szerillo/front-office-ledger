# Round 40 (Nov 12, 07:24 to ~07:55 ET)

## Item 1: WSH/ATH "#1/#2" softened. DEPLOYED, all gates green
Staged diff, 6 files, nothing else: og/o/2014-wsh.png, og/o/2011-ath.png, o/2014-wsh.html, o/2011-ath.html,
corrections/2026-11-12.html (item 2 line + one line on this change), engine/share_live.mjs (generator, so the next
rebuild keeps the wording; without it the round 36 rule would rebuild the old "#1" text on the next run).
Generator change: a TOO_CLOSE list with only these two winters. Built with the patched generator against the live site:
exactly 2 winter pages came out (4 club pages also came out from Wire drift; not staged, not uploaded). Only the
description and the preview kicker change; every number is the same.
Page/og text now: "One of the two best offseasons on record (too close to rank vs 2011 A's)" / "(... vs 2014 Nationals)".
Commits: ad84e11 (og/o), 620c3f8 (o), 8ba1911 (corrections), 542f010 (engine).
Pre-deploy suites (main + staged files, PAGE set): t_build, t_launch, t_wire, t_cards, t_nullgrades all exit 0.
Post-deploy, fresh clone of main at 542f010 + cache-busted live files (index 279c1e66 unchanged):
TARGET=live PAGE=/tmp/r40/post/index.html t_build exit=0 PASS
TARGET=live PAGE=/tmp/r40/post/index.html t_launch exit=0 PASS
TARGET=live PAGE=/tmp/r40/post/index.html t_wire exit=0 PASS
TARGET=live PAGE=/tmp/r40/post/index.html t_cards exit=0 PASS
TARGET=live PAGE=/tmp/r40/post/index.html t_nullgrades exit=0 PASS
Live vs staged md5 (12:40 UTC): 5/5 served files match (4d8ef3e5, ad401dd6, 817bb255, f147b635, 80d79405).
engine/ is not served by Pages (404); verified at the commit instead: raw/542f010 = 942c021c = staged.
Rollback set: /tmp/r40/rollback (main versions: b9792143, 2cf4fc07, 50843bbb, 0d9d3880, 58ae023f, d2c00c29). Not needed.

## Item 2: does the parked pre-season release rule change a public number? YES
92 trade-side numbers (all 92 moved seats change at one decimal) and 59 winter totals, largest 1.9 wins;
ATH 2011-12 +33.4 to +33.8; 8 positions in the top/bottom 20 winter lists change. Logged on the corrections page as a
known open item (8ba1911). bar2_written.py reproduces it and bar 2 as written (2 seats); bars.py's "unlisted" line in
r39 is the withdrawn 24-seat version.

## Challenge A: Minaya C to D+ is a band shift. Verified; it now traces
Cutoffs are fixed in z (GRADE_Z: C is z >= -0.40, D+ is -0.85 to -0.40). z = net / (seasons + 2) / SD, where SD is
the spread of all GMs' trade rates. SD(trade) went 2.71362 to 2.70856 (newer trades, Oct 29 to Nov 6).
Minaya: net -8.9, seasons+2 = 8.2. C cutoff in wins: -8.90 before, -8.88 after. z -0.4000 (C) to -0.4007 (D+).
His own numbers did not move; the line moved under him by 0.02 wins. Cause = newer data step, as the census said.
Same mechanism, unchanged numbers, 6 letters in all: Minaya trade, and 5 waiver letters (LAA, Hendry, Ricciardi,
Dombrowski MIA, Cashman), which the census filed under the re-sign step because that step moved the waiver spread.
Fragility now: 45 of 662 graded channel cells (39 GMs) sit within 0.1 wins of a cutoff, 26 within 0.05. This deploy
moved cutoffs by a median 0.03 wins, max 0.72. So expect a few one-step letter moves on every refresh with no change
to that GM's own record. Recommendation: one methodology sentence (grades are relative, a letter can move one step
when other front offices' records change), not a note on each grade. Kirk's call.

## Challenge B: content-hash names for every data file. Staged, not deployed
hash_names.py (after split_cards.py): cards.js, moves.js, book.js, deals.js, offseasons.json, trade_parts.json and
dudes.json get <stem>.<md5[:10]><ext> beside the plain file; index.html loads only the hashed names. Exempt by design:
rumors.json, share.json, wire.json (the daily jobs rewrite them in place; the page fetches them with a fresh query).
t_hashnames.mjs fails if index.html (or the cards file) loads any other local .js/.json that is not named by its own
md5. Results: hashed build PASS 11; live today FAIL 8; one reference reverted FAIL; a hashed file edited after naming
FAIL. Dry run with old and new on one server (dryrun.log): new data first gives old page + old data, then new page +
new data, rollback clean, 0 errors in every phase. Index before data gives 404s and the card banner, so the rule is
data commit first, confirm live, then index.html. A real deploy also needs t_build re-pinned (loader strings are code:
t_build FAIL on the hashed build, the other suites PASS).

## Challenge C: ranking claims where the gap is under 0.5
Fixed: WSH 2014-15 / ATH 2011-12 only (stored gap 33.9 vs 33.4 = exactly 0.5; model choices move it 0.3 to 0.5).
Not fixed, listed:
- 29 of 44 winter share pages (and their og images) carry a rank within 0.5 of a neighbour. Best list: 1998-ari #5,
  2019-phi #6, 2006-cws #7, 2005-sd #8, 2009-det #9, 2014-lad #10, 2013-det #11, 2021-tor #13, 2017-mil #14,
  2005-ari #15, 2004-ath #16, 2007-bal #17, 1998-sd #18, 2006-sd #19, 2012-mia #20 (the last three are an exact tie
  at +19.5 shown as three ranks). Worst list: 2016-mia #20, 2001-wsh #19, 2014-cws #18, 2005-tex #17, 1998-laa #16,
  2010-mil #15, 2014-bos #14, 1998-nyy #13, 2015-det #12, 2014-det #11; outside the 20s: 2019-laa #29 worst,
  2019-wsh #26 worst (tie with 2011 LAA), 2020-nym #21 worst (tie with 2003 CLE).
- Wording bug found: o/2021-tex.html says "The #675 worst offseason since 1998" for a +18.2 winter (23rd best).
  Pages kept outside the top/bottom 20 (round 36) fall into the "worst" branch. Needs a fix; not touched.
- Offseason explorer rank chip (index.html, every settled winter): 670 of 696 adjacent pairs are under 0.5 apart.
- Front office rankings ("#i of the 23 front offices"): 18 of 22 adjacent gaps under 0.5 wins a season, 9 under 0.1
  (CLE #1 vs LAD #2: 0.16). That unit is per season, so 0.5 is a loose bar there.
- share.json and feed.xml carry no ranking claims. Prospect/draft "#" ranks are external lists, not ours.

## Challenge D: what my 152/152 check still shares with the engine
Both sides come from the same engine run, so both share its inputs; the WAR cache (lvm_cache.json) is the big one.
Planted: Josh Reddick 2012 OAK WAR 4.19 to 6.19 in a copy of the cache, before any step; full engine-f run D0 on
ledger_v3 with pinned names (resumable runner; plant confirmed still in the cache after the run).
Effect: ATH 2011-12 +33.4 to +35.2 (it would retake #1 by 1.3), BOS 2011-12 -11.8 to -13.6, trade 2011-12-28 ATH
+1.8 / BOS -1.8. GM letters: none move (Beane 94.8 and Cherington -8.0 stay in their bands).
What catches it: nothing automatic. Determinism: no (D0 is deterministic). Live-vs-engine (152/152): passes once
deployed, because both sides carry the error. fa_independent_check: reads the same cache. Letters census: 0 GM
letters change. The only signal is a change detector (diff vs the last deploy shows 4 numbers moved with no listed
cause), which is exactly what bar 2 does for a rule but nothing does for a WAR refresh. Proposed: every cache refresh
lists the rows that moved and checks a sample plus the biggest movers against FanGraphs or Baseball-Reference.
