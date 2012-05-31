package de.tum.in.sonar.collector.server;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import redis.clients.jedis.BinaryJedis;
import redis.clients.jedis.JedisPool;
import redis.clients.util.SafeEncoder;
import de.tum.in.sonar.collector.ManagementService;
import de.tum.in.sonar.collector.TimeSeriesQuery;
import de.tum.in.sonar.collector.TransferableTimeSeriesPoint;
import de.tum.in.sonar.collector.tsdb.Query;
import de.tum.in.sonar.collector.tsdb.QueryException;
import de.tum.in.sonar.collector.tsdb.TimeSeries;
import de.tum.in.sonar.collector.tsdb.TimeSeriesDatabase;
import de.tum.in.sonar.collector.tsdb.TimeSeriesPoint;
import de.tum.in.sonar.collector.tsdb.UnresolvableException;

public class ManagementServiceImpl implements ManagementService.Iface {

	private static final Logger logger = LoggerFactory.getLogger(ManagementServiceImpl.class);

	private TimeSeriesDatabase tsdb;

	private JedisPool jedisPool = new JedisPool("srv2");

	@Override
	public List<TransferableTimeSeriesPoint> query(TimeSeriesQuery query) throws TException {

		Query tsdbQuery = new Query(query.getSensor(), query.getStartTime(), query.getStopTime());
		try {
			TimeSeries timeSeries = tsdb.run(tsdbQuery);
			List<TransferableTimeSeriesPoint> tsPoints = new ArrayList<TransferableTimeSeriesPoint>(100);

			for (TimeSeriesPoint point : timeSeries) {
				TransferableTimeSeriesPoint tsPoint = new TransferableTimeSeriesPoint();
				tsPoints.add(tsPoint);

				tsPoint.setTimestamp(point.getTimestamp());
				tsPoint.setValue(point.getValue());
				tsPoint.setLabels(point.getLabels());
			}

			return tsPoints;

		} catch (QueryException e) {
			logger.error("Error while executing query", e);
		} catch (UnresolvableException e) {
			logger.error("Error while mapping in query", e);
		}

		return null;
	}

	@Override
	public ByteBuffer fetchSensor(String name) throws TException {
		logger.debug("fetching sensor " + name);
		name = "sensor:" + name;
		BinaryJedis jedis = new BinaryJedis("srv2");
		byte[] data = jedis.get(SafeEncoder.encode(name));
		return ByteBuffer.wrap(data);
	}

	@Override
	public void deploySensor(String name, ByteBuffer file) throws TException {
		logger.debug("deploying sensor " + name);
		name = "sensor:" + name;
		BinaryJedis jedis = new BinaryJedis("srv2");
		jedis.set(SafeEncoder.encode(name), file.array());
	}

	@Override
	public void addHost(String hostname) throws TException {
		// TODO Auto-generated method stub

	}

	@Override
	public void delHost(String hostname) throws TException {
		// TODO Auto-generated method stub

	}

	@Override
	public void setHostLabels(Set<String> labels) throws TException {
		// TODO Auto-generated method stub

	}

	@Override
	public String setSensor(String hostname, String sensor, boolean activate) throws TException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public String getSensorKey(String hostname, String sensor) throws TException {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void setSensorLabels(String sensorKey, Set<String> labels) throws TException {
		// TODO Auto-generated method stub

	}

	@Override
	public void setSensorConfiguration(String sensorKey, ByteBuffer configuration) throws TException {
		// TODO Auto-generated method stub

	}

	public void setTsdb(TimeSeriesDatabase tsdb) {
		this.tsdb = tsdb;
	}

}
