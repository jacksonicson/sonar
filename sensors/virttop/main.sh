#!/bin/bash

sensor=$1
progName=$2

virt-top --script --stream | sed -u '{/virt-top.*/d}' | sed -u '{/ID.*/d}' | awk '{ print $7; fflush() }' | \
while read line ; do
        ((res_timestamp = $(date +%s)))
        toPrint="$sensor,$res_timestamp,$progName,none,$line"
        echo $toPrint
done
