package de.tum.in.sonar.collector.tsdb;

import java.util.List;
import java.util.Set;

import org.apache.hadoop.hbase.util.Bytes;

public class DataPoint {

	private final int METRIC_ID_WIDTH = 3;
	private final int TAG_ID_WIDTH = 3;
	private final int TIMESTAMP_WIDTH = 5;

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

	byte[] writeTimestamp(byte[] key, long timestamp) {
		long hourSinceEpoch = timestamp - (timestamp % 3600);
		byte[] hourTimestamp = Bytes.toBytes(hourSinceEpoch);

		System.arraycopy(hourTimestamp, 0, key, METRIC_ID_WIDTH, TIMESTAMP_WIDTH);

		return key;
	}

	private int lookupMetricId(String metric) {
		return 0;
	}

	private int lookupTagId(String tag) {
		return 0;
	}

	byte[] buildKey(String metric, List<String> tags) {
		int keyWidth = METRIC_ID_WIDTH + TIMESTAMP_WIDTH + TAG_ID_WIDTH * tags.size();
		byte[] key = new byte[keyWidth];

		int index = 0;
		index += appendToKey(key, index, lookupMetricId(metric), METRIC_ID_WIDTH);
		index += TIMESTAMP_WIDTH;

		for (String tag : tags) {
			index += appendToKey(key, index, lookupTagId(tag), TAG_ID_WIDTH);
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
