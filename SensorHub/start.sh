#!/bin/bash

test() {
	cd /home/jack/work/sonar/sonar/SensorHub/
	python sensorhub.py
}

cd /home/jack/work/sonar/sonar/SensorHub
echo $(dirname $0)
echo $(pwd)
test


