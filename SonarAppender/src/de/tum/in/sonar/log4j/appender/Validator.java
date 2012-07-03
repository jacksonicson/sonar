package de.tum.in.sonar.log4j.appender;

/**
 * A simple utility for validating method parameters. This is a cheap take on
 * Apache's commons-lang version of Validate.
 * 
 * @author Josh Devins
 */
public final class Validator {

	private Validator() {
		throw new UnsupportedOperationException();
	}

	public static void notEmptyString(final String validate, final String message) {
		if (validate == null || validate.isEmpty()) {
			throwIllegalArgumentExceptionWithMessage(message);
		}
	}

	public static void positiveInteger(final int validate, final String message) {
		if (validate < 0) {
			throwIllegalArgumentExceptionWithMessage(message);
		}
	}

	private static void throwIllegalArgumentExceptionWithMessage(final String message) {
		if (message == null) {
			throw new IllegalArgumentException();
		}
		throw new IllegalArgumentException(message);
	}
}