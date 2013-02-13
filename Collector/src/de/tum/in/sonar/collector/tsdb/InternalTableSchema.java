package de.tum.in.sonar.collector.tsdb;

class InternalTableSchema implements Comparable<InternalTableSchema> {
	private final String name;
	private final String[] families;
	private final int versions;

	public InternalTableSchema(String name, String[] families, int versions) {
		this.name = name;
		this.families = families;
		this.versions = versions;
	}

	public InternalTableSchema(String name, String[] families) {
		this(name, families, 1);
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

	public int getVersions() {
		return this.versions;
	}
}
