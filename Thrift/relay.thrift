namespace java de.tum.in.storm.relay 

typedef i64 long
typedef i32 int

service RelayService {

	// Deprecated
	void execute(1:string code);
	
	int launch(1:binary data, 2:string name)

	int launchNoWait(1:binary data, 2:string name)	

	bool isAlive(1:int pid)
	
	bool kill(1:int pid)
	
	bool pollForMessage(1:binary data, 2:string name, 3:string message)
	
	bool waitForMessage(1:binary data, 2:string name, 3:string message, 4:string file)
}
