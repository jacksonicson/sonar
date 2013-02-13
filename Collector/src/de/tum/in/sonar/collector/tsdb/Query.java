package de.tum.in.sonar.collector.tsdb;

import java.util.HashSet;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Query {

	@SuppressWarnings("unused")
	private static Logger logger = LoggerFactory.getLogger(Query.class);

	// Required fields
	private final long startTime;
	private final long stopTime;
	private final String sensor;

	// Optional fields
	private String hostname;
	private Set<String> labels = new HashSet<String>();

	public Query(String sensor, long startTime, long stopTime) {
		this.sensor = sensor;
		this.startTime = startTime;
		this.stopTime = stopTime;
	}

	public Query setHostname(String hostname) {
		this.hostname = hostname;

		return this;
	}

	public Query setLabels(String[] labels) {
		this.labels.clear();
		for (String label : labels)
			this.labels.add(label);

		return this;
	}

	long getStartTime() {
		return startTime;
	}

	long getStopTime() {
		return stopTime;
	}

	String getSensor() {
		return sensor;
	}

	String getHostname() {
		return hostname;
	}

	Set<String> getLabels() {
		return this.labels;
	}
}
