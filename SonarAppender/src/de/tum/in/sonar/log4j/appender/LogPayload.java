package de.tum.in.sonar.log4j.appender;

import java.io.Serializable;

import de.tum.in.sonar.collector.Identifier;
import de.tum.in.sonar.collector.LogMessage;

@SuppressWarnings("serial")
public class LogPayload implements Serializable {
	private Identifier id;
	private LogMessage message;

	public LogPayload(Identifier id, LogMessage message) {
		super();
		this.id = id;
		this.message = message;
	}

	/**
	 * @return the id
	 */
	public Identifier getId() {
		return id;
	}

	/**
	 * @param id
	 *            the id to set
	 */
	public void setId(Identifier id) {
		this.id = id;
	}

	/**
	 * @return the message
	 */
	public LogMessage getMessage() {
		return message;
	}

	/**
	 * @param message
	 *            the message to set
	 */
	public void setMessage(LogMessage message) {
		this.message = message;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see java.lang.Object#toString()
	 */
	@Override
	public String toString() {
		return "LogPayload [id=" + id + ", message=" + message + "]";
	}

}
