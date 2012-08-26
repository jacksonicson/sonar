#!/bin/bash

sensor=$1

pid=-1

cleanup()
{
        kill $pid
}

trap "exit" SIGTERM

virt-top --script --stream | sed -u '{/virt-top.*/d}' | sed -u '{/ID.*/d}' | awk '{ printf "%s,%s\n",$7,$10; fflush() }' | \
while read line ; do
        ((res_timestamp = $(date +%s)))

        IIS=$IFS
        IFS=","
        tmp=($line)
        IFS=$IIS

        cpu=${tmp[0]}
        domain=${tmp[1]}

        toPrint="$sensor,$res_timestamp,none,$domain,$cpu"
        echo $toPrint
done &

pid=$!

wait