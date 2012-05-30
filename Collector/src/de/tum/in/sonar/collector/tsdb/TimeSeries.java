package de.tum.in.sonar.collector.tsdb;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class TimeSeries implements Iterable<DataPoint> {

	private List<TimeSeriesFragment> fragments = new ArrayList<TimeSeriesFragment>();

	@Override
	public Iterator<DataPoint> iterator() {
		return new TimeSeriesIterator();
	}

	TimeSeriesFragment newFragment()
	{
		TimeSeriesFragment fragment = new TimeSeriesFragment();
		fragments.add(fragment); 
		return fragment; 
	}

	class TimeSeriesIterator<DataPoint> implements Iterator {

		int fragment = 0;
		Iterator<DataPoint> listIterator = null;

		@Override
		public boolean hasNext() {
			// TODO Auto-generated method stub
			return false;
		}

		@Override
		public Object next() {
			// TODO Auto-generated method stub
			return null;
		}

		@Override
		public void remove() {
			// TODO Auto-generated method stub

		}

	}
}
