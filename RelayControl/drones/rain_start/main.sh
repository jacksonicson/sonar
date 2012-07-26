#!/bin/bash

# Update configuration files
cp *.json /opt/rain/config
# cp -r load /opt/rain/config/
cd /opt/rain/

rm -rf /opt/rain/rain.pid
rm -rf /opt/rain/rain.log

sleep 1

# Launching Rain
python start.py driver config/rain.config.specj.json > rain.log 2>&1 &
