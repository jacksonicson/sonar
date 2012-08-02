#!/bin/bash

sleep 1

# Release dhclient
dhclient -r
ifdown eth0

# Update hostname
sed -i "s/vmt/test7/g" /etc/sysconfig/network

# Change scripts
cp ifcfg-eth0 /etc/sysconfig/network-scripts/

shutdown -h now
