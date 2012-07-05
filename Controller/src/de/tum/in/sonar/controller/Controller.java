package de.tum.in.sonar.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Controller {

	private static Logger logger = LoggerFactory.getLogger(Controller.class);

	public Controller() {

		logger.info("Starting Controller..."); 
	}

	public static void main(String arg[]) {
		new Controller();
	}

}
