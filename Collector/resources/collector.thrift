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

service CollectService {
	void logMessage(1:Identifier id, 2:string message),
	 	
	void logMetric(1:Identifier id, 2:MetricReading value),
	 
	void logResults(1:Identifier id, 2:File file),
}

service ManagementService {
	
	list<TransferableTimeSeriesPoint> query(1:TimeSeriesQuery query),
}
