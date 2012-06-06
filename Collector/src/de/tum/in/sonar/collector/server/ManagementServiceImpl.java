package de.tum.in.sonar.collector.server;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import redis.clients.jedis.BinaryJedis;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.util.SafeEncoder;
import de.tum.in.sonar.collector.BundledSensorConfiguration;
import de.tum.in.sonar.collector.ManagementService;
import de.tum.in.sonar.collector.SensorConfiguration;
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
	public void delSensor(String sensor) throws TException {
		// Remove the sensor binary
		Jedis jedis = jedisPool.getResource();

		// Remove sensor from the sensors list
		long llen = jedis.llen("sensors");
		jedis.lrem("sensors", llen, sensor);

		// Remove the binary
		jedis.del("sensor:" + sensor);

		// Remove configuration
		jedis.del("sensor:" + sensor + ":config");

		// Remove labels
		jedis.del("sensor:" + sensor + ":labels");

		// Remove sensor from hosts
		String key = "hostnames";
		long hostCount = jedis.llen(key);
		List<String> hosts = jedis.lrange(key, 0, hostCount);
		for (String hostname : hosts) {
			String id = jedis.get("hosts:" + hostname);
			jedis.del(hostname + ":" + id + ":sensor:" + sensor);
		}

		jedisPool.returnResource(jedis);
	}

	@Override
	public void deploySensor(String name, ByteBuffer file) throws TException {
		logger.debug("deploying sensor " + name);

		// Add sensor the the sensor list
		Jedis jedisString = jedisPool.getResource();
		jedisString.lpush("sensors", name);
		jedisPool.returnResource(jedisString);

		// Set sensor binary file
		name = "sensor:" + name;
		BinaryJedis jedis = new BinaryJedis("srv2");
		jedis.set(SafeEncoder.encode(name), file.array());
	}

	@Override
	public void setSensorLabels(String sensor, Set<String> labels) throws TException {
		Jedis jedis = jedisPool.getResource();

		String val = jedis.get("sensor:" + sensor);
		if (val != null) {
			String key = "sensor:" + sensor + ":";

			String[] arrLabels = new String[labels.size()];
			labels.toArray(arrLabels);

			jedis.sadd(key + "labels", arrLabels);
		}

		jedisPool.returnResource(jedis);
	}

	@Override
	public void addHost(String hostname) throws TException {
		Jedis jedis = jedisPool.getResource();

		long res = jedis.setnx("host:" + hostname, hostname);
		long id = 0;
		logger.debug("result");
		if (res == 1) {
			logger.debug("creating new host");

			id = jedis.incr("hosts");

			String key = "hostnames";
			jedis.lpush(key, hostname);

			key = "host:" + hostname;
			jedis.set(key, "" + id);

			key = "host:" + id + ":hostname";
			jedis.set(key, hostname);
		}

		jedisPool.returnResource(jedis);
	}

	@Override
	public void delHost(String hostname) throws TException {
		Jedis jedis = jedisPool.getResource();

		String val = jedis.get("host:" + hostname);
		if (val != null) {
			logger.debug("val " + val);
			long id = Integer.parseInt(val);

			String key = "host:" + id + ":hostname";
			jedis.del(key, hostname);

			jedis.del("host:" + hostname, hostname);

			logger.debug("host deleted");
		}

		jedisPool.returnResource(jedis);
	}

	@Override
	public void setHostLabels(String hostname, Set<String> labels) throws TException {
		Jedis jedis = jedisPool.getResource();

		String val = jedis.get("host:" + hostname);
		if (val != null) {
			logger.debug("val " + val);
			long id = Integer.parseInt(val);

			String key = "host:" + id + ":";
			String[] arrLabels = new String[labels.size()];
			labels.toArray(arrLabels);

			jedis.sadd(key + "labels", arrLabels);
		}

		jedisPool.returnResource(jedis);
	}

	@Override
	public Set<String> getLabels(String hostname) throws TException {

		logger.debug("reading labels for hostname: " + hostname);

		Jedis jedis = jedisPool.getResource();

		Set<String> labels = new HashSet<String>();
		String val = jedis.get("host:" + hostname);
		if (val != null) {
			logger.debug("val " + val);
			long id = Integer.parseInt(val);

			String key = "host:" + id + ":";
			labels = jedis.smembers(key + "labels");
		}

		jedisPool.returnResource(jedis);

		return labels;
	}

	@Override
	public void setSensor(String hostname, String sensor, boolean activate) throws TException {
		Jedis jedis = jedisPool.getResource();

		String val = jedis.get("host:" + hostname);
		if (val != null) {
			logger.debug("val " + val);
			long id = Integer.parseInt(val);
			String key = "host:" + id + ":";

			String flag = "on";
			if (!activate)
				flag = "off";

			jedis.set(key + "sensor:" + sensor, flag);
		}

		jedisPool.returnResource(jedis);
	}

	@Override
	public Set<String> getAllSensors() throws TException {
		Jedis jedisString = jedisPool.getResource();
		long length = jedisString.llen("sensors");

		List<String> sensorNames = jedisString.lrange("sensors", 0, length);

		Set<String> result = new HashSet<String>();
		result.addAll(sensorNames);

		jedisPool.returnResource(jedisString);

		return result;
	}

	@Override
	public boolean hasBinary(String sensor) throws TException {
		Jedis jedisString = jedisPool.getResource();
		byte[] data = jedisString.get(SafeEncoder.encode("sensors:" + sensor));
		return data.length > 64;
	}

	@Override
	public Set<String> getSensors(String hostname) throws TException {
		Jedis jedis = jedisPool.getResource();

		String val = jedis.get("host:" + hostname);
		Set<String> result = new HashSet<String>();
		if (val != null) {
			logger.debug("val " + val);
			long id = Integer.parseInt(val);
			String key = "host:" + id + ":";

			// Get all sensors
			Long len = jedis.llen("sensors");
			List<String> sensors = jedis.lrange("sensors", 0, len);
			for (String sensor : sensors) {
				logger.debug("checking sensor: " + sensor);
				String flag = jedis.get(key + "sensor:" + sensor);
				if (flag != null && flag.equals("on")) {
					logger.debug("found active sensor: " + sensor);
					result.add(sensor);
				}
			}
		}

		jedisPool.returnResource(jedis);
		return result;
	}

	@Override
	public Set<String> getSensorLabels(String sensor) throws TException {
		Jedis jedis = jedisPool.getResource();

		Set<String> labels = new HashSet<String>();
		String val = jedis.get("sensor:" + sensor);
		if (val != null) {
			String key = "sensor:" + sensor + ":";
			labels = jedis.smembers(key + "labels");
		}

		jedisPool.returnResource(jedis);

		return labels;
	}

	@Override
	public void setSensorConfiguration(String sensor, SensorConfiguration configuration) throws TException {
		Jedis jedis = jedisPool.getResource();

		String val = jedis.get("sensor:" + sensor);
		if (val != null) {
			String key = "sensor:" + sensor + ":";

			jedis.set(key + "config" + ":" + "interval", Long.toString(configuration.getInterval()));
		}

		jedisPool.returnResource(jedis);
	}

	public BundledSensorConfiguration getBundledSensorConfiguration(String sensor, String hostname) throws TException {
		BundledSensorConfiguration config = new BundledSensorConfiguration();

		config.setSensor(sensor);
		config.setHostname(hostname);

		Jedis jedis = jedisPool.getResource();

		String host = jedis.get("host:" + hostname);
		long hostId = Long.parseLong(host);

		String val = jedis.get("sensor:" + sensor);
		if (val != null) {
			String key = "sensor:" + sensor + ":";

			long interval = Long.parseLong(jedis.get(key + "config" + ":" + "interval"));

			// Active
			String active = jedis.get("host:" + hostId + ":sensor:" + sensor);
			logger.debug("active state: " + active);
			if(active == null)
				active = "off"; 
			
			config.setActive(active.equals("on"));

			// TODO: Host configuration overrides sensor configuration
			SensorConfiguration configuration = new SensorConfiguration();
			configuration.setInterval(interval);
			config.setConfiguration(configuration);

			// TODO: Attach the host labels
			Set<String> labels = jedis.smembers(key + "labels");
			config.setLabels(labels);
		}

		jedisPool.returnResource(jedis);

		return config;
	}

	public void setTsdb(TimeSeriesDatabase tsdb) {
		this.tsdb = tsdb;
	}

	@Override
	public Set<String> getAllHosts() throws TException {
		Jedis jedis = jedisPool.getResource();

		Set<String> hostnames = new HashSet<String>();

		long length = jedis.llen("hostnames");
		List<String> result = jedis.lrange("hostnames", 0, length);
		hostnames.addAll(result);

		jedisPool.returnResource(jedis);

		return hostnames;
	}

}
