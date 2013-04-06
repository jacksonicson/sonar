namespace java de.tum.in.storm.iaas 

typedef i64 long
typedef i32 int

service Infrastructure {

	string allocateDomain(); 

	bool isDomainReady(1:string hostname);
	
	bool deleteDomain(1:string hostname);
}
