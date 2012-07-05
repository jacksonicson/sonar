package de.tum.in.sonar.controller;

import java.util.Set;

import org.apache.thrift.TException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.NotificationClient;
import de.tum.in.sonar.collector.NotificationData;

public class Receiver implements NotificationClient.Iface {

	private static Logger logger = LoggerFactory.getLogger(Controller.class);

	@Override
	public void receive(Set<NotificationData> data) throws TException {
		
		for(NotificationData d : data){
			logger.info("Received notification! " + d.reading.getValue() + " - " + d.getId().getTimestamp());
		}
		
		
	}

}
