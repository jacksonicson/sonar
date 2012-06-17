#!/bin/bash
#
# Fedora-Service Update notification daemon
#
# Author:       Andreas Wolke
#
# chkconfig:    1000 50 50
#
# description:  Sonar SensorHub service
#
# processname:  SensorHub
#

. /etc/init.d/functions

RETVAL=0;
 
LOCATION = "/home/jack/work/sonar/sonar/SensorHub/start.sh"
 
start() {
        initlog -c "echo -n Starting SensorHub service: "
        $LOCATION &
        success $"SensorHub startup"
        echo
}
 
stop() {
echo "Stopping SensorHub-Service"
        initlog -c "echo -n Stopping SensorHub service: "
        killproc sensorhub
        echo
}
 
restart() {
stop
start
}
 
case "$1" in
start)
start
;;
stop)
stop
;;
restart)
restart
;;
*)
echo $"Usage: $0 {start|stop|restart}"
exit 1
esac
 
exit $RETVAL
