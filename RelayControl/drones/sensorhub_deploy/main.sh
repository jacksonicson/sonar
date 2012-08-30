#!/bin/bash

systemctl stop sensorhub.service

SENSORHUB=/opt/sensorhub

# Remove old files and create the directory
mkdir $SENSORHUB
rm -rf $SENSORHUB/*

# Update the files
cp sensorhub.zip $SENSORHUB

# Install psutil
mkdir /mnt/share
mount -t nfs monitor0:/mnt/arr0/share /mnt/share
cd /mnt/share/packages/
rm -f /tmp/psutil-0.5.1.tar.gz
cp psutil-0.5.1.tar.gz /tmp
cd /tmp
tar -xzf psutil-0.5.1.tar.gz
cd psutil-0.5.1
python setup.py install
cd $SENSORHUB
umount /mnt/share

# Remove old sensor dir
rm -rf /tmp/sonar

# Unzip
cd $SENSORHUB
unzip sensorhub.zip
rm sensorhub.zip

# Update service script
cp sensorhub.service /etc/systemd/system/

# Restart the service
systemctl enable sensorhub.service
systemctl stop sensorhub.service
systemctl start sensorhub.service

exit 0