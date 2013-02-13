namespace java de.tum.in.storm.times 

typedef i64 long
typedef i32 int

struct Element {
	1:long timestamp, // Timestamp (should correlate with the frequency)
	2:long value, // Value of the TS element
}

struct TimeSeries {
	1:string name, // name of the TS
	2:int frequency, // interval duration in seconds
	3:list<Element> elements, // elements of the TS
}

service TimeService {
	list<string> find(1:string pattern);

	TimeSeries load(1:string name);
	
	void remove(1:string name);
	
	void create(1:string name, 2:int frequency);
	
	void append(1:string name, 2:list<Element> elements);
}
