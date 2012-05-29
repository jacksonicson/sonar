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
	2:set<string> labels,
}

struct File {
	1:string filename,
	2:string description,
	3:string file,
	4:set<string> labels,
}

service LogService {
	void log(1:Identifier id, 2:string message), 	
}


service TsdService {
	void log(1:Identifier id, 2:TimeSeriesPoint value), 
}

service ResultService {
	void writeResults(1:Identifier id, 2:File file),
}

service QueryService {
	// TODO
}

service ConfigurationService {
	// TODO
}