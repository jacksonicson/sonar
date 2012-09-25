#!/bin/bash

# Name of the sensor passed as first cmdline argument
sensor=$1

device='sda'
if [ $# -eq 2 ]
then
	# Read parameters
	device=$2
	device=`echo $device | sed 's/device=//'`
fi

# End flag which is use to terminate the main loop
end=0
exitThis() 
{
  end=1
}

trap 'exitThis' TERM KILL


exec 3< <(iostat -x -d 3 $device)
PID=$!
while [ $end -lt 1 ] && read out; do

	out=`echo $out | grep --line-buffered $device`
	if [ "$out" = "" ]; then
		continue
	fi

	arr=$(echo $out | tr " " ",")
	IFS="," read -ra STR_ARRAY <<< "$arr"

	# Timestamp
	res_timestamp=$(date +%s)

	# Log 
	res_name='svctime'
	res_hostname='none'
	res_value=${STR_ARRAY[12]}
	echo "$sensor,$res_timestamp,$res_name,$res_hostname,$res_value"

	res_name='await'
	res_hostname='none'
	res_value=${STR_ARRAY[9]}
	echo "$sensor,$res_timestamp,$res_name,$res_hostname,$res_value"

	res_name='avgqu-sz'
	res_hostname='none'
	res_value=${STR_ARRAY[8]}
	echo "$sensor,$res_timestamp,$res_name,$res_hostname,$res_value"

done <&3
exec 3<&-
kill $PID
exit 0

