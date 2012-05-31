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

public class TimeSeriesFragment implements Iterable<DataPoint> {

	private static final Logger logger = LoggerFactory.getLogger(TimeSeriesFragment.class);

	private List<DataPoint> dataPoints = new ArrayList<DataPoint>(60);

	public TimeSeriesFragment() {
		// Default constructor
	}

	void addPoint(DataPoint dataPoint) {
		dataPoints.add(dataPoint);
	}

	void addSegment(byte[] data) throws TException {
		logger.info("deserializing segment");

		TDeserializer deserializer = new TDeserializer();
		CompactTimeseries ts = new CompactTimeseries();
		deserializer.deserialize(ts, data);

		for (CompactPoint point : ts.getPoints()) {
			DataPoint dp = new DataPoint();
			dp.setTimestamp(point.getTimestamp());
			dp.setValue(point.getValue());

			dataPoints.add(dp);
		}
	}

	@Override
	public Iterator<DataPoint> iterator() {
		return dataPoints.iterator(); 
	}
}
