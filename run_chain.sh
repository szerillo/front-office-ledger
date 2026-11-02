#!/bin/bash
# The full rebuild, in order (v5.8). contract_book.py first: every scorer
# reads its ownership and money rules. validation.py after hist_score.py
# (it reads the archive results), h2h_deals.py after trade_book.py.
set -e
for s in contract_book sweep_score fa_grade ext_grade ifa_score dev_score postseason archetype ret2 savant_fingerprint \
         hist_score validation champions_build trade_comps proj_v1 trade_book h2h_deals desk_data contract_apply \
         scenario_build gm_data regen_v3; do
  echo "=== $s ===" >> /tmp/chain.log
  python3 $s.py >> /tmp/chain.log 2>&1 || { echo "FAILED $s" >> /tmp/chain.log; exit 1; }
done
echo "CHAIN DONE" >> /tmp/chain.log
