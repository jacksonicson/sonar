package de.tum.in.sonar.collector.tsdb;

import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DataPoint {

	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(DataPoint.class);

	private long timestamp;
	private String sensor;
	private String hostname;
	private Set<String> labels;

	private long value;

	public long getValue() {
		return value;
	}

	public long getHourSinceEpoch() {
		long hourSinceEpoch = timestamp - (timestamp % 3600);
		return hourSinceEpoch;
	}

	public long getSecondsInHour() {
		long hourSinceEpoch = getHourSinceEpoch();
		long offset = (timestamp - hourSinceEpoch);
		return offset;
	}

	public String getSensor() {
		return sensor;
	}

	public String getHostname() {
		return hostname;
	}

	public Set<String> getLabels() {
		return labels;
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
