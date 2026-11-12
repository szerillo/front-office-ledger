#!/bin/bash
# usage: run_freeze.sh <RUN name> <engine dir name under /tmp/fix> <freeze 0|1> [extra env...]
R=$1; ENGD=$2; FZ=$3; shift 3; RUN=/tmp/sbx/runs/$R; RR=/home/claude/front-office-ledger; Z=/tmp/sbx/runs/Z_X6/work
rm -rf $RUN; mkdir -p $RUN; cp -a /work $RUN/work
cp /tmp/fix/$ENGD/engine/*.py $RR/ingest/*.py $RUN/work/; cp /tmp/fix/$ENGD/ingest/regen_v3.py $RUN/work/; cp -r $RR/data/research $RUN/work/research
mkdir -p $RUN/work/repo && (cd $RR && tar --exclude=.git -cf - .) | tar -xf - -C $RUN/work/repo; cp /tmp/v2/ledger_v3.sqlite $RUN/work/ledger.sqlite; chmod 644 $RUN/work/ledger.sqlite
cp $Z/names_pinned.json $RUN/work/; [ -f /tmp/fix/$ENGD/engine/published_service.json ] && cp /tmp/fix/$ENGD/engine/published_service.json $RUN/work/
F="trade_calib.json draft_calib.json ext_class_rate.json calib_blend.json calib_results.json arb_calib_rows.json calib_chart.json"
if [ "$FZ" = 1 ]; then mkdir -p /tmp/r49/run/frozen; for f in $F; do cp $Z/$f $RUN/work/$f; cp $Z/$f /tmp/r49/run/frozen/$f; done
  (cd $RUN/work && md5sum $F | sed 's#  #  /work/#') > $RUN/frozen.md5; DRV=/tmp/r49/run/step_run_freeze.sh; EXTRA="FREEZE=/tmp/r49/run/frozen $*"
else : > $RUN/frozen.md5; DRV=/tmp/sbx/step_run_eng.sh; EXTRA="$*"; fi
cat $RUN/frozen.md5 > /tmp/r49/run/$R.frozen.txt
: > $RUN/steps.txt; touch $RUN/INIT
while true; do
  ENG=$ENGD $DRV $R /tmp/v2/ledger_v3.sqlite $EXTRA > /tmp/sbx/runs/$R.drv.log 2>&1
  grep -q '^DONE' $RUN/steps.txt && break; grep -q '^STOP' $RUN/steps.txt && break
done; echo "$R finished: $(tail -1 $RUN/steps.txt)" >> /tmp/r49/run/runs.log
