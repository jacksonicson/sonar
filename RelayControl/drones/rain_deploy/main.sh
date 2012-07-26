#!/bin/bash

RAIN=/opt/rain

# Remove old files and create the directory
mkdir $RAIN
rm -rf $RAIN/*

# Update the files
cp driver.zip $RAIN
cd $RAIN
unzip driver.zip
rm driver.zip
