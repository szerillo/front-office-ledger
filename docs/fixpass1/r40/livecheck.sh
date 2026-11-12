#!/bin/bash
t=$(date +%s); ok=0
for f in o/2014-wsh.html o/2011-ath.html og/o/2014-wsh.png og/o/2011-ath.png corrections/2026-11-12.html engine/share_live.mjs; do
  l=$(curl -s "https://frontofficeledger.com/$f?t=$t" | md5sum | cut -c1-8); s=$(md5sum < /tmp/r40/stage/$f | cut -c1-8)
  echo "$f live $l staged $s $([ $l = $s ] && echo MATCH || echo DIFF)"; [ $l = $s ] && ok=$((ok+1))
done; echo "matched $ok/6 at $(date -u +%H:%M:%S)"
