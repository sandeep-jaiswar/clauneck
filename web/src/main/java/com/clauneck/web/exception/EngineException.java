package com.clauneck.web.exception;

/** The Python engine (/api/solve) was unreachable, timed out, or returned an error. Maps to HTTP 502. */
public class EngineException extends RuntimeException {

    public EngineException(String message) {
        super(message);
    }

    public EngineException(String message, Throwable cause) {
        super(message, cause);
    }
}
