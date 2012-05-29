namespace de.tum.in.sonar.collector 

typedef i64 long
typedef i32 int


service LogService {
	long add(1:int num1, 2:int num2),
	
	long multiply(1:int num1, 2:int num2),
}

service QueryService {

}

service ConfigurationService {

}