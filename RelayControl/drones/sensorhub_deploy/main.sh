#!/bin/bash

SENSORHUB=/opt/sensorhub

# Install psutil
mount -t nfs monitor0:/mnt/arr0/share /mnt/share
cd /mnt/share/packages/psutil-0.5.1/
python setup.py install
cd
umount /mnt/share

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
systemctl restart sensorhub.service
