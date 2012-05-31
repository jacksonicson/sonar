package de.tum.in.sonar.collector.tsdb;

import java.util.HashSet;
import java.util.Set;

public class TimeSeriesPoint {

	private long timestamp;
	private long value;
	private Set<String> labels = new HashSet<String>();

	public long getTimestamp() {
		return timestamp;
	}

	public void setTimestamp(long timestamp) {
		this.timestamp = timestamp;
	}

	public long getValue() {
		return value;
	}

	public void setValue(long value) {
		this.value = value;
	}

	public Set<String> getLabels() {
		return labels;
	}

	public void setLabels(Set<String> labels) {
		this.labels = labels;
	}
}
