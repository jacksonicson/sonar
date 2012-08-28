#!/bin/bash

sensor=$1
pid=-1

cleanup_term()
{
	# echo 'sigterm detected'
	# echo "killing $pid"
	pkill -TERM -P $$
	exit 0
}

trap cleanup_term SIGTERM

flag=0
set_flag()
{
	# echo 'setting flat'
	flag=1
}

# grep --line-buffered Cpu | sed -u 's/^.\{70\}[[:space:]]*//g' | sed -u 's/%st//' |

top -b -d 3 | grep --line-buffered Cpu | sed -u 's/^.\{70\}[[:space:]]*//g' | sed -u 's/%st//' | { 
trap set_flag SIGTERM
while read line ; do
        (( res_timestamp = $(date +%s) ))
        toPrint="$sensor,$res_timestamp,none,none,$line"
	echo $toPrint
	if [ $flag -eq 1 ] ; then
		# echo 'exiting'
		break
	fi
done 
# echo 'done'
exit 0
} &

pid=$!
echo $!
wait
exit 0



