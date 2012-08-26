#!/bin/bash

sensor=$1
progName=$2

top -b -d 3 | grep --line-buffered Cpu | sed -u 's/^.\{70\}[[:space:]]*//g' | sed -u 's/%st//' | \
while read line ; do
        ((res_timestamp = $(date +%s)))
        toPrint="$sensor,$res_timestamp,$progName,none,$line"
        echo $toPrint
done
