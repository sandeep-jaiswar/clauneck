package com.clauneck.web.api;

import com.clauneck.web.client.EngineClient;
import com.clauneck.web.dto.PrototypeRequest;
import com.clauneck.web.dto.PrototypeResponse;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.dto.SolverResultDto;
import com.clauneck.web.exception.TranslationException;
import com.clauneck.web.service.ClaudeTranslator;
import com.clauneck.web.service.DimensionalValidationService;
import com.clauneck.web.service.PrototypeHistoryService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/** Orchestrates translator -> validator -> engine per spec.md's high-level flow (FR1, FR4). */
@RestController
@RequestMapping("/api/prototype")
public class PrototypeController {

    private static final Logger log = LoggerFactory.getLogger(PrototypeController.class);
    private static final int MAX_QUERY_LENGTH = 1000;

    private final ClaudeTranslator translator;
    private final DimensionalValidationService dimensionalValidator;
    private final EngineClient engineClient;
    private final PrototypeHistoryService historyService;

    public PrototypeController(ClaudeTranslator translator,
            DimensionalValidationService dimensionalValidator,
            EngineClient engineClient,
            PrototypeHistoryService historyService) {
        this.translator = translator;
        this.dimensionalValidator = dimensionalValidator;
        this.engineClient = engineClient;
        this.historyService = historyService;
    }

    @PostMapping
    public ResponseEntity<PrototypeResponse> prototype(@RequestBody PrototypeRequest request) {
        String query = validateQuery(request);
        log.info("Received prototype query ({} chars)", query.length());

        ScientificModelDto model = translator.translate(query);
        log.info("Validating dimensional consistency for domain: {}", model.getDomain());
        dimensionalValidator.validate(model);

        SolverResultDto result = engineClient.solve(model);

        PrototypeResponse response = new PrototypeResponse(model, result, "OK");

        // Save to history if solver succeeded
        if (result.isSuccess()) {
            historyService.savePrototype(query, response);
        }

        return ResponseEntity.ok(response);
    }

    @GetMapping("/history")
    public ResponseEntity<Page<PrototypeHistoryService.PrototypeHistory>> getHistory(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int pageSize) {
        return ResponseEntity.ok(historyService.getHistory(page, pageSize));
    }

    private String validateQuery(PrototypeRequest request) {
        String query = request == null ? null : request.getQuery();
        if (query == null || query.isBlank()) {
            throw new TranslationException("Query must not be empty",
                    "Provide a natural language physics query, e.g. 'Ball at 10 m/s, 30 degrees, 1 kg mass'");
        }
        if (query.length() > MAX_QUERY_LENGTH) {
            throw new TranslationException(
                    "Query exceeds " + MAX_QUERY_LENGTH + " characters",
                    "Shorten the query to a single, focused physics scenario");
        }
        return query;
    }
}
