package com.clauneck.web.exception;

import com.clauneck.web.dto.ErrorResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class PrototypeExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(PrototypeExceptionHandler.class);

    @ExceptionHandler(TranslationException.class)
    public ResponseEntity<ErrorResponse> handleTranslationError(TranslationException e) {
        log.warn("Translation failed: {}", e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(new ErrorResponse(
                "TRANSLATION_FAILED", "Could not translate query", e.getMessage(), e.getSuggestion()));
    }

    @ExceptionHandler(UnsupportedDomainException.class)
    public ResponseEntity<ErrorResponse> handleUnsupportedDomain(UnsupportedDomainException e) {
        log.warn("Unsupported domain requested: {}", e.getDomain());
        return ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED).body(new ErrorResponse(
                "DOMAIN_NOT_SUPPORTED", e.getMessage(), null,
                "Try a physics.mechanics query, e.g. 'Ball at 10 m/s, 30 degrees, 1 kg mass'"));
    }

    @ExceptionHandler(ModelValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidationError(ModelValidationException e) {
        log.warn("Model failed schema validation: {}", e.getValidationErrors());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(new ErrorResponse(
                "VALIDATION_FAILED", "Translated model failed schema validation",
                String.join("; ", e.getValidationErrors()),
                "Try rephrasing with explicit numeric values and units"));
    }

    @ExceptionHandler(ClaudeUnavailableException.class)
    public ResponseEntity<ErrorResponse> handleClaudeUnavailable(ClaudeUnavailableException e) {
        log.error("Claude API unavailable", e);
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(new ErrorResponse(
                "SERVICE_UNAVAILABLE", "Claude API is temporarily unavailable", e.getMessage(),
                "Please retry in a few moments"));
    }

    @ExceptionHandler(EngineException.class)
    public ResponseEntity<ErrorResponse> handleEngineError(EngineException e) {
        log.error("Engine call failed", e);
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body(new ErrorResponse(
                "ENGINE_UNAVAILABLE", "The solver engine is unavailable or returned an error",
                "The solver engine request failed",
                "Confirm the engine is running (POST /health on its port) and retry"));
    }
}
