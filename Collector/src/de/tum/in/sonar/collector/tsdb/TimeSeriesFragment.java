package de.tum.in.sonar.collector.tsdb;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.apache.thrift.TDeserializer;
import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.tsdb.gen.CompactPoint;
import de.tum.in.sonar.collector.tsdb.gen.CompactTimeseries;

public class TimeSeriesFragment implements Iterable<TimeSeriesPoint> {

	private static final Logger logger = LoggerFactory.getLogger(TimeSeriesFragment.class);

	private List<TimeSeriesPoint> dataPoints = new ArrayList<TimeSeriesPoint>(60);

	TimeSeriesFragment() {
		// Default constructor
	}

	void addPoint(TimeSeriesPoint dataPoint) {
		dataPoints.add(dataPoint);
	}

	void addSegment(long hoursSinceEpoch, byte[] data) throws TException {
		TDeserializer deserializer = new TDeserializer();
		CompactTimeseries ts = new CompactTimeseries();
		deserializer.deserialize(ts, data);

		for (CompactPoint point : ts.getPoints()) {
			long timestamp = hoursSinceEpoch + point.getTimestamp();
			double value = point.getValue();
			TimeSeriesPoint dp = new TimeSeriesPoint(timestamp, value);
			dataPoints.add(dp);
		}
	}

	public int size() {
		return dataPoints.size();
	}

	@Override
	public Iterator<TimeSeriesPoint> iterator() {
		return dataPoints.iterator();
	}
}
