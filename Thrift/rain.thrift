namespace java de.tum.in.storm.rain 

typedef i64 long
typedef i32 int

struct Profile {
	1:string destTrackName;
	2:long interval;
	3:long transitionTime;
	4:long numberOfUsers;
	5:string mixName;
	6:string name;
}

service RainService {

	bool startBenchmark(1:long controllerTimestamp);
	
	bool dynamicLoadProfile(1:Profile profile);
	
	list<string> getTrackNames();
	
	long getRampUpTime();
	
	long getRampDownTime();
	
	long getDurationTime();
}
