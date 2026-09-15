package com.clauneck.web.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.time.Instant;

/** Matches the error shape in spec.md's API contract appendix. */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ErrorResponse {

    private String error;
    private String message;
    private String details;
    private String suggestion;
    private String timestamp;

    public ErrorResponse() {
    }

    public ErrorResponse(String error, String message, String details, String suggestion) {
        this.error = error;
        this.message = message;
        this.details = details;
        this.suggestion = suggestion;
        this.timestamp = Instant.now().toString();
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getDetails() {
        return details;
    }

    public void setDetails(String details) {
        this.details = details;
    }

    public String getSuggestion() {
        return suggestion;
    }

    public void setSuggestion(String suggestion) {
        this.suggestion = suggestion;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}
