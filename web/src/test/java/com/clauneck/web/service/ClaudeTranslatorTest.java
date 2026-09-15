package com.clauneck.web.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.clauneck.web.config.TranslatorProperties;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.exception.ClaudeUnavailableException;
import com.clauneck.web.exception.ModelValidationException;
import com.clauneck.web.exception.TranslationException;
import com.clauneck.web.exception.UnsupportedDomainException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpEntity;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

@ExtendWith(MockitoExtension.class)
class ClaudeTranslatorTest {

    private static final String VALID_MODEL_JSON = """
            {
              "id": "projectile_001",
              "domain": "physics.mechanics",
              "description": "Ball at 20 m/s, 45 degrees",
              "quantities": [
                {"name": "v0", "value": 20.0, "siUnit": "m/s", "isKnown": true}
              ],
              "equations": [
                {"lhs": "d2x/dt2", "rhs": "-g", "type": "ode"}
              ],
              "initialConditions": {"v0": 20.0},
              "solver": {"method": "RK45", "tolerance": 1e-6, "timeSpan": {"start": 0.0, "end": 5.0, "numPoints": 5000}},
              "metadata": {"source": "manual", "originalQuery": "placeholder"}
            }
            """;

    @Mock
    private RestTemplate restTemplate;

    private TranslatorProperties properties;
    private ClaudeTranslator translator;

    @BeforeEach
    void setUp() {
        properties = new TranslatorProperties();
        properties.setApiKey("test-key");
        properties.setModel("claude-haiku-4-5");
        properties.setMaxRetries(2);
        properties.setMaxTokens(2048);
        properties.setApiUrl("https://api.anthropic.com/v1/messages");
        properties.setAnthropicVersion("2023-06-01");

        ObjectMapper objectMapper = new ObjectMapper();
        SchemaValidator schemaValidator = new SchemaValidator(objectMapper);
        schemaValidator.loadSchema();

        translator = new ClaudeTranslator(restTemplate, objectMapper, schemaValidator, properties);
    }

    private AnthropicResponse responseWithText(String text) {
        AnthropicResponse response = new AnthropicResponse();
        AnthropicResponse.ContentBlock block = new AnthropicResponse.ContentBlock();
        block.setType("text");
        block.setText(text);
        response.setContent(java.util.List.of(block));
        return response;
    }

    @Test
    void validQueryReturnsModel() {
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText(VALID_MODEL_JSON));

        ScientificModelDto model = translator.translate("Ball at 20 m/s, 45 degrees");

        assertEquals("physics.mechanics", model.getDomain());
        assertEquals("llm_translator", model.getMetadata().getSource());
        assertEquals("Ball at 20 m/s, 45 degrees", model.getMetadata().getOriginalQuery());
    }

    @Test
    void claudeDeclineResponseThrowsTranslationException() {
        String decline = """
                {"error": true, "reason": "Query is about chemistry", "suggestion": "Ask about projectile motion"}
                """;
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText(decline));

        TranslationException ex = assertThrows(TranslationException.class,
                () -> translator.translate("Tell me about chemistry"));
        assertEquals("Query is about chemistry", ex.getMessage());
        assertEquals("Ask about projectile motion", ex.getSuggestion());
    }

    @Test
    void malformedJsonRetriesThenThrowsClaudeUnavailable() {
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText("this is not json at all"));

        assertThrows(ClaudeUnavailableException.class, () -> translator.translate("garbled query"));

        verify(restTemplate, times(properties.getMaxRetries()))
                .postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class));
    }

    @Test
    void unsupportedDomainThrowsUnsupportedDomainException() {
        String chemistryModel = VALID_MODEL_JSON.replace("physics.mechanics", "chemistry.kinetics");
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText(chemistryModel));

        assertThrows(UnsupportedDomainException.class,
                () -> translator.translate("Reaction rate of X"));
    }

    @Test
    void schemaInvalidModelThrowsModelValidationException() {
        String missingId = VALID_MODEL_JSON.replace("\"id\": \"projectile_001\",", "");
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText(missingId));

        assertThrows(ModelValidationException.class,
                () -> translator.translate("Ball at 20 m/s"));
    }

    @Test
    void transientHttpFailureRetriesThenThrowsClaudeUnavailable() {
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenThrow(new ResourceAccessException("connection timed out"));

        assertThrows(ClaudeUnavailableException.class, () -> translator.translate("Ball at 20 m/s"));

        verify(restTemplate, times(properties.getMaxRetries()))
                .postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class));
    }
}
