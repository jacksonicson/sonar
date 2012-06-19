namespace java de.tum.in.sonar.collector.tsdb.gen 

typedef i64 long
typedef i32 int

struct CompactPoint {
	1:long timestamp,
	2:double value,
}

struct CompactTimeseries {
	1:list<CompactPoint> points,
}
