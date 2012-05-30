package de.tum.in.sonar.collector.tsdb;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.apache.hadoop.hbase.KeyValue;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.util.Bytes;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import de.tum.in.sonar.collector.HBaseUtil;

public class IdResolver {

	private static final Logger logger = LoggerFactory.getLogger(IdResolver.class);

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

	long resolveName(String name) throws UnresolvableException {
		if (forwardMapping.containsKey(name)) {
			return forwardMapping.get(name);
		}

		long scan = scanNames(name);
		return scan;
	}

	String resolveId(Integer id) throws UnresolvableException {
		if (reverseMapping.containsKey(id)) {
			return reverseMapping.get(id);
		}

		throw new UnresolvableException();
	}

	private Long createMapping(String name) throws IOException {

		HTable uidTable = new HTable(hbaseUtil.getConfig(), "tsdb-uid");

		long value = uidTable.incrementColumnValue(Bytes.toBytes("counter"), Bytes.toBytes("forward"),
				Bytes.toBytes(type), 1);

		Put put = new Put(Bytes.toBytes(name));
		put.add(Bytes.toBytes("forward"), Bytes.toBytes(type), Bytes.toBytes(value));

		boolean success = uidTable.checkAndPut(Bytes.toBytes(name), Bytes.toBytes("forward"), Bytes.toBytes(type),
				null, put);

		if (success) {
			put = new Put(Bytes.toBytes(value));
			put.add(Bytes.toBytes("backward"), Bytes.toBytes(type), Bytes.toBytes(name));
			uidTable.put(put);

			return value;
		}

		return null;
	}

	private Long createMappingRetry(String name) throws UnresolvableException {

		for (int retry = 0; retry < 3; retry++) {
			try {
				Long mapping = createMapping(name);
				if (mapping != null)
					return mapping;
			} catch (IOException e) {
				logger.debug("could not insert mapping", e);
			}
		}

		throw new UnresolvableException();
	}

	long scanNames(String name) throws UnresolvableException {
		try {
			HTable uidTable = new HTable(hbaseUtil.getConfig(), "tsdb-uid");

			logger.info("checking for name: " + name + " of type " + type);

			Get get = new Get(Bytes.toBytes(name));
			Result result = uidTable.get(get);

			if (!uidTable.exists(get)) {
				logger.info("creating new mapping");
				long value = createMappingRetry(name);
				logger.info("value: " + value);

				return value;
			}

			KeyValue kvalue = result.getColumnLatest(Bytes.toBytes("forward"), Bytes.toBytes(type));
			if (kvalue == null) {
				long value = createMappingRetry(name);
				return value;
			}

			byte[] value = kvalue.getValue();
			return Bytes.toLong(value);

		} catch (IOException e) {
			e.printStackTrace();
		}

		return -1;
	}

	void scanId(Integer id) {

	}

	public void setHbaseUtil(HBaseUtil hbaseUtil) {
		this.hbaseUtil = hbaseUtil;
	}
}
