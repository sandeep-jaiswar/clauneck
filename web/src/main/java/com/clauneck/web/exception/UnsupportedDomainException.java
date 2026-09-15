package com.clauneck.web.exception;

/**
 * The translated model's domain is not in the supported set. Maps to HTTP 501.
 */
public class UnsupportedDomainException extends RuntimeException {

    private final String domain;

    public UnsupportedDomainException(String domain) {
        super("Domain '" + domain + "' is not supported. Supported domains: "
                + "physics.mechanics, mathematics.statistics");
        this.domain = domain;
    }

    public String getDomain() {
        return domain;
    }
}
