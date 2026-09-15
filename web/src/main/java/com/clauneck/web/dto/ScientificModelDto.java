package com.clauneck.web.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Mirrors engine/app/model.py's ScientificModel field-for-field, since that
 * Pydantic model — not the literal schemas/model.schema.json text — is the
 * actual accepted contract of the running engine's POST /api/solve.
 *
 * Known drift (documented, not fixed here — see build-plan.md): schema.json
 * declares initialConditions as a nested {time, values: {...}} object, but
 * engine/app/model.py declares it as a flat Dict[str, float], which is what
 * the engine actually parses. This DTO follows the engine (flat map), since
 * fixing the schema/engine mismatch is out of scope for this change (both
 * schemas/ and engine/ are "no changes" per spec.md).
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ScientificModelDto {

    private String id;
    private String domain;
    private String description;
    private List<Quantity> quantities = new ArrayList<>();
    private List<EquationDto> equations = new ArrayList<>();
    private Map<String, Double> initialConditions = new LinkedHashMap<>();
    private List<Map<String, Object>> boundaryConditions = new ArrayList<>();
    private SolverConfigDto solver = new SolverConfigDto();
    private MetadataDto metadata = new MetadataDto();

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getDomain() {
        return domain;
    }

    public void setDomain(String domain) {
        this.domain = domain;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public List<Quantity> getQuantities() {
        return quantities;
    }

    public void setQuantities(List<Quantity> quantities) {
        this.quantities = quantities;
    }

    public List<EquationDto> getEquations() {
        return equations;
    }

    public void setEquations(List<EquationDto> equations) {
        this.equations = equations;
    }

    public Map<String, Double> getInitialConditions() {
        return initialConditions;
    }

    public void setInitialConditions(Map<String, Double> initialConditions) {
        this.initialConditions = initialConditions;
    }

    public List<Map<String, Object>> getBoundaryConditions() {
        return boundaryConditions;
    }

    public void setBoundaryConditions(List<Map<String, Object>> boundaryConditions) {
        this.boundaryConditions = boundaryConditions;
    }

    public SolverConfigDto getSolver() {
        return solver;
    }

    public void setSolver(SolverConfigDto solver) {
        this.solver = solver;
    }

    public MetadataDto getMetadata() {
        return metadata;
    }

    public void setMetadata(MetadataDto metadata) {
        this.metadata = metadata;
    }
}
