package de.tum.in.sonar.collector.server;

import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.CollectService;
import de.tum.in.sonar.collector.File;
import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.TimeSeriesPoint;
import de.tum.in.sonar.collector.tsdb.DataPoint_mv;
import de.tum.in.sonar.collector.tsdb.TimeSeriesDatabase;

public class CollectServiceImpl implements CollectService.Iface {

	private static final Logger logger = LoggerFactory.getLogger(CollectServiceImpl.class);

	private TimeSeriesDatabase tsdb;

	@Override
	public void logMessage(Identifier id, String message) throws TException {
		logger.warn("log message - not implemented");
	}

	@Override
	public void logMetric(Identifier id, TimeSeriesPoint value) throws TException {
		logger.debug("log metric");

		DataPoint_mv dp = new DataPoint_mv();
		dp.setTimestamp(id.getTimestamp());
		dp.setSensor(id.getSensor());
		dp.setHostname(id.getHostname());
		dp.setValue(value.getValue());
		dp.setLabels(value.getLabels());
		
		tsdb.writeData(dp); 
	}

	@Override
	public void logResults(Identifier id, File file) throws TException {
		logger.warn("log results - not implemented");
	}

	public void setTsdb(TimeSeriesDatabase tsdb) {
		this.tsdb = tsdb;
	}
}
