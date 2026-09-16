package com.clauneck.web.exception;

import java.util.List;

/**
 * Translated model fails dimensional consistency validation.
 * The schema is structurally valid, but quantities/equations are dimensionally inconsistent.
 * Maps to HTTP 400.
 */
public class DimensionalMismatchException extends RuntimeException {

    private final List<String> validationErrors;

    public DimensionalMismatchException(List<String> validationErrors) {
        super("Model failed dimensional validation: " + String.join("; ", validationErrors));
        this.validationErrors = validationErrors;
    }

    public List<String> getValidationErrors() {
        return validationErrors;
    }
}
