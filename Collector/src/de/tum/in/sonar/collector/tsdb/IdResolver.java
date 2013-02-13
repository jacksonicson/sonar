package de.tum.in.sonar.collector.tsdb;

import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

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

	// HBase connection
	private HBaseUtil hbaseUtil;

	public IdResolver(String type) {
		this.type = type;
	}

	private static final Set<String> INVALID_LABELS = new HashSet<String>();

	static {
		INVALID_LABELS.add("counter");
	}

	private boolean isValid(String label) {
		label = label.toUpperCase();
		return INVALID_LABELS.contains(label) == false;
	}

	public long resolveName(String name) throws UnresolvableException, InvalidLabelException {
		if (forwardMapping.containsKey(name)) {
			return forwardMapping.get(name);
		}

		long scan = scanNames(name);
		forwardMapping.put(name, (int) scan);

		return scan;
	}

	private Long createMapping(String name) throws InvalidLabelException, IOException {
		if (!isValid(name))
			throw new InvalidLabelException(name);

		HTable uidTable = new HTable(hbaseUtil.getConfig(), Const.TABLE_UID);

		long value = uidTable.incrementColumnValue(Bytes.toBytes("counter"), Bytes.toBytes("forward"), Bytes.toBytes(type), 1);

		Put put = new Put(Bytes.toBytes(name));
		put.add(Bytes.toBytes("forward"), Bytes.toBytes(type), Bytes.toBytes(value));

		boolean success = uidTable.checkAndPut(Bytes.toBytes(name), Bytes.toBytes("forward"), Bytes.toBytes(type), null, put);

		if (success) {
			put = new Put(Bytes.toBytes(value));
			put.add(Bytes.toBytes("backward"), Bytes.toBytes(type), Bytes.toBytes(name));
			uidTable.put(put);

			uidTable.close();
			return value;
		}

		uidTable.close();
		return null;
	}

	private Long createMappingRetry(String name) throws UnresolvableException, InvalidLabelException {

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

	private long scanNames(String name) throws UnresolvableException, InvalidLabelException {
		logger.debug("checking for name: " + name + " of type " + type);

		HTable uidTable = null;
		try {
			uidTable = new HTable(hbaseUtil.getConfig(), Const.TABLE_UID);

			if (name == null) {
				if (uidTable != null)
					uidTable.close();

				throw new UnresolvableException("no name given");
			}

			Get get = new Get(Bytes.toBytes(name));
			Result result = uidTable.get(get);

			if (!uidTable.exists(get)) {
				logger.info("creating new mapping");
				long value = createMappingRetry(name);
				logger.debug("value: " + value);
				return value;
			}

			KeyValue kvalue = result.getColumnLatest(Bytes.toBytes("forward"), Bytes.toBytes(type));
			if (kvalue == null) {
				logger.debug("creating new mapping");
				long value = createMappingRetry(name);
				logger.debug("value: " + value);
				return value;
			}

			byte[] value = kvalue.getValue();
			long lValue = Bytes.toLong(value);
			logger.debug("resolved to value: " + lValue);

			uidTable.close();
			return lValue;

		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (uidTable != null)
				try {
					uidTable.close();
				} catch (IOException e) {
				}
		}

		return -1;
	}

	public void setHbaseUtil(HBaseUtil hbaseUtil) {
		this.hbaseUtil = hbaseUtil;
	}
}
