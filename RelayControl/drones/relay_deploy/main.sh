#!/bin/bash

RELAY=/opt/relay

# Remove old files and create the directory
if [ -d $RELAY ]; then
	rm -rf $RELAY/*
else
	mkdir $RELAY
fi

# Update the files
cp relay.zip $RELAY
cd $RELAY
unzip relay.zip
rm relay.zip

# Update service script
cp relay.service /etc/systemd/system/

# Restart the service
systemctl enable relay.service
systemctl restart relay.service
