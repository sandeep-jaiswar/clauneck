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
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

/**
 * Translates a natural-language query into a schema-validated ScientificModelDto.
 * Loads domain-specific prompt fragments from translator-prompts/*.txt files at startup.
 * Per spec.md and ADR 0002: LLM does translation only, never computation.
 */
@Service
public class ClaudeTranslator {

    private static final Logger log = LoggerFactory.getLogger(ClaudeTranslator.class);

    private static final Map<String, String> DOMAIN_PROMPTS = loadDomainPrompts();
    private static final Set<String> SUPPORTED_DOMAINS =
            Collections.unmodifiableSet(DOMAIN_PROMPTS.keySet());
    private static final String SYSTEM_PROMPT = buildSystemPrompt();

    private static Map<String, String> loadDomainPrompts() {
        Map<String, String> prompts = new TreeMap<>();  // Alphabetical iteration
        try {
            ClassPathResource resource = new ClassPathResource("translator-prompts");
            // Load all .txt files from classpath
            var files = Files.list(Paths.get(resource.getURI()))
                    .filter(p -> p.toString().endsWith(".txt"))
                    .collect(Collectors.toList());
            
            for (var path : files) {
                String filename = path.getFileName().toString();
                String domain = filename.replace(".txt", "");
                String content = new String(Files.readAllBytes(path), StandardCharsets.UTF_8);
                prompts.put(domain, content);
                log.debug("Loaded prompt for domain: {}", domain);
            }
        } catch (Exception e) {
            log.error("Failed to load domain prompts from classpath", e);
            // Fallback: provide empty map (will be caught by validation)
        }
        return prompts;
    }

    private static String buildSystemPrompt() {
        StringBuilder sb = new StringBuilder();
        sb.append("""
                You are a scientific model translator for the Clauneck platform.

                Your role: Convert natural language scientific and mathematical problems into structured Model JSON.

                CRITICAL CONSTRAINTS:
                1. Output ONLY valid JSON matching the schema below. No preamble, no explanation, no markdown code fences.
                2. Supported domains: """);
        sb.append(String.join(", ", SUPPORTED_DOMAINS));
        sb.append("""
                .
                3. All quantities must use SI units (m, kg, s, m/s, m/s^2, etc.) or domain-specific units (e.g., "dimensionless", "rad", "deg").
                4. When unit information is missing, use "dimensionless" as the default unit.

                DOMAIN-SPECIFIC STRUCTURE:

                """);
        
        // Append all domain prompts in order
        for (String domain : SUPPORTED_DOMAINS) {
            sb.append(DOMAIN_PROMPTS.get(domain)).append("\n\n");
        }
        
        sb.append("""
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
                """);
        
        return sb.toString();
    }

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
        return "Translate this query into Model JSON:\n\n\"" + query + "\"\n\n"
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
            throw new UnsupportedDomainException(model.getDomain(), SUPPORTED_DOMAINS);
        }

        List<String> validationErrors = new ArrayList<>(schemaValidator.validate(node));
        if ("physics.mechanics".equals(model.getDomain())) {
            validatePhysicsParameters(model, validationErrors);
        }
        if (!validationErrors.isEmpty()) {
            throw new ModelValidationException(validationErrors);
        }

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

    private static class JsonParseUnusableException extends RuntimeException {
        JsonParseUnusableException(String message) {
            super(message);
        }
    }
}
