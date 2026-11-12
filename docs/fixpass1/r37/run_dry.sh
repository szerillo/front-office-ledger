#!/bin/bash
# Dry-run deploy on a local copy of the live tree: deploy commit, verify (step 7), share step 2b, tests commit,
# then rollback, each with its checks. Served like Pages (gzip, max-age=600) at http://127.0.0.1:8767/dry/
set -u; T=/tmp/dry/tree; G=/tmp/deploy/good7; RB=/tmp/deploy/rb5; LIVE=/home/claude/fol-main; U=http://127.0.0.1:8767/dry/
log(){ echo "[$(date -u +%H:%M:%S)] $*"; }
fail=0; chk(){ if [ "$1" = 0 ]; then log "  OK   $2"; else log "  FAIL $2"; fail=1; fi; }
rm -rf $T; mkdir -p $T; (cd $LIVE && tar --exclude=.git -cf - .) | tar -xf - -C $T; ln -sfn $T /tmp/slow/sites/dry
log "0. dry tree = live copy; index $(md5sum < $T/index.html | cut -c1-8)"
log "1. deploy commit: 8 files"
for f in index.html book.js deals.js cards.js cards2.d7fb83c8d5.js moves.js offseasons.json trade_parts.json; do cp $G/$f $T/$f; done
log "2. verify"
for f in index.html book.js deals.js cards.js cards2.d7fb83c8d5.js moves.js offseasons.json trade_parts.json; do cmp -s $G/$f $T/$f; chk $? "md5 $f $(md5sum < $T/$f | cut -c1-8)"; done
curl -s "$U?t=1" | md5sum | cut -c1-8 | grep -q 279c1e66; chk $? "served index.html md5 279c1e66"
python3 /tmp/deploy/verify_stamps.py $T > /tmp/dry/stamps.txt; chk $? "verify_stamps on the tree"
cd $G; for t in t_build t_launch t_wire t_cards t_nullgrades; do TARGET=live LIVE_URL=$U PAGE=$T/index.html timeout 400 node tests/$t.mjs > /tmp/dry/v_$t.txt 2>&1; chk $? "TARGET=live $t"; done
PAGE=$T/index.html timeout 120 node tests/t_datashape.mjs > /tmp/dry/v_t_datashape.txt 2>&1; chk $? "t_datashape"
PAGE=$T/index.html OUT=/tmp/dry/L_dry.json timeout 400 node /tmp/deploy/letters.mjs > /dev/null 2>&1; cmp -s /tmp/dry/L_dry.json /tmp/deploy/L_g7.json; chk $? "letters census = good7 (102 vs live)"
python3 /tmp/deploy/offs_stamps.py $LIVE/offseasons.json $T/offseasons.json | head -1 | grep -q "changed: 18"; chk $? "tier labels 18"
python3 /tmp/note/note_check.py /tmp/note/note.md > /tmp/dry/note.txt; chk $? "note check"
python3 /tmp/deploy/winter_pages_check.py $T > /tmp/dry/wp_before.txt; r=$?; [ $r = 6 ]; chk $? "winter pages stale before 2b (expected red: $(head -1 /tmp/dry/wp_before.txt))"
log "3. share step 2b"
rm -rf /tmp/dry/share; timeout 500 node /tmp/share/share_live_r36.mjs /tmp/dry/share $U --only-new $T > /tmp/dry/share.txt 2>&1; chk $? "share job: $(tail -1 /tmp/dry/share.txt)"
cp /tmp/dry/share/o/*.html $T/o/; cp /tmp/dry/share/og/o/*.png $T/og/o/; cp /tmp/dry/share/share.json $T/share.json
python3 /tmp/deploy/winter_pages_check.py $T > /tmp/dry/wp_after.txt; chk $? "winter pages after 2b: $(head -1 /tmp/dry/wp_after.txt)"
log "4. tests commit"
mkdir -p $T/tests/fixtures; for f in t_build t_cards t_nullgrades t_datashape t_fun t_wire t_ui2; do cp $G/tests/$f.mjs $T/tests/; done
cp $G/tests/fixtures/page_code.json $G/tests/fixtures/grades.json $G/tests/fixtures/data_shape.json $T/tests/fixtures/
cd $T; n=0; for t in tests/t_*.mjs; do PAGE=$T/index.html timeout 500 node $t > /tmp/dry/s_$(basename $t .mjs).txt 2>&1 || { n=$((n+1)); log "    red: $t"; }; done; chk $n "all suites from the tree's own tests folder ($(ls tests/t_*.mjs | wc -l))"
log "5. rollback"
for f in index.html book.js deals.js cards.js cards2.bc21eaa482.js moves.js offseasons.json trade_parts.json; do cp $RB/$f $T/$f; done
cp $LIVE/o/*.html $T/o/; cp $LIVE/og/o/*.png $T/og/o/; cp $LIVE/share.json $T/share.json
for f in /tmp/dry/share/o/*.html; do b=$(basename $f); [ -e $LIVE/o/$b ] || rm -f $T/o/$b $T/og/o/${b%.html}.png; done
[ -e $T/cards2.d7fb83c8d5.js ]; chk $? "candidate cards2 part still present after rollback"
python3 /tmp/deploy/verify_stamps.py $T > /dev/null; chk $? "verify_stamps after rollback"
PAGE=$T/index.html OUT=/tmp/dry/L_rb.json timeout 400 node /tmp/deploy/letters.mjs > /dev/null 2>&1; cmp -s /tmp/dry/L_rb.json /tmp/deploy/L_live.json; chk $? "letters census after rollback = live"
python3 /tmp/deploy/winter_pages_check.py $T > /tmp/dry/wp_rb.txt; chk $? "winter pages after rollback: $(head -1 /tmp/dry/wp_rb.txt)"
cd $G; TARGET=live LIVE_URL=$U timeout 400 node tests/t_launch.mjs > /tmp/dry/rb_t_launch.txt 2>&1; chk $? "TARGET=live t_launch after rollback"
log "DONE fail=$fail"
