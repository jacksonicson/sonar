package de.tum.in.sonar.collector.log;

interface LogConstants {
	public static final String TABLE_LOG = "sonar_logs";
	public static final String FAMILY_LOG_DATA = "data";
	public static final String QUALIFIER_LOG_DATA = "data";
	
	/*public static final String QUALIFIER_LOG_MESSAGE = "logMessage";
	public static final String QUALIFIER_LOG_LEVEL = "logLevel";
	public static final String QUALIFIER_PROG_NAME = "programName";*/

	public static final int SENSOR_ID_WIDTH = 8;
	public static final int TIMESTAMP_WIDTH = 8;
	public static final int HOSTNAME_WIDTH = 8;
}
