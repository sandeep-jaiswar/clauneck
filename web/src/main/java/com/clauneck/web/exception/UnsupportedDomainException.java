package com.clauneck.web.exception;

/**
 * The translated model's domain is not in the supported set. Maps to HTTP 501.
 */
public class UnsupportedDomainException extends RuntimeException {

    private final String domain;

    public UnsupportedDomainException(String domain) {
        super("Domain '" + domain + "' is not supported. Supported domains: physics.mechanics, " +
              "mathematics.algebra, mathematics.calculus, mathematics.linear_algebra, " +
              "mathematics.statistics, mathematics.trigonometry, mathematics.number_theory, " +
              "mathematics.geometry, mathematics.optimization, mathematics.complex_numbers, mathematics.ode");
        this.domain = domain;
    }

    public String getDomain() {
        return domain;
    }
}
