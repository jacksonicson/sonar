# Sonar
Sonar is a data center monitoring solution that is designed to gather vast amounts of server metrics an log data. All data is stored in HBase by one or multiple data collection daemons. 

## Components

![Sonar Architecture](https://github.com/jacksonicson/sonar/blob/master/architecture.png?raw=true "Sonar Architecture")

* Sensors: A number of small programs dedicated to measure metrics on a system. For example, there are two programs that measure the CPU and memory load. A sensor gathers metric readings in an interval and prints the reading on its stndard output stream. 
* SensorHub: Runs on each monitored node. It starts and controls sensor program instances and reads their metric readings on the standard output stream. All data is aggregated and forwarded to a Collector service. 
* Collector: A horizontal scalable service that receives monitoring data from SensorHubs. All data is stored in an HBase database. In addition, the Collector manages all meta data about the infrastructure.
* WebUI: A web user interface to configure which sensor programs should be running on a particular node. In addition it provies interfaces for querying and browsing recorded log-message or metric readings. 

## Differences to OpenTSDB
The architecture is similar to the one of OpenTSDB but differs at some points: 
* Apache Thrift is used for all telemetry and storage
* Supports log messages
* Sensor programs are distributed and installed by Sonar automatically
* Dynamic (re-)configuration of sensors from a central location
* Supports dynamic environments like virtualized data centers

## Installation

Sonar needs access to an HBase cluster and a Redis key-value store. 

### Monitored Node
Each monitored node (Linux) runs the SensorHub daemon with the following dependencies: 
* Python 2.7 (with development packages)
* Python Easy Install
* [Apache Thrift for Python](http://thrift.apache.org/)
* [PyYaml](https://bitbucket.org/xi/pyyaml)
* [Psutil 0.5.1](https://code.google.com/p/psutil/)

Further libraries might be required, depending on the snsor programs used. 

### Collector Node
The collector is based on Java. The project contains all required JAR libraries. 

### WebUI
Based on [NodeJS](http://nodejs.org/). The project contains all required libraries.
