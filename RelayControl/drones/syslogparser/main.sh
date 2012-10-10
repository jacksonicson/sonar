#!/bin/bash
ARRAY=(`find /var/log -name "message*"`)
for i in ${ARRAY[*]}; do
    python SysLogParser.py "$i"
done
