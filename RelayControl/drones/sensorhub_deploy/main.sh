#!/bin/bash

SENSORHUB=/opt/sensorhub

# Remove old files and create the directory
mkdir -f $SENSORHUB
rm -rf $SENSORHUB/*

# Update the files
cp sensorhub.zip $SENSORHUB
cd $SENSORHUB
unzip sensorhub.zip

# Update service script
cp sensorhub.service /etc/systemd/system/

# Restart the service
systemctl enable sensorhub.service
systemctl restart sensorhub.service