package de.tum.in.sonar.collector.tsdb;

interface Const {

	public static final int SENSOR_ID_WIDTH = 8;
	public static final int LABEL_ID_WIDTH = 8;
	public static final int TIMESTAMP_WIDTH = 8;
	public static final int HOSTNAME_WIDTH = 8;

	public static final String TABLE_TSDB = "tsdb";
	public static final String FAMILY_TSDB_DATA = "data";

	public static final String TABLE_UID = "tsdb_uid";
	public static final String FAMILY_UID_FORWARD = "forward";
	public static final String FAMILY_UID_BACKWARD = "backward";
}
