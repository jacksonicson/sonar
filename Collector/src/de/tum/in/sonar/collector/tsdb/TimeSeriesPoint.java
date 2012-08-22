package de.tum.in.sonar.collector.tsdb;

public final class TimeSeriesPoint {

	private final long timestamp;
	private double value;
	private final String[] labels;

	public TimeSeriesPoint(long timestamp, double value, String[] labels) {
		this.timestamp = timestamp;
		this.value = value;
		this.labels = labels;
	}

	public TimeSeriesPoint(long timestamp, double value) {
		this(timestamp, value, null);
	}

	public long getTimestamp() {
		return timestamp;
	}

	public double getValue() {
		return value;
	}

	public void setValue(double value) {
		this.value = value;
	}

	public String[] getLabels() {
		return labels;
	}
}
