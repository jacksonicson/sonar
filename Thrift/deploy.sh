#!/bin/bash

hosts=( 'playground' )

for host in ""${hosts[@]}""
do
	# Remove the directory
	ssh root@$host "rm -rf /opt/sensorhub;mkdir/opt/sensorhub"
	
	# Copy over the updated version
	scp -r ./SensorHub/* root@$host:/opt/sensorhub/
	
	echo $host
done

