#!/bin/bash
# resumable run: $1 name, $2 ledger, rest env. Each call runs whole steps for at most ~7 minutes, then exits; call again to continue.
RUN=/tmp/sbx/runs/$1; LED=$2; shift 2; R=/home/claude/front-office-ledger
if [ ! -f $RUN/INIT ]; then
  rm -rf $RUN; mkdir -p $RUN; cp -a /work $RUN/work
  cp /tmp/fix/$ENG/engine/*.py $R/ingest/*.py $RUN/work/; cp /tmp/fix/$ENG/ingest/regen_v3.py $RUN/work/; cp -r $R/data/research $RUN/work/research
  mkdir -p $RUN/work/repo && (cd $R && tar --exclude=.git -cf - .) | tar -xf - -C $RUN/work/repo; cp "$LED" $RUN/work/ledger.sqlite; chmod 644 $RUN/work/ledger.sqlite
  : > $RUN/steps.txt; touch $RUN/INIT
fi
grep -q '^DONE' $RUN/steps.txt && { echo "$RUN already DONE"; exit 0; }
grep -q '^STOP' $RUN/steps.txt && { echo "$RUN STOPPED"; exit 1; }
DONE_STEPS=$(awk '/ rc=0 /{print $1}' $RUN/steps.txt | tr '\n' ' ')
unshare --mount --net bash -c "
mount --bind /work /tmp/sbx/realwork && mount -o remount,bind,ro /tmp/sbx/realwork && mount --bind $RUN/work /work && cd /work &&
export PYTHONPATH=/tmp/sbx/guard PYTHONHASHSEED=0 GUARD_LOG=$RUN/guard.log GUARD_CACHE=/tmp/v2/http $* &&
T0=\$(date +%s)
for s in r5_conduit contract_book sweep_score hist_score fa_grade ext_grade ifa_score dev_score postseason archetype ret2 savant_fingerprint validation champions_build trade_comps market_comps proj_v1 trade_book h2h_deals debut26 desk_data contract_apply scenario_build gm_data reliability fa_skills regen_v3 offseasons_build trade_parts; do
  case ' $DONE_STEPS ' in *\" \$s \"*) continue;; esac
  [ \$(( \$(date +%s)-T0 )) -gt 400 ] && { echo PAUSE; exit 0; }
  t0=\$(date +%s); timeout 300 python3 \$s.py > $RUN/log_\$s.txt 2>&1; rc=\$?; md5sum -c --quiet $RUN/frozen.md5 >> $RUN/log_\$s.txt 2>&1 || rc=97; echo \"\$s rc=\$rc secs=\$(( \$(date +%s)-t0 ))\" >> $RUN/steps.txt
  [ \$rc -ne 0 ] && { echo STOP >> $RUN/steps.txt; exit \$rc; }
done; echo DONE >> $RUN/steps.txt"
tail -1 $RUN/steps.txt
