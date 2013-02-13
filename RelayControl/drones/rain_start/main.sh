#!/bin/bash

# Update configuration files
rm -rf /opt/rain/config/*
cp -f *.json /opt/rain/config

cd /opt/rain/

rm -rf /opt/rain/*.pid
rm -rf /opt/rain/*.log


# Launching Rain
python start.py driver config/rain.config.specj.json > rain.log 2>&1 &
