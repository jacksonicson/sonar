#!/bin/bash

startup=$1
interface='eth0'

timestamp_new=0
value_new=0

function readBytes()
{
        line=$(cat /proc/net/dev | grep $interface | cut -d ':' -f 2 | awk '{print $1}')
        value_new=$line
        timestamp_new=$(date +%s)
}

function bytesPerSecond()
{
        ((vel = value_new - value_old))
        ((del = timestamp_new - timestamp_old))
        ((bps = vel / del / 1024))
        echo $bps
}

# Handle startup
if ((startup == 1))
then
        $(rm /var/sonar/procnet)
        
        # read current bytes
        readBytes
        
        # Get time 
        timestamp_now=$(date +%s)
        
        # Build string
        line="$timestamp_now,$received_bytes"
        
        # Write the stuff
        $(echo $line > /var/sonar/procnet)
fi


# Call function for reading bytes
readBytes

# Ready old bytes
value=$(cat /var/sonar/procnet)
IIS=$IFS
IFS=","
tmp=($value)
IFS=$IIS

timestamp_old=${tmp[0]}
value_old=${tmp[1]}

bytesPerSecond

line="$timestamp_new,$value_new"
$(echo $line > /var/sonar/procnet)


