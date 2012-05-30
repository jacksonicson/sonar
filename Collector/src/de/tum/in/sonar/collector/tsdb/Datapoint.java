package de.tum.in.sonar.collector.tsdb;

import java.util.Set;

import org.apache.hadoop.hbase.util.Bytes;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.HBaseUtil;

public class DataPoint {

	private static final Logger logger = LoggerFactory.getLogger(DataPoint.class);

	private final int SENSOR_ID_WIDTH = 8;
	private final int LABEL_ID_WIDTH = 8;
	private final int TIMESTAMP_WIDTH = 8;
	private final int HOSTNAME_WIDTH = 8;

	private IdResolver labelResolver;
	private IdResolver hostnameResolver;
	private IdResolver sensorResolver;

	private long timestamp;
	private String sensor;
	private String hostname;
	private Set<String> labels;

	private long value;

	long getValue() {
		return value;
	}

	public DataPoint() {
		labelResolver = new IdResolver("label");
		hostnameResolver = new IdResolver("hostname");
		sensorResolver = new IdResolver("sensor");
	}

	private int appendToKey(byte[] key, int index, long value, int length) {
		byte[] bvalue = Bytes.toBytes(value);
		return appendToKey(key, index, bvalue);
	}

	private int appendToKey(byte[] key, int index, byte[] value) {
		System.arraycopy(value, 0, key, index, value.length);
		return value.length;
	}

	long getOffset() {
		long hourSinceEpoch = timestamp - (timestamp % 3600);
		long offset = (timestamp - hourSinceEpoch);
		return offset;
	}

	private int writeTimestamp(byte[] key) {

		logger.info("timestamp: " + timestamp);
		logger.info("Secs: " + (timestamp % 3600));
		long hourSinceEpoch = timestamp - (timestamp % 3600);
		logger.info("hour: " + hourSinceEpoch);

		byte[] hourTimestamp = Bytes.toBytes(hourSinceEpoch);

		System.arraycopy(hourTimestamp, 0, key, SENSOR_ID_WIDTH, TIMESTAMP_WIDTH);

		return TIMESTAMP_WIDTH;
	}

	byte[] buildKey(HBaseUtil util) throws UnresolvableException {

		sensorResolver.setHbaseUtil(util);
		hostnameResolver.setHbaseUtil(util);
		labelResolver.setHbaseUtil(util);

		int keyWidth = SENSOR_ID_WIDTH + TIMESTAMP_WIDTH + HOSTNAME_WIDTH + LABEL_ID_WIDTH * labels.size();
		byte[] key = new byte[keyWidth];

		// Key structure:
		// sensor id, timestamp, hostname-id, n * label-id

		int index = 0;
		index += appendToKey(key, index, sensorResolver.resolveName(sensor), SENSOR_ID_WIDTH);
		index += writeTimestamp(key);
		index += appendToKey(key, index, hostnameResolver.resolveName(hostname), HOSTNAME_WIDTH);

		for (String label : labels) {
			index += appendToKey(key, index, labelResolver.resolveName(label), LABEL_ID_WIDTH);
		}

		return key;
	}

	public void setTimestamp(long timestamp) {
		this.timestamp = timestamp;
	}

	public void setSensor(String sensor) {
		this.sensor = sensor;
	}

	public void setHostname(String hostname) {
		this.hostname = hostname;
	}

	public void setValue(long value) {
		this.value = value;
	}

	public void setLabels(Set<String> labels) {
		this.labels = labels;
	}

}
