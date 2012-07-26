#!/bin/bash

SENSORHUB=/opt/sensorhub

# Remove old files and create the directory
mkdir $SENSORHUB
rm -rf $SENSORHUB/*

# Update the files
cp sensorhub.zip $SENSORHUB
cd $SENSORHUB
unzip sensorhub.zip
rm sensorhub.zip


# Update service script
cp sensorhub.service /etc/systemd/system/

# Restart the service
systemctl disable sensorhub.service
# systemctl restart sensorhub.service
# test