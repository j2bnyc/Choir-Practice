#!/bin/bash
while true; do
    echo -n "$(date +%H:%M:%S) "
    JLinkExe -device NRF52840_XXAA -if SWD -speed 100 -autoconnect 1 -CommandFile tools/jlink_slow_connect.jlink 2>&1 | grep -E "VTref|Cortex|identified|Error|Cannot|AP "
    sleep 2
done
