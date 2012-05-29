namespace java de.tum.in.sonar.collector 

typedef i64 long
typedef i32 int

struct Identifier {
	1:long timestamp,
	3:int sensor,
	2:string hostname,
}

struct TimeSeriesPoint {
	1:long value,
	3:set<string> labels,
}

struct File {
	1:string filename,
	2:string description,
	3:string file,
	4:set<string> labels,
}


service CollectService {
	void logMessage(1:Identifier id, 2:string message),
	 	
	void logMetric(1:Identifier id, 2:TimeSeriesPoint value),
	 
	void logResults(1:Identifier id, 2:File file),
}

service ManagementService {
	// TODO
}