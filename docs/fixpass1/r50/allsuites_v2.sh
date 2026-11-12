#!/bin/bash
# usage: allsuites_v2.sh <tree> <tag> [live_url]
# Round 48: one suite run at a time (exclusive lock; a second run exits 75).
# Round 49: the run must contain exactly the expected suites. A missing or extra suite file makes the run
# INCOMPLETE (exit 3) instead of reporting a clean pass on fewer suites.
EXPECT="t_audit t_build t_cards t_consistency t_datashape t_features t_fun t_gm_core t_grades t_hashnames t_launch t_leak t_math t_nov11 t_nullgrades t_qa t_ui2 t_winter t_wire"
LOCK=/tmp/fol_suites.lock
exec 9>"$LOCK"
if ! flock -n 9; then echo "allsuites: another suite run holds $LOCK, refusing to start" >&2; exit 75; fi
OUT=${SUITE_OUT:-/tmp/r49/s}; mkdir -p "$OUT"
cd "$1" || exit 2; rm -f "$OUT/$2_exits.txt"
HAVE=$(ls tests/t_*.mjs 2>/dev/null | xargs -n1 basename | sed 's/\.mjs$//' | sort | tr '\n' ' ' | sed 's/ $//')
WANT=$(echo $EXPECT | tr ' ' '\n' | sort | tr '\n' ' ' | sed 's/ $//')
if [ "$HAVE" != "$WANT" ]; then echo "INCOMPLETE: suites found [$HAVE], expected [$WANT]" | tee "$OUT/$2_exits.txt" >&2; exit 3; fi
for t in $EXPECT; do f=tests/$t.mjs
  if [ -n "$3" ]; then timeout 500 env TARGET=live LIVE_URL="$3" PAGE="$1/index.html" node $f > "$OUT/$2_$t.txt" 2>&1 9>&-; e=$?
  else timeout 500 env TARGET=live PAGE="$1/index.html" node $f > "$OUT/$2_$t.txt" 2>&1 9>&-; e=$?; fi
  echo "$t exit=$e $(grep -Eo 'PASS|FAIL' "$OUT/$2_$t.txt" | tail -1)" >> "$OUT/$2_exits.txt"
done
n=$(grep -c "exit=0 PASS" "$OUT/$2_exits.txt"); echo "DONE $n/19" >> "$OUT/$2_exits.txt"; [ "$n" = 19 ] || exit 1
