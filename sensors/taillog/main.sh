#!/bin/bash
sensor=$1
logFile=$2

tail -fn0 /var/log/redis_6379.log | \
while read line ; do
	((res_timestamp = $(date +%s)))
	toPrint="$sensor,$res_timestamp,$line"
	echo $toPrint
done

