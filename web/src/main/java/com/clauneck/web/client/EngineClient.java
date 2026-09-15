package com.clauneck.web.client;

import com.clauneck.web.config.EngineProperties;
import com.clauneck.web.dto.PrototypeResponse;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.dto.SolverResultDto;
import com.clauneck.web.exception.EngineException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

/** Calls the Python engine's POST /api/solve with a validated model, per spec.md Decision 3. */
@Service
public class EngineClient {

    private static final Logger log = LoggerFactory.getLogger(EngineClient.class);

    private final RestTemplate restTemplate;
    private final EngineProperties properties;

    public EngineClient(@Qualifier("engineRestTemplate") RestTemplate restTemplate,
                        EngineProperties properties) {
        this.restTemplate = restTemplate;
        this.properties = properties;
    }

    public SolverResultDto solve(ScientificModelDto model) {
        String url = properties.getUrl() + "/api/solve";
        try {
            // The engine's response envelope is {"model": ..., "result": ...}, which is a
            // subset of PrototypeResponse's fields (no "message"), so it deserializes cleanly.
            PrototypeResponse response = restTemplate.postForObject(url, model, PrototypeResponse.class);
            if (response == null || response.getResult() == null) {
                throw new EngineException("Engine returned an empty response");
            }
            SolverResultDto result = response.getResult();
            if (!result.isSuccess()) {
                throw new EngineException("Engine reported failure: " + result.getMessage()
                        + (result.getError() != null ? " (" + result.getError() + ")" : ""));
            }
            return result;
        } catch (ResourceAccessException e) {
            log.error("Engine unreachable at {}", url, e);
            throw new EngineException("Could not reach the solver engine at " + url, e);
        } catch (HttpStatusCodeException e) {
            log.error("Engine returned HTTP {} for {}", e.getStatusCode(), url);
            throw new EngineException("Engine returned HTTP " + e.getStatusCode() + ": " + e.getResponseBodyAsString(), e);
        }
    }
}
