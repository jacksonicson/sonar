# Sonar
Sonar is a data center monitoring solution that is designed to gather vast amounts of server metrics an log data. All data is stored in HBase by one or multiple data collection daemons. 

## Components
* Sensors: A number of small programs dedicated to measure metrics on a system. For example, there are two programs that measure the CPU and memory load. A sensor gathers metric readings in an interval and prints the reading on its stndard output stream. 
* SensorHub: Runs on each monitored node. It starts and controls sensor program instances and reads their metric readings on the standard output stream. All data is aggregated and forwarded to a Collector service. 
* Collector: A horizontal scalable service that receives monitoring data from SensorHubs. All data is stored in an HBase database. In addition, the Collector manages all meta data about the infrastructure.
* WebUI: A web user interface to configure which sensor programs should be running on a particular node. In addition it provies interfaces for querying and browsing recorded log-message or metric readings. 

## OpenTSDB
The architecture is similar to the one of OpenTSDB but differs at some points: 
* Apache Thrift is used for all telemetry and storage
* Supports log messages
* Sensor programs are distributed and installed by Sonar automatically
* Dynamic (re-)configuration of sensors from a central location
* Supports dynamic environments like virtualized data centers