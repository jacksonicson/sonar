package de.tum.in.sonar.collector.tsdb;

import java.util.ArrayList;
import java.util.List;

public class TimeSeriesFragment {

	private List<DataPoint> dataPoints = new ArrayList<DataPoint>(60);

	public TimeSeriesFragment() {
		// Default constructor
	}

	void addPoint(DataPoint dataPoint) {

	}

	void addSegment(byte[] data) {
		// Data contains a list of thrift encoded data points
		// The purpos is just to reduce the number of columns and therefore rows
		// - data duplication
	}
}
