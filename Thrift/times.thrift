namespace java de.tum.in.storm.times 

typedef i64 long
typedef i32 int

struct Element {
	1:long timestamp,
	2:long value,
}

struct TimeSeries {
	1:string name,
	2:int frequency,
	
	3:list<Element> elements,
}

service TimeService {

	TimeSeries load(1:string name);
	
	void create(1:string name, 2:int frequency);
	
	void append(1:string name, list<Element> elements);
}
