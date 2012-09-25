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

# Register sigkill handle
trap exitThis SIGKILL

while [ $end -eq 0 ] 
do
	n1=5
	out=`iostat -x -d $device | grep $device `
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

	# sleep until next run
	sleep 3
done
exit 0
