package de.tum.in.sonar.collector.tsdb;

public class InvalidLabelException extends Exception {

	private static final long serialVersionUID = -2393595909253840041L;

	private String label;

	public InvalidLabelException(String label) {
		this.label = label;
	}

	@Override
	public String toString() {
		return "Could not create mapping for invalid label name: " + label;
	}
}
