#!/bin/bash

RAIN=/opt/rain

# Remove old files and create the directory
mkdir $RAIN
rm -rf $RAIN/*

# Files are in the NFS share
if [ -d /mnt/share ]; then
echo "ATTENTION: mounting /mnt/share"
mount -t nfs monitor0:/mnt/arr0/share /mnt/share

# Update the files
cp /mnt/share/packages/rain/driver.zip $RAIN
cd $RAIN
unzip driver.zip
rm driver.zip

echo "umount /mnt/share"
umount /mnt/share

fi