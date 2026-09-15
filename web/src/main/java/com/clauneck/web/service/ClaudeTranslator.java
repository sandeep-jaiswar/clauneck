package com.clauneck.web.service;

import com.clauneck.web.config.TranslatorProperties;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.exception.ClaudeUnavailableException;
import com.clauneck.web.exception.ModelValidationException;
import com.clauneck.web.exception.TranslationException;
import com.clauneck.web.exception.UnsupportedDomainException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

/**
 * Translates a natural-language physics query into a schema-validated
 * ScientificModelDto, per spec.md's "Prompt Design" section and ADR 0002
 * (LLM does translation only, never computation).
 */
@Service
public class ClaudeTranslator {

    private static final Logger log = LoggerFactory.getLogger(ClaudeTranslator.class);

    private static final String SUPPORTED_DOMAIN = "physics.mechanics";

    private static final String SYSTEM_PROMPT = """
            You are a scientific model translator for the Clauneck platform.

            Your role: Convert natural language physics problems into structured Model JSON.

            CRITICAL CONSTRAINTS:
            1. Output ONLY valid JSON matching the schema below. No preamble, no explanation, no markdown code fences.
            2. Domain: ONLY physics.mechanics (projectile motion). Reject other domains.
            3. All quantities must use SI units (m, kg, s, m/s, m/s^2, etc.).
            4. Include drag_coeff only if user mentions drag, air resistance, or friction.
            5. Default values:
               - g (gravity): 9.81 m/s^2
               - angle: 45 degrees (if not specified)
               - mass: 1.0 kg (if not specified)
               - drag_coeff: 0.0 (if not mentioned)

            SCHEMA STRUCTURE (required fields):
            {
              "id": "unique_identifier",
              "domain": "physics.mechanics",
              "description": "Human-readable description",
              "quantities": [
                {"name": "v0", "value": <number>, "siUnit": "m/s", "isKnown": true},
                {"name": "angle", "value": <degrees>, "siUnit": "deg", "isKnown": true},
                {"name": "mass", "value": <kg>, "siUnit": "kg", "isKnown": true},
                {"name": "g", "value": 9.81, "siUnit": "m/s^2", "isKnown": true},
                {"name": "drag_coeff", "value": <coefficient>, "siUnit": "dimensionless", "isKnown": true}
              ],
              "equations": [
                {
                  "lhs": "d2x/dt2",
                  "rhs": "-drag_coeff * vx * sqrt(vx^2 + vy^2) / mass",
                  "type": "ode",
                  "description": "Horizontal acceleration with drag"
                },
                {
                  "lhs": "d2y/dt2",
                  "rhs": "-g - drag_coeff * vy * sqrt(vx^2 + vy^2) / mass",
                  "type": "ode",
                  "description": "Vertical acceleration with gravity and drag"
                }
              ],
              "initialConditions": {
                "v0": <number>,
                "angle": <degrees>,
                "mass": <kg>,
                "g": 9.81,
                "drag_coeff": <coefficient>
              },
              "solver": {
                "method": "RK45",
                "tolerance": 1e-6,
                "timeSpan": {"start": 0, "end": 5.0, "numPoints": 5000}
              },
              "metadata": {
                "source": "llm_translator",
                "originalQuery": "<user's exact query>"
              }
            }

            VALIDATION RULES:
            - v0 > 0 (positive velocity)
            - angle: 0-90 degrees (launching angle, not negative)
            - mass > 0
            - g > 0
            - drag_coeff >= 0

            If the query is ambiguous, nonsensical, or outside physics.mechanics, output this JSON error
            instead of a model:
            {
              "error": true,
              "reason": "Explanation of why this query cannot be translated",
              "suggestion": "What the user should ask instead"
            }
            """;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final SchemaValidator schemaValidator;
    private final TranslatorProperties properties;

    public ClaudeTranslator(RestTemplate restTemplate, ObjectMapper objectMapper,
                             SchemaValidator schemaValidator, TranslatorProperties properties) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
        this.schemaValidator = schemaValidator;
        this.properties = properties;
    }

    public ScientificModelDto translate(String query) {
        int maxAttempts = Math.max(1, properties.getMaxRetries());
        Exception lastFailure = null;

        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                String rawOutput = callClaudeApi(query);
                return parseAndValidate(rawOutput, query);
            } catch (TranslationException | UnsupportedDomainException | ModelValidationException e) {
                // Claude responded; the response itself is the problem. Retrying with the
                // exact same prompt won't help beyond parse failures, which are handled
                // separately below — propagate immediately.
                throw e;
            } catch (JsonParseUnusableException e) {
                lastFailure = e;
                log.warn("Attempt {}/{}: Claude output was not parseable JSON, retrying: {}",
                        attempt, maxAttempts, e.getMessage());
            } catch (ResourceAccessException | HttpStatusCodeException e) {
                lastFailure = e;
                log.warn("Attempt {}/{}: Claude API call failed transiently: {}",
                        attempt, maxAttempts, e.getMessage());
            }
        }

        throw new ClaudeUnavailableException(
                "Claude API did not return a usable response after " + maxAttempts + " attempt(s)",
                lastFailure);
    }

    private String callClaudeApi(String query) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("x-api-key", properties.getApiKey());
        headers.set("anthropic-version", properties.getAnthropicVersion());

        ObjectNode body = objectMapper.createObjectNode();
        body.put("model", properties.getModel());
        body.put("max_tokens", properties.getMaxTokens());
        body.put("system", SYSTEM_PROMPT);
        ObjectNode userMessage = body.putArray("messages").addObject();
        userMessage.put("role", "user");
        userMessage.put("content", buildUserPrompt(query));

        HttpEntity<String> request = new HttpEntity<>(body.toString(), headers);

        AnthropicResponse response = restTemplate.postForObject(
                properties.getApiUrl(), request, AnthropicResponse.class);

        if (response == null || response.getContent() == null || response.getContent().isEmpty()) {
            throw new JsonParseUnusableException("Claude API returned an empty response");
        }
        String text = response.getContent().get(0).getText();
        if (text == null || text.isBlank()) {
            throw new JsonParseUnusableException("Claude API returned no text content");
        }
        return text;
    }

    private String buildUserPrompt(String query) {
        return "Translate this physics query into Model JSON:\n\n\"" + query + "\"\n\n"
                + "Output ONLY the JSON. No explanation.";
    }

    private ScientificModelDto parseAndValidate(String rawOutput, String originalQuery) {
        JsonNode node;
        try {
            node = objectMapper.readTree(stripMarkdownFences(rawOutput));
        } catch (Exception e) {
            throw new JsonParseUnusableException("Claude output was not valid JSON: " + e.getMessage());
        }

        if (isDeclineResponse(node)) {
            String reason = node.path("reason").asText("Query could not be translated");
            String suggestion = node.path("suggestion").asText(null);
            throw new TranslationException(reason, suggestion);
        }

        ScientificModelDto model;
        try {
            model = objectMapper.treeToValue(node, ScientificModelDto.class);
        } catch (Exception e) {
            throw new JsonParseUnusableException(
                    "Claude output did not match the expected model shape: " + e.getMessage());
        }

        if (model.getDomain() == null || !SUPPORTED_DOMAIN.equals(model.getDomain())) {
            throw new UnsupportedDomainException(model.getDomain());
        }

        List<String> validationErrors = schemaValidator.validate(node);
        if (!validationErrors.isEmpty()) {
            throw new ModelValidationException(validationErrors);
        }

        // Audit trail per ADR 0002: set server-side, don't trust the LLM to echo these back correctly.
        model.getMetadata().setSource("llm_translator");
        model.getMetadata().setOriginalQuery(originalQuery);

        return model;
    }

    private boolean isDeclineResponse(JsonNode node) {
        if (!node.has("error")) {
            return false;
        }
        JsonNode errorNode = node.get("error");
        return errorNode.asBoolean(false) || "true".equalsIgnoreCase(errorNode.asText(""));
    }

    private String stripMarkdownFences(String text) {
        String trimmed = text.trim();
        if (trimmed.startsWith("```")) {
            int firstNewline = trimmed.indexOf('\n');
            int lastFence = trimmed.lastIndexOf("```");
            if (firstNewline != -1 && lastFence > firstNewline) {
                return trimmed.substring(firstNewline + 1, lastFence).trim();
            }
        }
        return trimmed;
    }

    /** Internal signal that the model call needs a retry due to unusable output, not a real translation failure. */
    private static class JsonParseUnusableException extends RuntimeException {
        JsonParseUnusableException(String message) {
            super(message);
        }
    }
}
