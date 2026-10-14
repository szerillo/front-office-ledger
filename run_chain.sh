#!/bin/bash
set -e
for s in sweep_score fa_grade ext_grade ifa_score dev_score postseason archetype ret2 validation; do
  echo "=== $s ===" >> /tmp/chain.log
  python3 $s.py >> /tmp/chain.log 2>&1 || { echo "FAILED $s" >> /tmp/chain.log; exit 1; }
done
echo "CHAIN DONE" >> /tmp/chain.log
