package de.tum.in.sonar.collector.notification;

import java.util.HashSet;
import java.util.Set;

import de.tum.in.sonar.collector.SensorToWatch;

public final class Subscription {

	private final String ip;
	private final int port;
	private final Set<SensorToWatch> watchlist;

	private Set<String> hosts = new HashSet<String>();
	private Set<String> hostsensor = new HashSet<String>();

	public Subscription(String ip, int port, Set<SensorToWatch> watchlist) {
		this.ip = ip;
		this.port = port;
		this.watchlist = watchlist;
		updateSets(watchlist);
	}

	private void updateSets(Set<SensorToWatch> watchlist) {
		for (SensorToWatch watch : watchlist) {
			if (!hosts.contains(watch.hostname))
				hosts.add(watch.hostname);
			String sensor = watch.hostname + "." + watch.sensor;
			if (!hostsensor.contains(sensor))
				hostsensor.add(sensor);
		}
	}

	String getIp() {
		return ip;
	}

	int getPort() {
		return port;
	}

	Set<SensorToWatch> getWatchlist() {
		return watchlist;
	}

	public void extendWatchlist(Set<SensorToWatch> watchlist) {
		this.watchlist.addAll(watchlist);
		updateSets(watchlist);
	}

	boolean check(Notification notification) {
		if (!hosts.contains(notification.getHostname()))
			return false;

		if (!hostsensor.contains(notification.getHostname() + "." + notification.getSensor()))
			return false;

		return true;
	}

	@Override
	public boolean equals(Object obj) {
		if (!(obj instanceof Subscription))
			return false;

		Subscription test = (Subscription) obj;
		boolean equals = true;
		equals &= test.getIp().equals(this.ip);
		equals &= test.getPort() == this.port;

		return equals;
	}

	public String dump() {
		String sensors = "";
		for (SensorToWatch sensor : this.watchlist) {
			sensors += sensor.sensor + ";";
		}
		return "ip: " + this.ip + " sensors " + sensors;
	}
}
