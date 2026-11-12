#!/bin/bash
# Round 51 runs. usage: run_freeze2.sh <RUN> <engine dir under /tmp/fix> <mode: U unfrozen | R record | F full freeze> <plant D, 0 for none> [env...]
R=$1; ENGD=$2; MODE=$3; PD=$4; shift 4; RUN=/tmp/sbx/runs/$R; RR=/home/claude/front-office-ledger; Z=/tmp/sbx/runs/Z_X6/work
rm -rf $RUN; mkdir -p $RUN; cp -a /work $RUN/work
cp /tmp/fix/$ENGD/engine/*.py $RR/ingest/*.py $RUN/work/; cp /tmp/fix/$ENGD/ingest/regen_v3.py $RUN/work/; cp -r $RR/data/research $RUN/work/research
mkdir -p $RUN/work/repo && (cd $RR && tar --exclude=.git -cf - .) | tar -xf - -C $RUN/work/repo; cp /tmp/v2/ledger_v3.sqlite $RUN/work/ledger.sqlite; chmod 644 $RUN/work/ledger.sqlite
cp $Z/names_pinned.json $RUN/work/; [ -f /tmp/fix/$ENGD/engine/published_service.json ] && cp /tmp/fix/$ENGD/engine/published_service.json $RUN/work/
if [ "$PD" != 0 ]; then python3 - "$RUN/work/lvm_cache.json" "$PD" <<'PY'
import json, sys
p, d = sys.argv[1], float(sys.argv[2]); L = json.load(open(p)); CH = set(json.load(open('/tmp/r51/ch.json'))); n = 0
for k in CH:
    if isinstance(L.get(k), dict):
        for row in L[k]['rows']: row[2] += d; n += 1
json.dump(L, open(p, 'w')); print('plant: +', d, 'on', n, 'rows of', len(CH), 'players')
PY
fi
F="trade_calib.json draft_calib.json ext_class_rate.json calib_blend.json calib_results.json arb_calib_rows.json calib_chart.json"
case $MODE in
 U) : > $RUN/frozen.md5; DRV=/tmp/sbx/step_run_eng.sh; EXTRA="$*";;
 R) for f in $F; do cp $Z/$f $RUN/work/$f; done; (cd $RUN/work && md5sum $F | sed 's#  #  /work/#') > $RUN/frozen.md5
    mkdir -p $RUN/rec; DRV=/tmp/r49/run/step_run_freeze.sh; EXTRA="FREEZE=/tmp/r49/run/frozen RECORD=$RUN/rec $*";;
 F) F2="$F reliability.json validation.json"; for f in $F2; do cp $Z/$f $RUN/work/$f; done; (cd $RUN/work && md5sum $F2 | sed 's#  #  /work/#') > $RUN/frozen.md5
    DRV=/tmp/r51/run/step_run_freeze2.sh; EXTRA="FREEZE=/tmp/r49/run/frozen FREEZE2=/tmp/r51/frozen2 $*";;
esac
: > $RUN/steps.txt; touch $RUN/INIT
while true; do
  ENG=$ENGD $DRV $R /tmp/v2/ledger_v3.sqlite $EXTRA > /tmp/sbx/runs/$R.drv.log 2>&1
  grep -q '^DONE' $RUN/steps.txt && break; grep -q '^STOP' $RUN/steps.txt && break
done; echo "$R finished: $(tail -n1 $RUN/steps.txt)" >> /tmp/r51/run/runs.log
