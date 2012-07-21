#!/bin/bash

# Update configuration files
cp *.json /opt/rain/config
cd /opt/rain/

# Lauch Rain
python start.py driver config/rain.config.specj.json 1>&2 rain.log &
