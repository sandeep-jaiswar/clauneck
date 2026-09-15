package com.clauneck.web.exception;

import java.util.List;

/**
 * Claude produced parseable JSON with the right domain, but it fails
 * structural validation against schemas/model.schema.json. Maps to HTTP 400.
 */
public class ModelValidationException extends RuntimeException {

    private final List<String> validationErrors;

    public ModelValidationException(List<String> validationErrors) {
        super("Model failed schema validation: " + String.join("; ", validationErrors));
        this.validationErrors = validationErrors;
    }

    public List<String> getValidationErrors() {
        return validationErrors;
    }
}
