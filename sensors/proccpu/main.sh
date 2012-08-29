#!/bin/bash

# Fields
# echo "USER    NICE    SYS   IDLE   IOWAIT  IRQ  SOFTIRQ  STEAL  GUEST"

end=0
exitThis() 
{
  end=1
}

trap exitThis SIGKILL


while [ $end -eq 0 ] 
do
	# Read all words to the array CPU
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
		# Calc percentage and shift comma to the right
		OUT_INT=$((1000*(${CPU[$i]}-${PREV_STAT[$i]:-0})/DIFF_TOTAL))
		
		# Extract separate values by using modulo
		OUT[$((i*2))]=$((OUT_INT/10))
		OUT[$((i*2+1))]=$((OUT_INT%10))
	done

	# steal time
	index=$((7*2))
	index2=$(($index+1))
	sensor=$1
	res_timestamp=$(date +%s)
	res_name='steal'
	res_hostname='none'
	res_value="${OUT[$index]}.${OUT[$index2]}"
	echo "$sensor,$res_timestamp,$res_name,$res_hostname,$res_value"
		

	PREV_STAT=("${CPU[@]}")
	PREV_TOTAL="$TOTAL"
	sleep 1
done
exit 0

