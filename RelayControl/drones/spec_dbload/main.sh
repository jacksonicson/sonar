#!/bin/bash

if [ ! -d "/mnt/share" ]; then
	mkdir /mnt/share
fi

# Umount before mounting
umount /mnt/share

# Mount NFS share with dumpfile
mount -t nfs monitor0:/mnt/arr0/share /mnt/share

# Load dumpfile
mysql -uroot -proot specj < /mnt/share/dumps/specdb\ txrate\ 60.sql

# Umount NFS share
cd /
umount /mnt/share

# Print done
echo "done"
