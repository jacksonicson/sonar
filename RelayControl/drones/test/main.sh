#!/bin/bash

cd /opt/glassfish/current/glassfish/bin
./startserv

close() {
	./stopserv
}

trap 'close' TERM

while :			# This is the same as "while true".
do
        sleep 60	# This script is not really doing anything.
done