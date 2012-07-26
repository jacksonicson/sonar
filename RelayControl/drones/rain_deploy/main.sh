#!/bin/bash

RAIN=/opt/rain

# Remove old files and create the directory
mkdir $RAIN
rm -rf $RAIN/*

# Update the files
cp rain.zip $RAIN
cd $RAIN
unzip rain.zip
rm rain.zip
