namespace java de.tum.in.storm.relay 

typedef i64 long
typedef i32 int

service RelayService {

	void execute(1:string code);

	int launch(1:binary data, 2:string name)

	list<int> getPids();
	
	void kill(1:int pid); 
}
