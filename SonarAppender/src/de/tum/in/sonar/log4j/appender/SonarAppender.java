package de.tum.in.sonar.log4j.appender;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;

import org.apache.log4j.Appender;
import org.apache.log4j.AppenderSkeleton;
import org.apache.log4j.spi.LoggingEvent;
import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TFramedTransport;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

import de.tum.in.sonar.collector.CollectService.Client;
import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.LogMessage;

/**
 * Implements a Sonar client to send logs to a remote Sonar server
 * 
 * @author Deepak Srinathan
 * 
 */
public class SonarAppender extends AppenderSkeleton implements Appender {

	// the default server
	private String server = "localhost";

	// port number of the remote sonar server
	private int port = 7922;

	// the host name of the machine from whcih logs are generated
	private String hostname = null;

	// name of the sensor to be logged to
	private String sensor = null;

	// Sonar client
	private TTransport transport = null;
	private Client client = null;

	/**
	 * Send a log message to the Sonar Log Server.
	 */
	@Override
	protected synchronized void append(LoggingEvent event) {

		boolean connected = connectIfNeeded();

		if (!connected) {
			getErrorHandler().error("No connection to the client");
			return;
		}

		Identifier id = new Identifier();

		// convert timestamp to unix timestamp
		id.setTimestamp(event.getTimeStamp() / 1000);
		id.setSensor(getSensor());
		id.setHostname(getHostname());

		LogMessage message = new LogMessage();
		message.setLogLevel(event.getLevel().getSyslogEquivalent());
		message.setLogMessage(event.getMessage().toString());
		message.setProgramName(event.getLoggerName());
		try {
			client.logMessage(id, message);
		} catch (TException e) {
			handleError("TException occured while logging", e);
		} catch (Exception e) {
			handleError("Exception occured while logging", e);
		}
	}

	/**
	 * Close the connection to the server
	 */
	@Override
	public synchronized void close() {
		if (isConnected()) {
			transport.close();
		}
	}

	/**
	 * Does not require a layout, so return false
	 */
	@Override
	public boolean requiresLayout() {
		return false;
	}

	/**
	 * Establish connection with the Sonar Server
	 * 
	 * @throws TTransportException
	 * @throws UnknownHostException
	 * @throws IOException
	 */
	private void establishConnection() throws TTransportException, UnknownHostException, IOException {
		final TSocket socket = new TSocket(getServer(), getPort());
		TTransport transport = new TFramedTransport(socket);
		transport.open();

		TProtocol protocol = new TBinaryProtocol(transport);
		client = new Client(protocol);
	}

	/**
	 * Check if connected, if not , drop the current connection and establish a
	 * new connection
	 * 
	 * @return
	 */
	private boolean connectIfNeeded() {
		if (isConnected()) {
			return true;
		}

		// connection was dropped, establish new connection
		if (transport != null && !transport.isOpen()) {
			transport.close();
		}

		try {
			establishConnection();
			return true;
		} catch (TTransportException e) {
			handleError("TTransportException on connect", e);
		} catch (UnknownHostException e) {
			handleError("UnknownHostException on connect", e);
		} catch (IOException e) {
			handleError("IOException on connect", e);
		} catch (Exception e) {
			handleError("Unhandled Exception on connect", e);
		}
		return false;
	}

	/**
	 * Check if connected
	 * 
	 * @return true if connected false if not connected
	 */
	public synchronized boolean isConnected() {
		return transport != null && transport.isOpen();
	}

	/**
	 * General error handler
	 * 
	 * @param failure
	 * @param e
	 */
	private void handleError(final String failure, final Exception e) {
		getErrorHandler().error(
				"Failure in SonarAppender: name=[" + name + "], failure=[" + failure + "], exception=["
						+ e.getMessage() + "]");
	}

	public String getServer() {
		return server;
	}

	public void setServer(String server) {
		Validator.notEmptyString(server, "Server field cannot be empty");
		this.server = server;
	}

	public int getPort() {
		return port;
	}

	public void setPort(int port) {
		Validator.positiveInteger(port, "Port number should be a possitive integer");
		this.port = port;
	}

	public String getHostname() {
		if (hostname == null) {
			try {
				InetAddress addr = InetAddress.getLocalHost();
				hostname = addr.getHostName();
			} catch (UnknownHostException uhe) {
				hostname = "UNKNOWN_HOST";
			}
		}
		return hostname;
	}

	public void setHostname(String hostname) {
		this.hostname = hostname;
	}

	public String getSensor() {
		return sensor;
	}

	public void setSensor(String sensor) {
		Validator.notEmptyString(sensor, "Sensor field cannot be empty");
		this.sensor = sensor;
	}

	@Override
	public void finalize() {
		close();
		super.finalize();
	}
}
