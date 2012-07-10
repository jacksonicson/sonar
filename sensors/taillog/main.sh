#!/bin/bash
sensor=$1

trap 'kill $(jobs -p)' EXIT
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for (( c=2; c<=$#; c++ ))
do
    export progName=$(echo ${!c} | cut -d"=" -f1)
    export logFile=$(echo ${!c} | cut -d"=" -f2)
	sh $DIR/logMonitor.sh $sensor $progName $logFile &
done

wait
