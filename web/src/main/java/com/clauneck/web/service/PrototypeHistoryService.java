package com.clauneck.web.service;

import com.clauneck.web.dto.PrototypeResponse;
import com.clauneck.web.entity.Prototype;
import com.clauneck.web.repository.PrototypeRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
public class PrototypeHistoryService {

    private static final Logger log = LoggerFactory.getLogger(PrototypeHistoryService.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final PrototypeRepository prototypeRepository;

    public PrototypeHistoryService(PrototypeRepository prototypeRepository) {
        this.prototypeRepository = prototypeRepository;
    }

    public void savePrototype(String query, PrototypeResponse response) {
        try {
            String modelJson = objectMapper.writeValueAsString(response.getModel());
            String resultJson = objectMapper.writeValueAsString(response.getResult());

            Prototype prototype = new Prototype(query, modelJson, resultJson);
            prototypeRepository.save(prototype);
            log.info("Prototype saved: id={}, query_length={}", prototype.getId(), query.length());
        } catch (Exception e) {
            log.warn("Failed to save prototype: {}", e.getMessage());
            // Don't fail the request if history save fails
        }
    }

    public Page<PrototypeHistory> getHistory(int page, int pageSize) {
        Pageable pageable = PageRequest.of(page, pageSize);
        return prototypeRepository.findAllByOrderByCreatedAtDesc(pageable)
                .map(this::toHistoryDto);
    }

    private PrototypeHistory toHistoryDto(Prototype prototype) {
        try {
            var model = objectMapper.readTree(prototype.getModelJson());
            var result = objectMapper.readTree(prototype.getResultJson());
            String domain = model.has("domain") ? model.get("domain").asText() : "unknown";
            boolean success = result.has("success") && result.get("success").asBoolean();
            return new PrototypeHistory(
                    prototype.getId(),
                    prototype.getQuery(),
                    domain,
                    success,
                    prototype.getCreatedAt()
            );
        } catch (Exception e) {
            log.warn("Failed to parse prototype {}: {}", prototype.getId(), e.getMessage());
            return new PrototypeHistory(
                    prototype.getId(),
                    prototype.getQuery(),
                    "unknown",
                    false,
                    prototype.getCreatedAt()
            );
        }
    }

    public static class PrototypeHistory {
        public Long id;
        public String query;
        public String domain;
        public boolean success;
        public String createdAt;

        public PrototypeHistory(Long id, String query, String domain, boolean success, java.time.LocalDateTime createdAt) {
            this.id = id;
            this.query = query;
            this.domain = domain;
            this.success = success;
            this.createdAt = createdAt.toString();
        }
    }
}
