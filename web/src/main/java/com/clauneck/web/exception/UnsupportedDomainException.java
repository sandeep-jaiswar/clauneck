package com.clauneck.web.exception;

/**
 * The translated model's domain isn't physics.mechanics. Maps to HTTP 501
 * per spec.md FR5 ("other domains return 501").
 */
public class UnsupportedDomainException extends RuntimeException {

    private final String domain;

    public UnsupportedDomainException(String domain) {
        super("Domain '" + domain + "' is not supported; only physics.mechanics is implemented");
        this.domain = domain;
    }

    public String getDomain() {
        return domain;
    }
}
