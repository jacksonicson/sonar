package de.tum.in.sonar.collector.tsdb;

import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.MetricReading;

public class MetricPoint {

	@SuppressWarnings("unused")
	private static final Logger logger = LoggerFactory.getLogger(MetricPoint.class);

	private final Identifier id;
	private final MetricReading value;

	public MetricPoint(Identifier id, MetricReading value) {
		this.id = id;
		this.value = value;
	}

	final long getValue() {
		return value.getValue();
	}

	final String getSensor() {
		return id.getSensor();
	}

	final String getHostname() {
		return id.getHostname();
	}

	final Set<String> getLabels() {
		return value.getLabels();
	}
	
	final long getTimestamp() {
		return id.getTimestamp(); 
	}
}
