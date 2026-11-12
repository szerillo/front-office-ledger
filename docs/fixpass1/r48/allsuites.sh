#!/bin/bash
# usage: allsuites.sh <tree> <tag> [live_url]
# Round 48: one suite run at a time. A second run exits 75 at once instead of starting Chromium in parallel
# (two runs in parallel crashed t_leak in round 47). Inside a run the suites go one after another.
LOCK=/tmp/fol_suites.lock
exec 9>"$LOCK"
if ! flock -n 9; then echo "allsuites: another suite run holds $LOCK, refusing to start" >&2; exit 75; fi
OUT=${SUITE_OUT:-/tmp/r48/s}; mkdir -p "$OUT"
cd "$1" || exit 2; rm -f "$OUT/$2_exits.txt"
for f in tests/t_*.mjs; do t=$(basename $f .mjs)
  if [ -n "$3" ]; then timeout 500 env TARGET=live LIVE_URL="$3" PAGE="$1/index.html" node $f > "$OUT/$2_$t.txt" 2>&1 9>&-; e=$?
  else timeout 500 env TARGET=live PAGE="$1/index.html" node $f > "$OUT/$2_$t.txt" 2>&1 9>&-; e=$?; fi
  echo "$t exit=$e $(grep -Eo 'PASS|FAIL' "$OUT/$2_$t.txt" | tail -1)" >> "$OUT/$2_exits.txt"
done; echo DONE >> "$OUT/$2_exits.txt"
