package de.tum.in.sonar.collector.tsdb;

import java.util.Arrays;
import java.util.concurrent.Delayed;
import java.util.concurrent.TimeUnit;

public class RowKeyJob implements Delayed {

	// end of delay is always 30 minutes by default
	private long endOfDelay = 300000;
	private byte[] rowKey;
	private long queueInsertTime;

	public RowKeyJob() {
	}

	public RowKeyJob(long endOfDelay, byte[] rowKey, long queueInsertTime) {
		super();
		this.endOfDelay = endOfDelay;
		this.rowKey = rowKey;
		this.queueInsertTime = queueInsertTime;
	}

	public long getEndOfDelay() {
		return endOfDelay;
	}

	public void setEndOfDelay(long endOfDelay) {
		this.endOfDelay = endOfDelay;
	}

	public byte[] getRowKey() {
		return rowKey;
	}

	public void setRowKey(byte[] rowKey) {
		this.rowKey = rowKey;
	}

	public long getQueueInsertTime() {
		return queueInsertTime;
	}

	public void setQueueInsertTime(long queueInsertTime) {
		this.queueInsertTime = queueInsertTime;
	}

	@Override
	public int compareTo(Delayed o) {
		int ret = 0;
		RowKeyJob ns = (RowKeyJob) o;
		if (this.endOfDelay < ns.endOfDelay)
			ret = -1;
		else if (this.endOfDelay > ns.endOfDelay)
			ret = 1;
		else if (this.getQueueInsertTime() == ns.getQueueInsertTime())
			ret = 0;
		return ret;
	}

	@Override
	public long getDelay(TimeUnit unit) {
		long tmp = unit.convert(
				(getQueueInsertTime() - System.currentTimeMillis())
						+ endOfDelay, TimeUnit.MILLISECONDS);
		return tmp;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + Arrays.hashCode(rowKey);
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		RowKeyJob other = (RowKeyJob) obj;
		if (!Arrays.equals(rowKey, other.rowKey))
			return false;
		return true;
	}

}
