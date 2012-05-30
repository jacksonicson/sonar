package de.tum.in.sonar.collector.server;

import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.ManagementService;
import de.tum.in.sonar.collector.TimeSeriesQuery;
import de.tum.in.sonar.collector.tsdb.Query;
import de.tum.in.sonar.collector.tsdb.QueryException;
import de.tum.in.sonar.collector.tsdb.TimeSeriesDatabase;
import de.tum.in.sonar.collector.tsdb.UnresolvableException;

public class ManagementServiceImpl implements ManagementService.Iface {

	private static final Logger logger = LoggerFactory.getLogger(ManagementServiceImpl.class);

	private TimeSeriesDatabase tsdb;

	@Override
	public void query(TimeSeriesQuery query) throws TException {

		Query tsdbQuery = new Query(query.getSensor(), query.getStartTime(), query.getStopTime());
		try {
			tsdb.run(tsdbQuery);
		} catch (QueryException e) {
			logger.error("Error while executing query", e);
		} catch (UnresolvableException e) {
			logger.error("Error while mapping in query", e);
		}
	}

	public void setTsdb(TimeSeriesDatabase tsdb) {
		this.tsdb = tsdb;
	}
}
