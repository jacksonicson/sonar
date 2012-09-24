#!/bin/bash

# Name of the sensor passed as first cmdline argument
sensor=$1

# Fields
# echo "USER    NICE    SYS   IDLE   IOWAIT  IRQ  SOFTIRQ  STEAL  GUEST"

# End flag which is use to terminate the main loop
end=0
exitThis() 
{
  end=1
}

# Register sigkill handle
trap exitThis SIGKILL

# Main loop which reads the /proc/stat file regularly
while [ $end -eq 0 ] 
do
	# Read all words from /proc/stat to the array CPU
	read -a CPU < /proc/stat
	
	# Check fi there are 5 words and if the first word is "cpu"
	if [[ ${#CPU[*]} -lt 5 && "${CPU[0]}" != "cpu" ]]; then
		echo "unexpected /proc/stat format: <${CPU[*]}>"
		exit 1
	fi
	
	# Remove first array element
	unset CPU[0]
	CPU=("${CPU[@]}")

	# Sum up all values (=100%)
	TOTAL=0
	for t in "${CPU[@]}"; do ((TOTAL+=t)); done
	
	# Difference of current total and previous total (0 if not defined)
	((DIFF_TOTAL=$TOTAL-${PREV_TOTAL:-0}))

	# Iterate over all array indices
  	for i in ${!CPU[*]}; do
		# Calc percentage
		# Comma to the right which allows float representation
		OUT_INT=$((1000*(${CPU[$i]}-${PREV_STAT[$i]:-0})/DIFF_TOTAL))
		
		# Extract float representation using modulo operation
		OUT[$((i*2))]=$((OUT_INT/10))
		OUT[$((i*2+1))]=$((OUT_INT%10))
	done

	# log STEAL value
	# indices in the OUT array which contains the steal time 
	index=$((7*2))
	index2=$(($index+1))
	res_timestamp=$(date +%s)
	res_name='steal'
	res_hostname='none'
	res_value="${OUT[$index]}.${OUT[$index2]}"
	echo "$sensor,$res_timestamp,$res_name,$res_hostname,$res_value"

	# Log 
	index=$((0*2))
	index2=$(($index+1))
	res_name='user'
	res_hostname='none'
	res_value="${OUT[$index]}.${OUT[$index2]}"
	echo "$sensor,$res_timestamp,$res_name,$res_hostname,$res_value"

	# Log 
	index=$((4*2))
	index2=$(($index+1))
	res_name='iowait'
	res_hostname='none'
	res_value="${OUT[$index]}.${OUT[$index2]}"
	echo "$sensor,$res_timestamp,$res_name,$res_hostname,$res_value"

	# Log 
	index=$((2*2))
	index2=$(($index+1))
	res_name='sys'
	res_hostname='none'
	res_value="${OUT[$index]}.${OUT[$index2]}"
	echo "$sensor,$res_timestamp,$res_name,$res_hostname,$res_value"
		
	# store cpu counters for next iteration
	PREV_STAT=("${CPU[@]}")
	PREV_TOTAL="$TOTAL"
	
	# sleep until next run
	sleep 3
done
exit 0

