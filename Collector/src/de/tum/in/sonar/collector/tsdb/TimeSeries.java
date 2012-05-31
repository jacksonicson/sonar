package de.tum.in.sonar.collector.tsdb;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.apache.commons.lang.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TimeSeries implements Iterable<DataPoint> {

	private static final Logger logger = LoggerFactory.getLogger(TimeSeries.class);

	private List<TimeSeriesFragment> fragments = new ArrayList<TimeSeriesFragment>();

	private TimeSeriesIterator iterator = new TimeSeriesIterator();

	@Override
	public Iterator<DataPoint> iterator() {
		return iterator;
	}

	TimeSeriesFragment newFragment() {
		logger.info("new fragment");
		TimeSeriesFragment fragment = new TimeSeriesFragment();
		fragments.add(fragment);
		return fragment;
	}

	class TimeSeriesIterator implements Iterator<DataPoint> {

		int fragment = 0;
		Iterator<DataPoint> listIterator = null;

		@Override
		public boolean hasNext() {
			if (fragment > fragments.size())
				return false;

			if (listIterator != null) {
				if (!listIterator.hasNext())
					return fragment < fragments.size();
			}

			return true;
		}

		@Override
		public DataPoint next() {
			if (listIterator == null) {
				listIterator = fragments.get(fragment).iterator();
				fragment++;
			}

			if (!listIterator.hasNext()) {
				listIterator = fragments.get(fragment).iterator();
				fragment++;
			}

			return listIterator.next();
		}

		@Override
		public void remove() {
			throw new NotImplementedException();
		}

	}
}
