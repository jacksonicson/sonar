#!/bin/bash

# Target installation directory of rain
RAIN=/opt/rain

chmod 600 id_rsa 
# Create directory if necessary
if [ ! -d $RAIN ]
then
	mkdir $RAIN
fi

# Clean all files from directory
rm -rf $RAIN/*

# Copy binary using public/privat key login 
scp -i id_rsa root@monitor0.dfg:/mnt/arr0/share/packages/rain/driver.zip $RAIN

# Switch directory and unzip driver
cd $RAIN
unzip driver.zip
rm driver.zip

