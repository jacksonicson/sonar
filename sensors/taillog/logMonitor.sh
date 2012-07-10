#!/bin/bash
sensor=$1
progName=$2
logFile=$3

trap 'kill $(jobs -p)' EXIT

tail -fn0 $3 | \
while read line ; do
	((res_timestamp = $(date +%s)))
	toPrint="$sensor,$res_timestamp,$progName,$line"
	echo $toPrint
done
