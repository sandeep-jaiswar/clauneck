package com.clauneck.web.exception;

/**
 * Query could not be turned into a Model: Claude explicitly declined
 * (ambiguous/nonsensical input), or its output could not be parsed as JSON
 * after exhausting retries. Maps to HTTP 400.
 */
public class TranslationException extends RuntimeException {

    private final String suggestion;

    public TranslationException(String message, String suggestion) {
        super(message);
        this.suggestion = suggestion;
    }

    public TranslationException(String message, String suggestion, Throwable cause) {
        super(message, cause);
        this.suggestion = suggestion;
    }

    public String getSuggestion() {
        return suggestion;
    }
}
