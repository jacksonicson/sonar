namespace java de.tum.in.sonar.collector 

typedef i64 long
typedef i32 int

struct Identifier {
	1:long timestamp,
	3:string sensor,
	2:string hostname,
}

struct MetricReading {
	1:double value,
	3:set<string> labels,
}

struct LogMessage {
	1: int logLevel,
	2: string logMessage,
	3: string programName,
	4: i64 timestamp,
}

struct LogsQuery {
	1:long startTime,
	2:long stopTime,
	3:string sensor,
	4:string hostname, 
}

struct File {
	1:string filename,
	2:string description,
	3:string file,
	4:set<string> labels,
}

struct TransferableTimeSeriesPoint {
	1:long timestamp,
	2:double value,
	3:set<string> labels,
}

struct TimeSeriesQuery {
	1:long startTime,
	2:long stopTime,
	3:string sensor,
	5:set<string>labels,
	4:optional string hostname,
}

struct Parameter {
	1:string key,
	2:string value
}

enum SensorType {
  METRIC = 0,
  LOG = 1
}

struct SensorConfiguration {
	1:long interval,
	2:list<Parameter> parameters, 
	3:SensorType sensorType
}

struct BundledSensorConfiguration {
	1:string sensor,
	2:string hostname,
	3:set<string> labels,
	4:SensorConfiguration configuration,
	5:bool active,
}

struct SensorToWatch {
	1:string hostname,
	2:string sensor
}

struct NotificationData {
	1:Identifier id,
	2:MetricReading reading,
}

service CollectService {
	void logMessage(1:Identifier id, 2:LogMessage message),
	 	
	void logMetric(1:Identifier id, 2:MetricReading value),
	 
	void logResults(1:Identifier id, 2:File file),
}

service NotificationService {
	void subscribe(1:string ip, 2:int port, 3:set<SensorToWatch> watchlist),
	
	void unsubscribe(1:string ip),
}

service NotificationClient {
	void receive(1:list<NotificationData> data)
}

service ManagementService {

	// query for logs
	list<LogMessage> queryLogs(1:LogsQuery query),
	
	// Query Section
	list<TransferableTimeSeriesPoint> query(1:TimeSeriesQuery query),
	
	
	// Sensor Section
	binary fetchSensor(1:string name),
	
	string sensorHash(1:string name),
	
	void deploySensor(1:string name, 2:binary file),
	
	set<string> getAllSensors(),
	
	bool  hasBinary(1:string sensor),
	
	set<string> getSensorLabels(1:string sensor),
	
	void delSensor(1:string sensor),
	
	void setSensorLabels(1:string sensor, 3:set<string> labels),
	
	void setSensorConfiguration(1:string sensor, 2:SensorConfiguration configuration),
	
	SensorConfiguration getSensorConfiguration(1: string sensor),
	
	set<string> getSensorNames(),
	
	
	// Host Section
	void addHost(1:string hostname),
	
	set<string> getAllHosts(),
	
	void delHost(1:string hostname),
	
	void setHostLabels(1:string hostname, 2:set<string> labels),
	
	set<string> getLabels(1:string hostname), 
	
	void setSensor(1:string hostname, 2:string sensor, 3:bool activate),
	
	set<string> getSensors(1:string hostname),
	
	BundledSensorConfiguration getBundledSensorConfiguration(1:string sensor, 2:string hostname),
}
