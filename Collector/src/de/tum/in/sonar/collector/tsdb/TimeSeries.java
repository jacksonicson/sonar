package de.tum.in.sonar.collector.tsdb;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;

import org.apache.commons.lang.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TimeSeries implements Iterable<TimeSeriesPoint> {

	private static final Logger logger = LoggerFactory.getLogger(TimeSeries.class);

	private List<TimeSeriesFragment> fragments = new ArrayList<TimeSeriesFragment>();

	@Override
	public Iterator<TimeSeriesPoint> iterator() {
		return new TimeSeriesIterator();
	}

	TimeSeriesFragment newFragment() {
		TimeSeriesFragment fragment = new TimeSeriesFragment();
		fragments.add(fragment);
		return fragment;
	}

	class TimeSeriesIterator implements Iterator<TimeSeriesPoint> {

		final Iterator<TimeSeriesFragment> fragmentsIterator;
		Iterator<TimeSeriesPoint> pointIterator = null;

		private TimeSeriesIterator() {
			fragmentsIterator = fragments.iterator();
			if (fragmentsIterator.hasNext())
				pointIterator = fragmentsIterator.next().iterator();
		}

		@Override
		public boolean hasNext() {
			if (pointIterator == null)
				return false;

			boolean fragmentLeft = fragmentsIterator.hasNext();
			boolean pointLeft = pointIterator.hasNext();
			return fragmentLeft || pointLeft;
		}

		@Override
		public TimeSeriesPoint next() {
			if (pointIterator == null)
				throw new NoSuchElementException();

			if (pointIterator.hasNext())
				return pointIterator.next();

			if (fragmentsIterator.hasNext())
			{
				pointIterator = fragmentsIterator.next().iterator();
				return next();
			}
			
			throw new NoSuchElementException(); 
		}

		@Override
		public void remove() {
			throw new NotImplementedException();
		}

	}
}
