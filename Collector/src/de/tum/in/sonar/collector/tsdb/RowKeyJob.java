package de.tum.in.sonar.collector.tsdb;

import java.util.Arrays;
import java.util.concurrent.Delayed;
import java.util.concurrent.TimeUnit;

final class RowKeyJob implements Delayed {

	// end of delay is always 30 minutes by default
	private final long delay;
	private final byte[] rowKey;
	private final long insertTime = System.currentTimeMillis();

	RowKeyJob(long delay, byte[] rowKey) {
		super();
		this.delay = delay * 1000;
		this.rowKey = rowKey;
	}

	long getDelay() {
		long remaining = delay - (System.currentTimeMillis() - insertTime);
		return remaining; 
	}

	byte[] getRowKey() {
		return rowKey;
	}

	@Override
	public int compareTo(Delayed o) {
		RowKeyJob rowKey = (RowKeyJob) o;
		return (int) (this.getDelay() - rowKey.getDelay());
	}

	@Override
	public long getDelay(TimeUnit unit) {
		long remaining = delay - (System.currentTimeMillis() - insertTime);
		return unit.convert(remaining, TimeUnit.MILLISECONDS);
	}

	@Override
	public int hashCode() {
		return Arrays.hashCode(rowKey);
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		
		if (obj == null)
			return false;
		
		if (getClass() != obj.getClass())
			return false;

		RowKeyJob job = (RowKeyJob) obj;
		return Arrays.equals(rowKey, job.rowKey);
	}

}
