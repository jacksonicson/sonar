#!/bin/bash

# Template variables
hostname=$hostname

# Release dhclient
dhclient -r
ifdown eth0

# Update hostname
sed -i "s/vmt/$hostname/g" /etc/sysconfig/network

# Change scripts
cp ifcfg-eth0 /etc/sysconfig/network-scripts/