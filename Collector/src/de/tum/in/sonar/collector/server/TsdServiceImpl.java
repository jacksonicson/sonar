package de.tum.in.sonar.collector.server;

import org.apache.thrift.TException;

import de.tum.in.sonar.collector.CollectService;
import de.tum.in.sonar.collector.File;
import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.TimeSeriesPoint;

public class TsdServiceImpl implements CollectService.Iface {

	@Override
	public void logMessage(Identifier id, String message) throws TException {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void logMetric(Identifier id, TimeSeriesPoint value)
			throws TException {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void logResults(Identifier id, File file) throws TException {
		// TODO Auto-generated method stub
		
	}

}
