package de.tum.in.sonar.collector.tsdb;

public class InternalTableDescriptor implements Comparable<InternalTableDescriptor> {
	private final String name;

	private final String[] families;

	public InternalTableDescriptor(String name, String[] families) {
		this.name = name;
		this.families = families;
	}

	String getName() {
		return name;
	}

	String[] getFamilies() {
		return families;
	}

	@Override
	public int compareTo(InternalTableDescriptor o) {
		return name.compareTo(o.getName());
	}

	@Override
	public int hashCode() {
		return name.hashCode();
	}

	@Override
	public boolean equals(Object obj) {
		InternalTableDescriptor desc = (InternalTableDescriptor) obj;
		return name.equals(desc.getName());
	}
}
