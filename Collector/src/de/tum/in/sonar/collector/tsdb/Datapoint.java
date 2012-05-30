package de.tum.in.sonar.collector.tsdb;

import java.util.Set;

import org.apache.hadoop.hbase.util.Bytes;

public class DataPoint {

	private final int SENSOR_ID_WIDTH = 4;
	private final int LABEL_ID_WIDTH = 4;
	private final int TIMESTAMP_WIDTH = 8;
	private final int HOSTNAME_WIDTH = 4;

	private long timestamp;
	private int sensor;
	private String hostname;
	private Set<String> labels;
	private long value;

	private int appendToKey(byte[] key, int index, int value, int length) {
		byte[] bvalue = Bytes.toBytes(value);
		// TODO: Check for padding
		return appendToKey(key, index, bvalue);
	}

	private int appendToKey(byte[] key, int index, byte[] value) {
		System.arraycopy(value, 0, key, index, value.length);
		return value.length;
	}

	private int writeTimestamp(byte[] key) {
		long hourSinceEpoch = timestamp - (timestamp % 3600);
		byte[] hourTimestamp = Bytes.toBytes(hourSinceEpoch);

		System.arraycopy(hourTimestamp, 0, key, SENSOR_ID_WIDTH, TIMESTAMP_WIDTH);

		return TIMESTAMP_WIDTH;
	}

	private int lookupTagId(String tag) {
		return 111;
	}

	byte[] buildKey() {
		int keyWidth = SENSOR_ID_WIDTH + TIMESTAMP_WIDTH + HOSTNAME_WIDTH + LABEL_ID_WIDTH * labels.size();
		byte[] key = new byte[keyWidth];

		// Key structure:
		// sensor id, timestamp, hostname-id, n * label-id

		int index = 0;
		index += appendToKey(key, index, sensor, SENSOR_ID_WIDTH);
		index += writeTimestamp(key);
		index += HOSTNAME_WIDTH;

		for (String label : labels) {
			index += appendToKey(key, index, lookupTagId(label), LABEL_ID_WIDTH);
		}

		return key;
	}

	public void setTimestamp(long timestamp) {
		this.timestamp = timestamp;
	}

	public void setSensor(int sensor) {
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
