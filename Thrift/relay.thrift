namespace java de.tum.in.storm.relay 

typedef i64 long
typedef i32 int

service RelayService {

	void execute(1:string code);

	list<int> getPids();
	
	void kill(1:int pid); 
}
