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

	public TimeSeriesFragment() {
		// Default constructor
	}

	void addPoint(TimeSeriesPoint dataPoint) {
		dataPoints.add(dataPoint);
	}

	void addSegment(long hoursSinceEpoch, byte[] data) throws TException {
		logger.info("deserializing segment");

		TDeserializer deserializer = new TDeserializer();
		CompactTimeseries ts = new CompactTimeseries();
		deserializer.deserialize(ts, data);

		for (CompactPoint point : ts.getPoints()) {
			TimeSeriesPoint dp = new TimeSeriesPoint();
			dp.setTimestamp(hoursSinceEpoch + point.getTimestamp());
			dp.setValue(point.getValue());
			dataPoints.add(dp);
		}

		logger.info("segment data points: " + dataPoints.size());
	}

	public int size() {
		return dataPoints.size();
	}

	@Override
	public Iterator<TimeSeriesPoint> iterator() {
		return dataPoints.iterator();
	}
}
