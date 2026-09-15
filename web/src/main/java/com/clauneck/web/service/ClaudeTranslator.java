package com.clauneck.web.service;

import com.clauneck.web.config.TranslatorProperties;
import com.clauneck.web.dto.Quantity;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.exception.ClaudeUnavailableException;
import com.clauneck.web.exception.ModelValidationException;
import com.clauneck.web.exception.TranslationException;
import com.clauneck.web.exception.UnsupportedDomainException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
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

    private static final Set<String> SUPPORTED_DOMAINS = Set.of(
            "physics.mechanics", "mathematics.statistics");

    private static final String SYSTEM_PROMPT = """
            You are a scientific model translator for the Clauneck platform.

            Your role: Convert natural language scientific and mathematical problems into structured Model JSON.

            CRITICAL CONSTRAINTS:
            1. Output ONLY valid JSON matching the schema below. No preamble, no explanation, no markdown code fences.
            2. Supported domains: physics.mechanics, mathematics.statistics.
            3. All quantities must use SI units (m, kg, s, m/s, m/s^2, etc.) or domain-specific units (e.g., "dimensionless", "rad", "deg").
            4. When unit information is missing, use "dimensionless" as the default unit.

            DOMAIN-SPECIFIC STRUCTURE:

            === physics.mechanics (projectile motion) ===
            Quantities: v0 (m/s), angle (deg or rad), mass (kg), g (m/s^2), drag_coeff (dimensionless).
            Equations: d2x/dt2 (ode), d2y/dt2 (ode).
            solver.timeSpan: required for time-dependent solve.
            Example:
            {
              "id": "projectile-1",
              "domain": "physics.mechanics",
              "description": "Projectile motion without drag",
              "quantities": [
                {"name": "v0", "value": 20.0, "siUnit": "m/s", "isKnown": true},
                {"name": "angle", "value": 45.0, "siUnit": "deg", "isKnown": true},
                {"name": "mass", "value": 1.0, "siUnit": "kg", "isKnown": true},
                {"name": "g", "value": 9.81, "siUnit": "m/s^2", "isKnown": true},
                {"name": "drag_coeff", "value": 0.0, "siUnit": "dimensionless", "isKnown": true}
              ],
              "equations": [
                {"lhs": "d2x/dt2", "rhs": "0", "type": "ode"},
                {"lhs": "d2y/dt2", "rhs": "-g", "type": "ode"}
              ],
              "initialConditions": {},
              "solver": {"method": "RK45", "tolerance": 1e-6, "timeSpan": {"start": 0, "end": 5, "numPoints": 1000}}
            }

            === mathematics.statistics ===
            Descriptive stats, distributions, hypothesis tests over datasets.
            Quantities: the dataset (array value), distribution parameters.
            Equations: put exactly one supported operation call in rhs, such as mean(data),
            normal_pdf(x, mu, sigma), or ttest_1samp(data, null_hypothesis).
            solver.timeSpan: not required.
            Example quantities: [{"name": "data", "value": [1, 2, 3, 4, 5],
            "siUnit": "dimensionless", "isKnown": true}].

            GENERAL VALIDATION RULES:
            - isKnown must be true exactly when value is present.
            - For time-dependent problems (ODE, physics.mechanics), provide solver.timeSpan.
            - Unknown/unsupported domains: output error JSON instead.

            If the query is ambiguous, nonsensical, or outside supported domains, output:
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

    public ClaudeTranslator(@Qualifier("translatorRestTemplate") RestTemplate restTemplate,
                             ObjectMapper objectMapper,
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

        if (lastFailure instanceof JsonParseUnusableException) {
            throw new TranslationException(
                    "Claude returned unusable model JSON after " + maxAttempts + " attempt(s)",
                    "Try rephrasing the query with explicit numeric values and units",
                    lastFailure);
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

        if (node == null || !node.isObject()) {
            throw new JsonParseUnusableException("Claude output must be a JSON object");
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

        if (model == null) {
            throw new JsonParseUnusableException("Claude output did not contain a model");
        }

        if (model.getDomain() == null || !SUPPORTED_DOMAINS.contains(model.getDomain())) {
            throw new UnsupportedDomainException(model.getDomain());
        }

        List<String> validationErrors = new ArrayList<>(schemaValidator.validate(node));
        if ("physics.mechanics".equals(model.getDomain())) {
            validatePhysicsParameters(model, validationErrors);
        }
        if (!validationErrors.isEmpty()) {
            throw new ModelValidationException(validationErrors);
        }

        // Audit trail per ADR 0002: set server-side, don't trust the LLM to echo these back correctly.
        model.getMetadata().setSource("llm_translator");
        model.getMetadata().setOriginalQuery(originalQuery);

        return model;
    }

    private void validatePhysicsParameters(ScientificModelDto model, List<String> validationErrors) {
        Map<String, Quantity> quantities = new HashMap<>();
        if (model.getQuantities() != null) {
            for (Quantity quantity : model.getQuantities()) {
                if (quantity != null && quantity.getName() != null) {
                    quantities.put(quantity.getName(), quantity);
                }
            }
        }

        validateGreaterThanZero("v0", effectiveValue(model, quantities, "v0", null), validationErrors);
        validateGreaterThanZero("mass", effectiveValue(model, quantities, "mass", null), validationErrors);
        validateGreaterThanZero("g", effectiveValue(model, quantities, "g", null), validationErrors);

        Double dragCoefficient = effectiveValue(model, quantities, "drag_coeff", 0.0);
        if (dragCoefficient == null || !Double.isFinite(dragCoefficient) || dragCoefficient < 0.0) {
            validationErrors.add("drag_coeff must be greater than or equal to 0");
        }

        Double angle = effectiveValue(model, quantities, "angle", null);
        Quantity angleQuantity = quantities.get("angle");
        if (angle == null || !Double.isFinite(angle)) {
            validationErrors.add("angle must be a finite number between 0 and 90 degrees");
            return;
        }
        if (angleQuantity == null || angleQuantity.getSiUnit() == null) {
            validationErrors.add("angle must declare a unit of deg or rad");
            return;
        }

        double angleDegrees;
        if ("deg".equals(angleQuantity.getSiUnit())) {
            angleDegrees = angle;
        } else if ("rad".equals(angleQuantity.getSiUnit())) {
            angleDegrees = Math.toDegrees(angle);
        } else {
            validationErrors.add("angle must declare a unit of deg or rad");
            return;
        }
        if (angleDegrees < 0.0 || angleDegrees > 90.0) {
            validationErrors.add("angle must be between 0 and 90 degrees");
        }
    }

    private Double effectiveValue(ScientificModelDto model, Map<String, Quantity> quantities,
                                  String name, Double defaultValue) {
        Map<String, Double> initialConditions = model.getInitialConditions();
        if (initialConditions != null && initialConditions.containsKey(name)) {
            return initialConditions.get(name);
        }
        Quantity quantity = quantities.get(name);
        if (quantity == null || quantity.getValue() == null) {
            return defaultValue;
        }
        return quantity.getValue() instanceof Number number ? number.doubleValue() : null;
    }

    private void validateGreaterThanZero(String name, Double value, List<String> validationErrors) {
        if (value == null || !Double.isFinite(value) || value <= 0.0) {
            validationErrors.add(name + " must be greater than 0");
        }
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
