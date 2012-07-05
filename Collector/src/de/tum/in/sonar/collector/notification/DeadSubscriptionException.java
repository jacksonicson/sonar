package de.tum.in.sonar.collector.notification;

public class DeadSubscriptionException extends Exception {

	private static final long serialVersionUID = 7766938622998289471L;

	private final Subscription subscription;

	public DeadSubscriptionException(Subscription subscription) {
		this.subscription = subscription;
	}

	Subscription getSubscription() {
		return this.subscription;
	}

}
