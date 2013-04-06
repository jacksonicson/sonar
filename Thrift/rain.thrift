namespace java de.tum.in.storm.rain 

typedef i64 long
typedef i32 int

service RainService {

	bool startBenchmark(1:long controllerTimestamp);
	
	list<string> getTrackNames();
	
	long getRampUpTime();
	
	long getRampDownTime();
	
	long getDurationTime();
}
