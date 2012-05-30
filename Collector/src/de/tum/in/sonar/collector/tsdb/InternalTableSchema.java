package de.tum.in.sonar.collector.tsdb;

class InternalTableSchema implements Comparable<InternalTableSchema> {
	private final String name;

	private final String[] families;

	public InternalTableSchema(String name, String[] families) {
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
	public int compareTo(InternalTableSchema o) {
		return name.compareTo(o.getName());
	}

	@Override
	public int hashCode() {
		return name.hashCode();
	}

	@Override
	public boolean equals(Object obj) {
		InternalTableSchema desc = (InternalTableSchema) obj;
		return name.equals(desc.getName());
	}
}
