#!/bin/bash

mkdir /mnt/share
mount -t nfs monitor0:/mnt/arr0/share /mnt/share
mysql -uroot -prooter < /mnt/share/dumps/specdb\ txrate\ 60.sql
umount /mnt/share

echo "done"