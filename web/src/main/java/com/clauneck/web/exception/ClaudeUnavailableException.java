package com.clauneck.web.exception;

/**
 * The Claude API itself could not be reached (network/timeout/5xx) after
 * exhausting retries — distinct from TranslationException, where Claude
 * responded but declined or produced unusable output. Maps to HTTP 503
 * per spec.md NFR2.
 */
public class ClaudeUnavailableException extends RuntimeException {

    public ClaudeUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}
