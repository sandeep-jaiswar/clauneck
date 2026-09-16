package com.clauneck.web.api;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.clauneck.web.client.EngineClient;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.dto.SolverResultDto;
import com.clauneck.web.exception.ClaudeUnavailableException;
import com.clauneck.web.exception.DimensionalMismatchException;
import com.clauneck.web.exception.EngineException;
import com.clauneck.web.exception.ModelValidationException;
import com.clauneck.web.exception.TranslationException;
import com.clauneck.web.exception.UnsupportedDomainException;
import com.clauneck.web.service.ClaudeTranslator;
import com.clauneck.web.service.DimensionalValidationService;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(PrototypeController.class)
class PrototypeControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private ClaudeTranslator translator;

    @MockBean
    private DimensionalValidationService dimensionalValidator;

    @MockBean
    private EngineClient engineClient;

    private String requestJson(String query) throws Exception {
        return objectMapper.writeValueAsString(Map.of("query", query));
    }

    @Test
    void validQueryReturns200WithModelAndResult() throws Exception {
        ScientificModelDto model = new ScientificModelDto();
        model.setId("projectile_001");
        model.setDomain("physics.mechanics");

        SolverResultDto result = new SolverResultDto();
        result.setSuccess(true);
        result.setMessage("Projectile motion solved successfully");
        result.setSummary(Map.of("max_range", 7.515369));

        when(translator.translate(anyString())).thenReturn(model);
        when(engineClient.solve(any(ScientificModelDto.class))).thenReturn(result);

        mockMvc.perform(post("/api/prototype")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestJson("Ball at 20 m/s, 45 degrees, mass 0.5kg, drag coefficient 0.1")))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.model.domain").value("physics.mechanics"))
                .andExpect(jsonPath("$.result.success").value(true))
                .andExpect(jsonPath("$.result.summary.max_range").value(7.515369));
    }

    @Test
    void dimensionalMismatchReturns400() throws Exception {
        ScientificModelDto model = new ScientificModelDto();
        model.setDomain("physics.mechanics");
        when(translator.translate(anyString())).thenReturn(model);
        doThrow(new DimensionalMismatchException(
                        List.of("Quantity 'x': unit 'seconds' does not match its declared dimension")))
                .when(dimensionalValidator).validate(any(ScientificModelDto.class));

        mockMvc.perform(post("/api/prototype")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestJson("Ball at 20 m/s")))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("DIMENSIONAL_MISMATCH"))
                .andExpect(jsonPath("$.message").value("Translated model has dimensional inconsistencies"));
    }

    @Test
    void emptyQueryReturns400() throws Exception {
        mockMvc.perform(post("/api/prototype")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestJson("")))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("TRANSLATION_FAILED"));
    }

    @Test
    void translationExceptionReturns400() throws Exception {
        when(translator.translate(anyString()))
                .thenThrow(new TranslationException("ambiguous input", "try being more specific"));

        mockMvc.perform(post("/api/prototype")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestJson("something vague")))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("TRANSLATION_FAILED"))
                .andExpect(jsonPath("$.suggestion").value("try being more specific"));
    }

    @Test
    void unsupportedDomainReturns501() throws Exception {
        Set<String> supportedDomains = Set.of(
                "mathematics.algebra", "mathematics.calculus", "mathematics.complex_numbers",
                "mathematics.geometry", "mathematics.linear_algebra", "mathematics.number_theory",
                "mathematics.ode", "mathematics.optimization", "mathematics.statistics",
                "mathematics.trigonometry", "physics.mechanics");
        when(translator.translate(anyString()))
                .thenThrow(new UnsupportedDomainException("chemistry.kinetics", supportedDomains));

        mockMvc.perform(post("/api/prototype")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestJson("reaction rate of X")))
                .andExpect(status().isNotImplemented())
                .andExpect(jsonPath("$.error").value("DOMAIN_NOT_SUPPORTED"));
    }

    @Test
    void modelValidationExceptionReturns400() throws Exception {
        when(translator.translate(anyString()))
                .thenThrow(new ModelValidationException(List.of("missing required field 'id'")));

        mockMvc.perform(post("/api/prototype")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestJson("Ball at 20 m/s")))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("VALIDATION_FAILED"));
    }

    @Test
    void claudeUnavailableReturns503() throws Exception {
        when(translator.translate(anyString()))
                .thenThrow(new ClaudeUnavailableException("timed out", new RuntimeException("boom")));

        mockMvc.perform(post("/api/prototype")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestJson("Ball at 20 m/s")))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.error").value("SERVICE_UNAVAILABLE"));
    }

    @Test
    void engineExceptionReturns502() throws Exception {
        ScientificModelDto model = new ScientificModelDto();
        model.setDomain("physics.mechanics");
        when(translator.translate(anyString())).thenReturn(model);
        when(engineClient.solve(any(ScientificModelDto.class)))
                .thenThrow(new EngineException("connection refused"));

        mockMvc.perform(post("/api/prototype")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestJson("Ball at 20 m/s")))
                .andExpect(status().isBadGateway())
                .andExpect(jsonPath("$.error").value("ENGINE_UNAVAILABLE"))
                .andExpect(jsonPath("$.details").value("The solver engine request failed"));
    }
}
