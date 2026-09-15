package com.clauneck.web.client;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

import com.clauneck.web.config.EngineProperties;
import com.clauneck.web.dto.PrototypeResponse;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.dto.SolverResultDto;
import com.clauneck.web.exception.EngineException;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

@ExtendWith(MockitoExtension.class)
class EngineClientTest {

    @Mock
    private RestTemplate restTemplate;

    private EngineProperties properties;
    private EngineClient client;

    @BeforeEach
    void setUp() {
        properties = new EngineProperties();
        properties.setUrl("http://localhost:8001");
        client = new EngineClient(restTemplate, properties);
    }

    @Test
    void successfulSolveReturnsResult() {
        SolverResultDto result = new SolverResultDto();
        result.setSuccess(true);
        result.setMessage("Projectile motion solved successfully");
        result.setSummary(Map.of("max_range", 7.515369));

        PrototypeResponse engineResponse = new PrototypeResponse(new ScientificModelDto(), result, null);

        when(restTemplate.postForObject(eq("http://localhost:8001/api/solve"),
                any(ScientificModelDto.class), eq(PrototypeResponse.class)))
                .thenReturn(engineResponse);

        SolverResultDto actual = client.solve(new ScientificModelDto());

        assertEquals(true, actual.isSuccess());
        assertEquals(7.515369, actual.getSummary().get("max_range"));
    }

    @Test
    void engineFailureResultThrowsEngineException() {
        SolverResultDto result = new SolverResultDto();
        result.setSuccess(false);
        result.setMessage("Solver error");
        result.setError("division by zero");

        PrototypeResponse engineResponse = new PrototypeResponse(new ScientificModelDto(), result, null);

        when(restTemplate.postForObject(anyString(), any(ScientificModelDto.class), eq(PrototypeResponse.class)))
                .thenReturn(engineResponse);

        assertThrows(EngineException.class, () -> client.solve(new ScientificModelDto()));
    }

    @Test
    void connectionFailureThrowsEngineException() {
        when(restTemplate.postForObject(anyString(), any(ScientificModelDto.class), eq(PrototypeResponse.class)))
                .thenThrow(new ResourceAccessException("connection refused"));

        assertThrows(EngineException.class, () -> client.solve(new ScientificModelDto()));
    }
}
