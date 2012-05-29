namespace java de.tum.in.sonar.collector 

typedef i64 long
typedef i32 int


service LogService {

}

service TsdService {
	void log(1:long timestamp, 2:long value), 
}

service QueryService {

}

service ConfigurationService {

}