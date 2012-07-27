#!/bin/bash

# Update configuration files
cp -f *.json /opt/rain/config
mkdir /opt/rain/config/load
cp -f load/* /opt/rain/config/load

cd /opt/rain/

rm -rf /opt/rain/rain.pid
rm -rf /opt/rain/rain.log

sleep 1

# Launching Rain
python start.py driver config/rain.config.specj.json > rain.log 2>&1 &
