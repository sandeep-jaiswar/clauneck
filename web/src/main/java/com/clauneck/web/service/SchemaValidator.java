package com.clauneck.web.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import jakarta.annotation.PostConstruct;
import java.io.InputStream;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.springframework.stereotype.Service;

/**
 * Validates translated models against the shared schemas/model.schema.json
 * contract (draft-07), classpath-resolved via web/build.gradle's sourceSets
 * addition of ../schemas.
 */
@Service
public class SchemaValidator {

    private static final String SCHEMA_RESOURCE = "/model.schema.json";

    private final ObjectMapper objectMapper;
    private JsonSchema schema;

    public SchemaValidator(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    void loadSchema() {
        JsonSchemaFactory factory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
        try (InputStream in = getClass().getResourceAsStream(SCHEMA_RESOURCE)) {
            if (in == null) {
                throw new IllegalStateException(
                        "Could not find " + SCHEMA_RESOURCE + " on the classpath");
            }
            this.schema = factory.getSchema(in);
        } catch (Exception e) {
            throw new IllegalStateException("Failed to load model schema", e);
        }
    }

    /**
     * Returns a list of human-readable validation errors; empty if the model
     * is valid.
     */
    public List<String> validate(JsonNode modelNode) {
        Set<ValidationMessage> messages = schema.validate(modelNode);
        return messages.stream().map(ValidationMessage::getMessage).collect(Collectors.toList());
    }

    public List<String> validate(Object model) {
        return validate(objectMapper.valueToTree(model));
    }
}
