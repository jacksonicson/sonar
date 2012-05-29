package de.tum.in.sonar.collector.tsdb;

import java.util.List;

public class Datapoint {

	private final int METRIC_ID_WIDTH = 3;
	private final int TAG_ID_WIDTH = 3;
	private final int TIMESTAMP_WIDTH = 5;

	private int appendToKey(byte[] key, int index, int value, int length) {
		// TODO
		return length;
	}

	private int appendToKey(byte[] key, int index, byte[] value) {
		System.arraycopy(value, 0, key, index, value.length);
		return value.length;
	}

	private byte[] zeors(int length) {
		return new byte[length];
	}

	byte[] writeTimestamp(byte[] key, long timestamp) {

		// Split timestamp to hours
		byte[] hourTimestamp = new byte[TIMESTAMP_WIDTH];

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
		index += appendToKey(key, index, zeors(TIMESTAMP_WIDTH));

		for (String tag : tags) {
			index += appendToKey(key, index, lookupTagId(tag), TAG_ID_WIDTH);
		}

		return key;
	}

}
