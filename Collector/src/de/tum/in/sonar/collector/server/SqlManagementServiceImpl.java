package de.tum.in.sonar.collector.server;

import java.beans.PropertyVetoException;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.log4j.Logger;
import org.apache.thrift.TException;

import com.mchange.v2.c3p0.ComboPooledDataSource;

import de.tum.in.sonar.collector.BundledSensorConfiguration;
import de.tum.in.sonar.collector.LogMessage;
import de.tum.in.sonar.collector.LogsQuery;
import de.tum.in.sonar.collector.ManagementService;
import de.tum.in.sonar.collector.Parameter;
import de.tum.in.sonar.collector.SensorConfiguration;
import de.tum.in.sonar.collector.SensorType;
import de.tum.in.sonar.collector.TimeSeriesQuery;
import de.tum.in.sonar.collector.TransferableTimeSeriesPoint;
import de.tum.in.sonar.collector.log.LogDatabase;
import de.tum.in.sonar.collector.tsdb.InvalidLabelException;
import de.tum.in.sonar.collector.tsdb.Query;
import de.tum.in.sonar.collector.tsdb.QueryException;
import de.tum.in.sonar.collector.tsdb.TimeSeries;
import de.tum.in.sonar.collector.tsdb.TimeSeriesDatabase;
import de.tum.in.sonar.collector.tsdb.TimeSeriesPoint;
import de.tum.in.sonar.collector.tsdb.UnresolvableException;

public class SqlManagementServiceImpl implements ManagementService.Iface {

	private static final Logger logger = Logger.getLogger(SqlManagementServiceImpl.class);

	private TimeSeriesDatabase tsdb;

	private LogDatabase logdb;

	private ComboPooledDataSource cpds;

	public SqlManagementServiceImpl() throws PropertyVetoException {
		cpds = new ComboPooledDataSource();
		cpds.setDriverClass("com.mysql.jdbc.Driver");
		cpds.setJdbcUrl("jdbc:mysql://localhost/sonar");
		cpds.setUser("root");
		cpds.setPassword("root");
		cpds.setMinPoolSize(1);
		cpds.setAcquireIncrement(5);
		cpds.setMaxPoolSize(50);
	}

	@Override
	public List<LogMessage> queryLogs(LogsQuery query) throws TException {
		List<LogMessage> logMessages = null;
		try {
			logMessages = logdb.run(query);
			return logMessages;
		} catch (QueryException e) {
			logger.error("Error while executing query", e);
		} catch (UnresolvableException e) {
			logger.error("Error while executing query", e);
		} catch (InvalidLabelException e) {
			logger.error("Error while executing query", e);
		}
		return new ArrayList<LogMessage>();
	}

	@Override
	public List<TransferableTimeSeriesPoint> query(TimeSeriesQuery query) throws TException {
		Query tsdbQuery = new Query(query.getSensor(), query.getStartTime(), query.getStopTime());
		tsdbQuery.setHostname(query.hostname);
		try {
			TimeSeries timeSeries = tsdb.run(tsdbQuery);
			List<TransferableTimeSeriesPoint> tsPoints = new ArrayList<TransferableTimeSeriesPoint>(100);

			for (TimeSeriesPoint point : timeSeries) {
				TransferableTimeSeriesPoint tsPoint = new TransferableTimeSeriesPoint();
				tsPoints.add(tsPoint);

				tsPoint.setTimestamp(point.getTimestamp());
				tsPoint.setValue(point.getValue());

				if (point.getLabels() != null) {
					Set<String> labels = new HashSet<String>();
					Collections.addAll(labels, point.getLabels());
					tsPoint.setLabels(labels);
				}
			}

			return tsPoints;

		} catch (QueryException e) {
			logger.error("Error while executing query", e);
		} catch (UnresolvableException e) {
			logger.trace("Error while mapping in query", e);
		}

		return new ArrayList<TransferableTimeSeriesPoint>();
	}

	@Override
	public ByteBuffer fetchSensor(String name) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("select binary from sensors where name = ?");
			st.setString(1, name);
			ResultSet res = st.executeQuery();
			if (!res.next()) {
				logger.warn("Could not find sensor binary for " + name);
				return null;
			}

			// Copy stuff
			InputStream in = res.getBlob(1).getBinaryStream();
			ByteArrayOutputStream out = new ByteArrayOutputStream();
			byte[] buffer = new byte[128];
			int len = 0;
			while ((len = in.read(buffer)) > 0) {
				out.write(buffer, 0, len);
			}

			// Return binary
			return ByteBuffer.wrap(out.toByteArray());

		} catch (SQLException e) {
			logger.error("SQL exception while fetching sensor " + name, e);
		} catch (IOException e) {
			logger.warn("Could not load sensor binary for " + name);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}

		logger.warn("Could not find sensor binary for " + name);
		return null;
	}

	@Override
	public String sensorHash(String name) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("select md5 from sensors where name = ?");
			st.setString(1, name);
			ResultSet res = st.executeQuery();
			if (!res.next()) {
				logger.warn("Could not find sensor hash for " + name);
				return null;
			}

			return res.getString(1);

		} catch (SQLException e) {
			logger.error("SQL exception while fetching sensor " + name, e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}

		return null;
	}

	@Override
	public void deploySensor(String name, ByteBuffer file) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();

			// Build input stream from buffer
			ByteArrayInputStream in = new ByteArrayInputStream(file.array());

			// Run query
			PreparedStatement st = con.prepareStatement("update sensors set name = ? where name = ?");
			st.setBlob(1, in);
			st.setString(2, name);
			st.executeUpdate();

		} catch (SQLException e) {
			logger.error("SQL exception while deploying sensor " + name, e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}
	}

	@Override
	public Set<String> getAllSensors() throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("select name from sensors");
			ResultSet res = st.executeQuery();

			Set<String> names = new HashSet<String>();
			while (res.next()) {
				names.add(res.getString(1));
			}

			return names;

		} catch (SQLException e) {
			logger.error("SQL exception while fetching all sensor names", e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}

		logger.warn("Could not fetch all sensor names");
		return null;
	}

	@Override
	public boolean hasBinary(String name) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("select zip from sensors where name = ? and zip is not NULL");
			st.setString(1, name);
			ResultSet res = st.executeQuery();
			return res.next();
		} catch (SQLException e) {
			logger.error("SQL exception while fetching all sensor names", e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}

		logger.warn("Could not check whether sensor " + name + " has a binary");
		return false;
	}

	@Override
	public Set<String> getSensorLabels(String sensor) throws TException {
		return new HashSet<String>();
	}

	@Override
	public void delSensor(String name) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("delete from sensors where name = ?");
			st.setString(1, name);
			st.executeUpdate();
		} catch (SQLException e) {
			logger.error("SQL exception while fetching all sensor names", e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}
	}

	@Override
	public void setSensorLabels(String sensor, Set<String> labels) throws TException {
		// pass
	}

	@Override
	public void setSensorConfiguration(String name, SensorConfiguration configuration) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();

			PreparedStatement st = con
					.prepareStatement("update sensors set interval = ?, type = ?, extends = ? where name = ?");
			st.setLong(1, configuration.getInterval());
			st.setInt(2, configuration.getSensorType().getValue());
			st.setString(3, configuration.getSensorExtends());
			st.setString(4, name);
			st.executeUpdate();

			st = con.prepareStatement("select id from sensors where name = ?");
			ResultSet rid = st.executeQuery();
			rid.next();
			int id = rid.getInt(1);

			for (Parameter param : configuration.getParameters()) {
				PreparedStatement stParam = con
						.prepareStatement("insert into params (SENSOR_ID, param, value, extend) values (?,?,?,?)");
				stParam.setInt(1, id);
				stParam.setString(2, param.getKey());
				stParam.setString(3, param.getValue());
				stParam.setString(4, param.getExtendSensor());
				st.execute();
			}
		} catch (SQLException e) {
			logger.error("SQL exception while fetching all sensor names", e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}
	}

	@Override
	public SensorConfiguration getSensorConfiguration(String name) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();

			SensorConfiguration config = new SensorConfiguration();

			PreparedStatement st = con
					.prepareStatement("select id, interval, type, extends from sensors where name = ?");
			st.setString(1, name);
			ResultSet res = st.executeQuery();
			if (!res.next()) {
				logger.warn("Could not load sensor configuration for sensor " + name);
				return null;
			}

			config.setInterval(res.getLong(2));
			config.setSensorType(SensorType.findByValue(res.getInt(3)));
			config.setSensorExtends(res.getString(4));

			st = con.prepareStatement("select param, value, extend from params where SENSOR_ID = ? ");
			res = st.executeQuery();
			while (res.next()) {
				Parameter param = new Parameter();
				param.setKey(res.getString(1));
				param.setValue(res.getString(2));
				param.setExtendSensor(res.getString(3));
				config.addToParameters(param);
			}

			return config;
		} catch (SQLException e) {
			logger.error("SQL exception with sensor " + name, e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}

		logger.warn("Could not read sensor configuration for sensor " + name);
		return null;
	}

	@Override
	public Set<String> getSensorNames() throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("select name from sensors");
			ResultSet res = st.executeQuery();
			Set<String> sensors = new HashSet<String>();
			while (res.next()) {
				sensors.add(res.getString(1));
			}
			return sensors;
		} catch (SQLException e) {
			logger.error("SQL exception while fetching sensor names", e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}

		logger.warn("Could not read sensor names");
		return null;
	}

	@Override
	public void updateSensorConfiguration(String name, SensorConfiguration configuration, Set<String> labels)
			throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();

			PreparedStatement st = con
					.prepareStatement("update sensors set interval = ?, type = ?, extends = ? where name = ?");
			st.setLong(1, configuration.getInterval());
			st.setInt(2, configuration.getSensorType().getValue());
			st.setString(3, configuration.getSensorExtends());
			st.setString(4, name);
			st.executeUpdate();

			st = con.prepareStatement("select id from sensors where name = ?");
			ResultSet rid = st.executeQuery();
			rid.next();
			int id = rid.getInt(1);

			for (Parameter param : configuration.getParameters()) {
				PreparedStatement stParam = con
						.prepareStatement("insert into params (SENSOR_ID, param, value, extend) values (?,?,?,?)");
				stParam.setInt(1, id);
				stParam.setString(2, param.getKey());
				stParam.setString(3, param.getValue());
				stParam.setString(4, param.getExtendSensor());
				st.execute();
			}
		} catch (SQLException e) {
			logger.error("SQL exception while fetching all sensor names", e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}
	}

	@Override
	public void addHost(String hostname) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("insert into hosts (name) values(?)");
			st.setString(1, hostname);
			st.execute();
		} catch (SQLException e) {
			logger.error("SQL exception while adding host " + hostname, e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}
		logger.warn("Could not add hostname " + hostname);
	}

	@Override
	public void addHostExtension(String hostname, String virtualHostName) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("update hosts set extends = ? where name = ?");
			st.setString(1, virtualHostName);
			st.setString(2, hostname);
			st.execute();
		} catch (SQLException e) {
			logger.error("SQL exception while adding host extension " + hostname, e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}
		logger.warn("Could not add host extension " + hostname);
	}

	@Override
	public String getHostExtension(String hostname) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("select extends from hosts where name = ?");
			st.setString(1, hostname);
			ResultSet res = st.executeQuery();
			if (!res.next()) {
				logger.warn("Could not load host extension for host " + hostname);
				return null;
			}

			return res.getString(1);

		} catch (SQLException e) {
			logger.error("SQL exception while adding host extension " + hostname, e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
				}
		}

		logger.warn("Could not get host extension " + hostname);
		return null;
	}

	@Override
	public Set<String> getAllHosts() throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("select name hosts");
			ResultSet res = st.executeQuery();
			Set<String> hosts = new HashSet<String>();
			while (res.next()) {
				hosts.add(res.getString(1));
			}
			return hosts;

		} catch (SQLException e) {
			logger.error("SQL exception while loading all hosts", e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
				}
		}

		logger.warn("Could not load all hosts");
		return null;
	}

	@Override
	public void delHost(String hostname) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("delete from hosts where name = ?");
			st.setString(1, hostname);
			st.execute();
		} catch (SQLException e) {
			logger.error("SQL exception while deleting host " + hostname, e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}
		logger.warn("Could not delete host " + hostname);
	}

	@Override
	public void setHostLabels(String hostname, Set<String> labels) throws TException {
		// pass
	}

	@Override
	public Set<String> getLabels(String hostname) throws TException {
		return new HashSet<String>();
	}

	@Override
	public void setSensor(String hostname, String sensor, boolean activate) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();

			PreparedStatement st;
			ResultSet res;

			st = con.prepareStatement("select id from sensors where name = ?");
			res = st.executeQuery();
			if (!res.next())
				return;
			int idSensor = res.getInt(1);

			st = con.prepareStatement("select id from hosts where name = ?");
			res = st.executeQuery();
			if (!res.next())
				return;
			int idHost = res.getInt(1);

			if (activate) {
				st = con.prepareStatement("insert into host2sensors values (?,?)");
				st.setInt(1, idHost);
				st.setInt(2, idSensor);
				st.execute();
			} else {
				st = con.prepareStatement("delete from host2sensors where HOST_ID=? and SENSOR_ID=?");
				st.setInt(1, idHost);
				st.setInt(2, idSensor);
				st.execute();
			}

		} catch (SQLException e) {
			logger.error("SQL exception while adding host extension " + hostname, e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
					// pass
				}
		}
		logger.warn("Could not add host extension " + hostname);
	}

	@Override
	public Set<String> getSensors(String hostname) throws TException {
		Connection con = null;
		try {
			con = cpds.getConnection();
			PreparedStatement st = con.prepareStatement("select name sensors");
			ResultSet res = st.executeQuery();
			Set<String> sensors = new HashSet<String>();
			while (res.next()) {
				sensors.add(res.getString(1));
			}
			return sensors;

		} catch (SQLException e) {
			logger.error("SQL exception while loading all sensors", e);
		} finally {
			if (con != null)
				try {
					con.close();
				} catch (SQLException e) {
				}
		}

		logger.warn("Could not load all sensors");
		return null;
	}

	@Override
	public BundledSensorConfiguration getBundledSensorConfiguration(String sensor, String hostname) throws TException {
		// TODO Auto-generated method stub
		return null;
	}

	public void setTsdb(TimeSeriesDatabase tsdb) {
		this.tsdb = tsdb;
	}

	public void setLogdb(LogDatabase logdb) {
		this.logdb = logdb;
	}
}
