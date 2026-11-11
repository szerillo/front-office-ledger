#!/bin/bash
# runs inside a private mount + network namespace
set -e
mount --bind /work /tmp/sbx/realwork && mount -o remount,bind,ro /tmp/sbx/realwork
mount --bind /tmp/sbx/run/work /work
cd /work
export PYTHONPATH=/tmp/sbx/guard PYTHONHASHSEED=0 GUARD_LOG=${GUARD_LOG:-/tmp/sbx/run/guard.log}
exec "$@"
