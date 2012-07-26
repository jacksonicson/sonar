#!/bin/bash

RELAY=/opt/relay

# Remove old files and create the directory
mkdir $RELAY
rm -rf $RELAY/*

# Update the files
cp relay.zip $RELAY
cd $RELAY
unzip relay.zip
rm relay.zip

# Update service script
cp relay.service /etc/systemd/system/

# Restart the service
systemctl disable relay.service
systemctl restart relay.service
