package de.tum.in.sonar.collector.notification;

import de.tum.in.sonar.collector.tsdb.MetricPoint;

final class Notification {

	private final String hostname;
	private final String sensor;
	private final MetricPoint reading;

	public Notification(String hostname, String sensor, MetricPoint reading) {
		this.hostname = hostname;
		this.sensor = sensor;
		this.reading = reading;
	}

	String getHostname() {
		return this.hostname;
	}

	String getSensor() {
		return this.sensor;
	}

	MetricPoint getReading() {
		return this.reading;
	}
}
