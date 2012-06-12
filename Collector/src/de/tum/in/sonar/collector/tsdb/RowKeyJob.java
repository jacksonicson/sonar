package de.tum.in.sonar.collector.tsdb;

import java.util.Arrays;
import java.util.concurrent.Delayed;
import java.util.concurrent.TimeUnit;

final class RowKeyJob implements Delayed {

	// end of delay is always 30 minutes by default
	private final long delaz;
	private final byte[] rowKey;
	private final long offset = System.currentTimeMillis();

	RowKeyJob(long delay, byte[] rowKey) {
		super();
		this.delaz = delay;
		this.rowKey = rowKey;
	}

	long getDelaz() {
		return delaz;
	}

	byte[] getRowKey() {
		return rowKey;
	}

	@Override
	public int compareTo(Delayed o) {
		RowKeyJob rowKey = (RowKeyJob) o;
		return (int) (this.delaz - rowKey.getDelaz());
	}

	@Override
	public long getDelay(TimeUnit unit) {
		long remaining = delaz - (System.currentTimeMillis() - offset);
		return unit.convert(remaining, TimeUnit.MILLISECONDS);
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

		RowKeyJob job = (RowKeyJob) obj;
		return Arrays.equals(rowKey, job.rowKey);
	}

}
