package de.tum.in.sonar.collector.tsdb;

public class QueryException extends Exception {

	public QueryException(Throwable e) {
		super(e);
	}

	public QueryException() {
	}

}
