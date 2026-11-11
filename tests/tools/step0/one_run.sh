#!/bin/bash
# $1 = run name, $2 = ledger file, extra env passed through; runs chain + post steps in its own namespace
RUN=/tmp/sbx/runs/$1; rm -rf $RUN; mkdir -p $RUN; cp -a /work $RUN/work; R=/home/claude/front-office-ledger
cp $R/engine/*.py $R/ingest/*.py $RUN/work/; cp -r $R/data/research $RUN/work/research
mkdir -p $RUN/work/repo && (cd $R && tar --exclude=.git -cf - .) | tar -xf - -C $RUN/work/repo; cp "$2" $RUN/work/ledger.sqlite
shift 2
unshare --mount --net bash -c "
mount --bind /work /tmp/sbx/realwork && mount -o remount,bind,ro /tmp/sbx/realwork && mount --bind $RUN/work /work && cd /work &&
export PYTHONPATH=/tmp/sbx/guard PYTHONHASHSEED=0 GUARD_LOG=$RUN/guard.log $* &&
for s in r5_conduit contract_book trade_calib draft_calib sweep_score hist_score fa_grade ext_grade ifa_score dev_score postseason archetype ret2 savant_fingerprint validation champions_build trade_comps market_comps proj_v1 trade_book h2h_deals debut26 desk_data contract_apply scenario_build gm_data reliability fa_skills regen_v3 offseasons_build trade_parts; do
  t0=\$(date +%s); timeout 3000 python3 \$s.py > $RUN/log_\$s.txt 2>&1; rc=\$?; echo \"\$s rc=\$rc secs=\$(( \$(date +%s)-t0 ))\" >> $RUN/steps.txt
  [ \$rc -ne 0 ] && { echo STOP >> $RUN/steps.txt; exit \$rc; }
done; echo DONE >> $RUN/steps.txt"
