package de.tum.in.sonar.collector.tsdb;

import java.util.HashMap;
import java.util.Map;

import de.tum.in.sonar.collector.HBaseUtil;

public class IdResolver {

	// Type
	private final String type;

	// Caches
	private Map<String, Integer> forwardMapping = new HashMap<String, Integer>();
	private Map<Integer, String> reverseMapping = new HashMap<Integer, String>();

	// HBase connection
	private HBaseUtil hbaseUtil;

	public IdResolver(String type) {
		this.type = type;
	}

	Integer resolveName(String name) throws UnresolvableException {
		if (forwardMapping.containsKey(name)) {
			return forwardMapping.get(name);
		}

		throw new UnresolvableException();
	}

	String resolveId(Integer id) throws UnresolvableException {
		if (reverseMapping.containsKey(id)) {
			return reverseMapping.get(id);
		}

		throw new UnresolvableException();
	}

	void scanNames(String name) {

	}

	void scanId(Integer id) {

	}

	public void setHbaseUtil(HBaseUtil hbaseUtil) {
		this.hbaseUtil = hbaseUtil;
	}
}
