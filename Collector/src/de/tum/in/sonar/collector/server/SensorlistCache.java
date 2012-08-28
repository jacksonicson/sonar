package de.tum.in.sonar.collector.server;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

public class SensorlistCache {

	final class Entry {
		final Set<String> sensors;
		final long created;

		public Entry(Set<String> sensors, long created) {
			this.sensors = sensors;
			this.created = created;
		}
	}

	private Map<String, Entry> sensorCache = new HashMap<String, Entry>();

	void put(String hostname, Set<String> sensors) {
		Entry entry = new Entry(sensors, System.currentTimeMillis());
		sensorCache.put(hostname, entry);
	}

	Set<String> get(String hostname) {
		if (sensorCache.containsKey(hostname)) {
			Entry entry = sensorCache.get(hostname);
			long delta = System.currentTimeMillis() - entry.created;
			if (delta > 60000)
				return null;

			return entry.sensors;
		}

		return null;
	}

	void invalidate(String hostname) {
		sensorCache.remove(hostname);
	}

	void invalidateAll() {
		sensorCache.clear();
	}

}
