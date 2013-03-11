# Sonar
Sonar is a bundle of programs that were created to control and monitor a cloud computing test bed in research environments. Its architecture is designed to scale horizontally which allows its application in larger scale infrastructures as well. 

1. Monitoring: An efficient monitoring solution which stores all data in an HBase database. 
2. Relay: A leightweight tool which supports the implementation of a software-reconfiguration process for cloud test bed environments.

## Monitoring
Sonar monitoring consits of four subprojects: 
* Sensors: A number of small programs used to measure metrics on a system. For example, there are two programs that measure the CPU and memory load. 
* SensorHub: A service that controls a number of Sensor instances and recieves their metric readings. The data is aggregated and then forwarded to the Collector. 
* Collector: A horizontal scalable service that receives monitoring data from the SensorHub. Everything is stored in an Apache HBase database. 
* WebUI: A web user interface to configure which Sensors are running on which systems. In addition it provies interfaces for querying and browsing recorded log-message or metric readings. 

### Sytem dependencies: 
* Python
	* Apache Thrift
	* EasyInstall
	* PyYaml
* NTP (Network Time Protocol)

* SensorHub and Sensors
	* yum group install "Development Tools"
	* yum install python-devel
	* [psutil] 
	
* Relay and RelayControl
	* Python Twisted [twisted]
	* Zope Interfaces [zopei]
	* Mako Template Engine [mako]


## Relay
Relay was designed for research environments where security is of no concern. We do not recommend to use Relay in any productive environment therefore. Sonar monitoring does depend in any way on the Relay system. 

## OpenTSDB
The architecture is similar to the one of OpenTSDB but differs in a number of points: 
* Apache Thrift is used for all telmetry and storage
* Support for storing log messages
* Sensor programs are distributed and installed by Sonar
* Dynamic configuration of sensors from a central location


[psutil]: https://code.google.com/p/psutil/  "PsUtil"
[mako]: http://www.makotemplates.org/ "Mako Template Engine"
[zopei]: https://pypi.python.org/pypi/zope.interface#download "Zope Interfaces"
[twisted]: http://twistedmatrix.com/trac/ "Twisted"