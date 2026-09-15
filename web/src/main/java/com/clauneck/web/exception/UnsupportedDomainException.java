package com.clauneck.web.exception;

import java.util.Collection;

/**
 * The translated model's domain is not in the supported set. Maps to HTTP 501.
 */
public class UnsupportedDomainException extends RuntimeException {

    private final String domain;

    public UnsupportedDomainException(String domain, Collection<String> supportedDomains) {
        super("Domain '" + domain + "' is not supported. Supported domains: "
                + String.join(", ", supportedDomains));
        this.domain = domain;
    }

    public String getDomain() {
        return domain;
    }
}
