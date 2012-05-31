package de.tum.in.sonar.collector.tsdb;

import java.util.HashSet;
import java.util.Set;

public class TimeSeriesPoint {

	private long timestamp;
	private long value;
	private Set<String> labels = new HashSet<String>();

	long getTimestamp() {
		return timestamp;
	}

	void setTimestamp(long timestamp) {
		this.timestamp = timestamp;
	}

	long getValue() {
		return value;
	}

	void setValue(long value) {
		this.value = value;
	}

	Set<String> getLabels() {
		return labels;
	}

	void setLabels(Set<String> labels) {
		this.labels = labels;
	}
}
