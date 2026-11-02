#!/bin/bash
# The full rebuild, in order (v5.9). Feed repairs and calibrations first
# (debut dates, Rule 5 conduits, the contract book, the open-trade and draft
# curves); hist_score right after sweep_score, because fa_grade and
# ext_grade grade archive regimes too; validation after them (it reads the
# value-time series they extend); h2h_deals after trade_book.
set -e
for s in debut_fetch r5_conduit contract_book trade_calib draft_calib sweep_score hist_score fa_grade ext_grade \
         ifa_score dev_score postseason archetype ret2 savant_fingerprint validation champions_build trade_comps market_comps \
         proj_v1 trade_book h2h_deals desk_data contract_apply scenario_build gm_data reliability regen_v3; do
  echo "=== $s ===" >> /tmp/chain.log
  python3 $s.py >> /tmp/chain.log 2>&1 || { echo "FAILED $s" >> /tmp/chain.log; exit 1; }
done
echo "CHAIN DONE" >> /tmp/chain.log
