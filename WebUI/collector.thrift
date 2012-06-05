namespace java de.tum.in.sonar.collector 

typedef i64 long
typedef i32 int

struct Identifier {
	1:long timestamp,
	3:string sensor,
	2:string hostname,
}

struct MetricReading {
	1:long value,
	3:set<string> labels,
}

struct File {
	1:string filename,
	2:string description,
	3:string file,
	4:set<string> labels,
}

struct TransferableTimeSeriesPoint {
	1:long timestamp,
	2:long value,
	3:set<string> labels,
}

struct TimeSeriesQuery {
	1:long startTime,
	2:long stopTime,
	3:string sensor,
	5:set<string>labels,
	4:optional string hostname,
}

struct SensorConfiguration {
	1:long interval,
}

struct BundledSensorConfiguration {
	1:string sensor,
	2:string hostname,
	3:set<string> labels,
	4:SensorConfiguration configuration,
}

service CollectService {
	void logMessage(1:Identifier id, 2:string message),
	 	
	void logMetric(1:Identifier id, 2:MetricReading value),
	 
	void logResults(1:Identifier id, 2:File file),
}

service ManagementService {
	
	list<TransferableTimeSeriesPoint> query(1:TimeSeriesQuery query),
	
	
	binary fetchSensor(1:string name),
	
	void deploySensor(1:string name, 2:binary file),
	
	set<string> getAllSensors(),
	
	bool  hasBinary(1:string sensor),
	
	set<string> getSensorLabels(1:string sensor),
	
	void delSensor(1:string sensor),
	
	void addHost(1:string hostname),
	
	void delHost(1:string hostname),
	
	void setHostLabels(1:string hostname, 2:set<string> labels),
	
	set<string> getLabels(1:string hostname), 
	
	void setSensor(1:string hostname, 2:string sensor, 3:bool activate),
	
	set<string> getSensors(1:string hostname),
	
	void setSensorLabels(1:string sensor, 3:set<string> labels),
	
	void setSensorConfiguration(1:string sensor, 2:SensorConfiguration configuration),
	
	BundledSensorConfiguration getBundledSensorConfiguration(1:string sensor, 2:string hostname),
}
