package de.tum.in.sonar.collector.notification;

import java.util.Set;

import de.tum.in.sonar.collector.SensorToWatch;

public final class Subscription {

	private final String ip;
	private final int port;
	private final Set<SensorToWatch> watchlist;

	public Subscription(String ip, int port, Set<SensorToWatch> watchlist) {
		this.ip = ip;
		this.port = port;
		this.watchlist = watchlist;
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

	boolean check(Notification notification) {
		return true;
	}

	@Override
	public boolean equals(Object obj) {
		if(!(obj instanceof Subscription))
			return false;
		
		Subscription test = (Subscription)obj; 
		boolean equals = true; 
		equals &= test.getIp().equals(this.ip);
		equals &= test.getPort() == this.port;
				
		return equals; 
	}
}
