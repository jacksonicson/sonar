package de.tum.in.sonar.collector.server;

import org.apache.thrift.TException;

import de.tum.in.sonar.collector.ManagementService;
import de.tum.in.sonar.collector.TimeSeriesQuery;

public class ManagementServiceImpl implements ManagementService.Iface {

	@Override
	public void query(TimeSeriesQuery query) throws TException {

	}

}
