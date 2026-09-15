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
                {"name": "v0", "value": 20.0, "siUnit": "m/s", "isKnown": true},
                {"name": "angle", "value": 45.0, "siUnit": "deg", "isKnown": true},
                {"name": "mass", "value": 1.0, "siUnit": "kg", "isKnown": true},
                {"name": "g", "value": 9.81, "siUnit": "m/s^2", "isKnown": true},
                {"name": "drag_coeff", "value": 0.0, "siUnit": "dimensionless", "isKnown": true}
              ],
              "equations": [
                {"lhs": "d2x/dt2", "rhs": "-g", "type": "ode"}
              ],
              "initialConditions": {"v0": 20.0, "angle": 45.0, "mass": 1.0, "g": 9.81, "drag_coeff": 0.0},
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
    void statisticsModelAcceptsArrayValuesWithoutPhysicsValidation() {
        String statisticsModel = """
                {
                  "id": "statistics_001",
                  "domain": "mathematics.statistics",
                  "description": "Mean of a dataset",
                  "quantities": [
                    {"name": "data", "value": [1.0, 2.0, 3.0], "siUnit": "dimensionless", "isKnown": true}
                  ],
                  "equations": [
                    {"lhs": "result", "rhs": "mean(data)", "type": "algebraic"}
                  ],
                  "initialConditions": {},
                  "solver": {"method": "symbolic_solve", "tolerance": 1e-6},
                  "metadata": {"source": "manual"}
                }
                """;
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText(statisticsModel));

        ScientificModelDto model = translator.translate("Compute the mean of 1, 2, and 3");

        assertEquals("mathematics.statistics", model.getDomain());
        assertEquals(java.util.List.of(1.0, 2.0, 3.0), model.getQuantities().get(0).getValue());
    }

    @Test
    void unregisteredMathematicsDomainIsRejected() {
        String algebraModel = VALID_MODEL_JSON.replace("physics.mechanics", "mathematics.algebra");
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText(algebraModel));

        assertThrows(UnsupportedDomainException.class,
                () -> translator.translate("Solve an algebra equation"));
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
    void malformedJsonRetriesThenThrowsTranslationException() {
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText("this is not json at all"));

        assertThrows(TranslationException.class, () -> translator.translate("garbled query"));

        verify(restTemplate, times(properties.getMaxRetries()))
                .postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class));
    }

    @Test
    void nonObjectJsonRetriesThenThrowsTranslationException() {
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText("null"), responseWithText("[]"));

        assertThrows(TranslationException.class, () -> translator.translate("garbled query"));

        verify(restTemplate, times(properties.getMaxRetries()))
                .postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class));
    }

    @Test
    void initialConditionsTakePrecedenceDuringPhysicsValidation() {
        String invalidInitialVelocity = VALID_MODEL_JSON.replace(
                "\"v0\": 20.0, \"angle\"", "\"v0\": -1.0, \"angle\"");
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText(invalidInitialVelocity));

        ModelValidationException ex = assertThrows(ModelValidationException.class,
                () -> translator.translate("Ball at 20 m/s"));

        org.junit.jupiter.api.Assertions.assertTrue(
                ex.getValidationErrors().contains("v0 must be greater than 0"));
    }

    @Test
    void angleValidationConvertsDeclaredRadiansToDegrees() {
        String invalidRadianAngle = VALID_MODEL_JSON
                .replace("\"value\": 45.0, \"siUnit\": \"deg\"",
                        "\"value\": 2.0, \"siUnit\": \"rad\"")
                .replace("\"angle\": 45.0", "\"angle\": 2.0");
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(AnthropicResponse.class)))
                .thenReturn(responseWithText(invalidRadianAngle));

        ModelValidationException ex = assertThrows(ModelValidationException.class,
                () -> translator.translate("Ball launched at 2 radians"));

        org.junit.jupiter.api.Assertions.assertTrue(
                ex.getValidationErrors().contains("angle must be between 0 and 90 degrees"));
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
