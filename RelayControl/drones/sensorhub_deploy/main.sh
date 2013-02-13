#!/bin/bash

systemctl stop sensorhub.service

SENSORHUB=/opt/sensorhub

# Remove old files and create the directory
if [ -d $SENSORHUB ]; then
	rm -rf $SENSORHUB
	mkdir $SENSORHUB
else
	mkdir $SENSORHUB
fi

# Update the files
cp sensorhub.zip $SENSORHUB

# Install psutil
SHARE=/mnt/share
if [ -d $SHARE ]; then
	umount $SHARE
	rm -rf $SHARE
	mkdir $SHARE
else
	umount $SHARE
	mkdir $SHARE
fi

mount -t nfs monitor0:/mnt/arr0/share /mnt/share

echo "installing psutil..."
cd /mnt/share/packages/
rm -f /tmp/psutil-0.5.1.tar.gz
cp psutil-0.5.1.tar.gz /tmp
cd /tmp
tar -xzf psutil-0.5.1.tar.gz
cd psutil-0.5.1
python setup.py install

echo "umounting"
cd $SENSORHUB
umount /mnt/share

echo "removing old sensor dir..."
rm -rf /tmp/sonar

# Unzip
echo "unzipping..."
cd $SENSORHUB
unzip sensorhub.zip
rm sensorhub.zip

# Update service script
echo "copy sensorhub.service script"
cp sensorhub.service /etc/systemd/system/

# Restart the service
echo "restarting service..."
systemctl enable sensorhub.service
systemctl stop sensorhub.service
systemctl start sensorhub.service

exit 0