package com.clauneck.core.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * Complete representation of a scientific model.
 * Immutable after construction; built via Builder.
 */
@JsonInclude(JsonInclude.Include.NON_ABSENT)
public class Model {
  private final String id;
  private final String domain;
  private final Optional<String> description;
  private final List<Quantity> quantities;
  private final List<Equation> equations;
  private final Map<String, Double> initialConditions;
  private final SolverConfig solverConfig;
  private final ModelMetadata metadata;

  private Model(
      String id, String domain, Optional<String> description,
      List<Quantity> quantities, List<Equation> equations,
      Map<String, Double> initialConditions, SolverConfig solverConfig,
      ModelMetadata metadata) {
    this.id = Objects.requireNonNull(id);
    this.domain = Objects.requireNonNull(domain);
    this.description = description == null ? Optional.empty() : description;
    this.quantities = new ArrayList<>(Objects.requireNonNull(quantities));
    this.equations = new ArrayList<>(Objects.requireNonNull(equations));
    this.initialConditions = initialConditions == null
        ? new HashMap<>() : new HashMap<>(initialConditions);
    this.solverConfig = Objects.requireNonNull(solverConfig);
    this.metadata = metadata == null ? new ModelMetadata() : metadata;
  }

  @JsonCreator
  private static Model fromJson(
      @JsonProperty(value = "id", required = true) String id,
      @JsonProperty(value = "domain", required = true) String domain,
      @JsonProperty("description") Optional<String> description,
      @JsonProperty(value = "quantities", required = true) List<Quantity> quantities,
      @JsonProperty(value = "equations", required = true) List<Equation> equations,
      @JsonProperty("initialConditions") InitialConditionsPayload initialConditions,
      @JsonProperty(value = "solver", required = true) SolverConfig solverConfig,
      @JsonProperty("metadata") ModelMetadata metadata) {
    Map<String, Double> values = initialConditions == null
        ? new HashMap<>() : initialConditions.getValues();
    return new Model(id, domain, description, quantities, equations,
        values, solverConfig, metadata);
  }

  public static Builder builder(String id, String domain) {
    return new Builder(id, domain);
  }

  public static class Builder {
    private final String id;
    private final String domain;
    private Optional<String> description = Optional.empty();
    private final List<Quantity> quantities = new ArrayList<>();
    private final List<Equation> equations = new ArrayList<>();
    private final Map<String, Double> initialConditions = new HashMap<>();
    private SolverConfig solverConfig;
    private ModelMetadata metadata = new ModelMetadata();

    public Builder(String id, String domain) {
      this.id = id;
      this.domain = domain;
    }

    public Builder description(String desc) {
      this.description = Optional.of(desc);
      return this;
    }

    public Builder quantity(Quantity q) {
      this.quantities.add(q);
      return this;
    }

    public Builder equation(Equation eq) {
      this.equations.add(eq);
      return this;
    }

    public Builder initialCondition(String quantityName, double value) {
      this.initialConditions.put(quantityName, value);
      return this;
    }

    public Builder solverConfig(SolverConfig config) {
      this.solverConfig = config;
      return this;
    }

    public Model build() {
      Objects.requireNonNull(solverConfig, "solverConfig is required");
      return new Model(id, domain, description, quantities, equations,
          initialConditions, solverConfig, metadata);
    }
  }

  public String getId() { return id; }
  public String getDomain() { return domain; }
  public Optional<String> getDescription() { return description; }
  public List<Quantity> getQuantities() { return new ArrayList<>(quantities); }
  public List<Equation> getEquations() { return new ArrayList<>(equations); }
  @JsonIgnore
  public Map<String, Double> getInitialConditions() { return new HashMap<>(initialConditions); }
  @JsonProperty("initialConditions")
  public InitialConditionsPayload getInitialConditionsPayload() {
    return new InitialConditionsPayload(Optional.empty(), initialConditions);
  }
  @JsonProperty("solver")
  public SolverConfig getSolverConfig() { return solverConfig; }
  public ModelMetadata getMetadata() { return metadata; }

  /**
   * Look up a quantity by name.
   */
  public Optional<Quantity> getQuantity(String name) {
    return quantities.stream()
        .filter(q -> q.getName().equals(name))
        .findFirst();
  }

  /**
   * Schema representation for ODE initial conditions.
   */
  @JsonInclude(JsonInclude.Include.NON_ABSENT)
  public static class InitialConditionsPayload {
    private final Optional<Double> time;
    private final Map<String, Double> values;

    @JsonCreator
    public InitialConditionsPayload(
        @JsonProperty("time") Optional<Double> time,
        @JsonProperty("values") Map<String, Double> values) {
      this.time = time == null ? Optional.empty() : time;
      this.values = values == null ? new HashMap<>() : new HashMap<>(values);
    }

    public Optional<Double> getTime() { return time; }
    public Map<String, Double> getValues() { return new HashMap<>(values); }
  }

  @Override
  public String toString() {
    return String.format("Model[id=%s, domain=%s, %d quantities, %d equations]",
        id, domain, quantities.size(), equations.size());
  }

  /**
   * Metadata for audit trail.
   */
  @JsonInclude(JsonInclude.Include.NON_ABSENT)
  public static class ModelMetadata {
    private Instant createdAt = Instant.now();
    private String source = "manual"; // or "llm_translator"
    private Optional<String> originalQuery = Optional.empty();
    private List<String> validationErrors = new ArrayList<>();

    public Instant getCreatedAt() { return createdAt; }
    public String getSource() { return source; }
    public Optional<String> getOriginalQuery() { return originalQuery; }
    public List<String> getValidationErrors() { return validationErrors; }

    public void setSource(String source) { this.source = source; }
    public void setOriginalQuery(String query) { this.originalQuery = Optional.ofNullable(query); }
    public void addValidationError(String error) { this.validationErrors.add(error); }
  }
}
