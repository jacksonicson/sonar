#!/bin/bash

sleep 1

# Release dhclient
dhclient -r
# ifdown eth0

# Update hostname
sed -i "s/vmt/$hostname/g" /etc/sysconfig/network
sed -i "s/vmt/$hostname/g" /etc/hostname

# Change scripts
cp ifcfg-eth0 /etc/sysconfig/network-scripts/

shutdown -h now
