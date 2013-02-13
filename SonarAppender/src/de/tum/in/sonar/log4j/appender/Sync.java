package de.tum.in.sonar.log4j.appender;

import org.apache.log4j.Level;

@SuppressWarnings("serial")
public class Sync extends Level {

	public static final int SYNC_INT = FATAL_INT + 10;
	public static final Level SYNC = new Sync(SYNC_INT, "SYNC", 7);

	protected Sync(int level, String levelStr, int syslogEquivalent) {
		super(level, levelStr, syslogEquivalent);
	}

	public static Level toLevel(String sArg) {
		if (sArg != null && sArg.toUpperCase().equals("SYNC")) {
			return SYNC;
		}
		return (Level) toLevel(sArg, Level.TRACE);
	}

	public static Level toLevel(int val) {
		if (val == SYNC_INT) {
			return SYNC;
		}
		return (Level) toLevel(val, Level.TRACE);
	}

	public static Level toLevel(int val, Level defaultLevel) {
		if (val == SYNC_INT) {
			return SYNC;
		}
		return Level.toLevel(val, defaultLevel);
	}

	public static Level toLevel(String sArg, Level defaultLevel) {
		if (sArg != null && sArg.toUpperCase().equals("SYNC")) {
			return SYNC;
		}
		return Level.toLevel(sArg, defaultLevel);
	}
}
