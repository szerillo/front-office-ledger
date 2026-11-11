#!/bin/bash
F=/tmp/sbx/frozen
( /tmp/sbx/one_run.sh R0 $F/ledger_frozen.sqlite; /tmp/sbx/one_run.sh R2 $F/ledger_R2.sqlite; /tmp/sbx/one_run.sh R4 $F/ledger_R4.sqlite; /tmp/sbx/one_run.sh R6 $F/ledger_frozen.sqlite GUARD_REVERSE=1 ) &
( /tmp/sbx/one_run.sh R1 $F/ledger_R1.sqlite; /tmp/sbx/one_run.sh R3 $F/ledger_R3.sqlite; /tmp/sbx/one_run.sh R5 $F/ledger_R5.sqlite; /tmp/sbx/one_run.sh R7 $F/ledger_frozen.sqlite GUARD_CLOCK=2026-12-15T12:00:00+00:00 ) &
wait; echo ALL > /tmp/sbx/runs/ALL_DONE
