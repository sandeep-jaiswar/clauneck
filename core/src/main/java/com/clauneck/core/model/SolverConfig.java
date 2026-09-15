package com.clauneck.core.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonValue;
import java.util.Objects;
import java.util.Optional;

/**
 * Configuration for the numerical solver.
 */
public class SolverConfig {
  public enum Method {
    RK45("RK45"),
    RK23("RK23"),
    DOP853("DOP853"),
    SOLVE_IVP("solve_ivp"),
    ODEINT("odeint"),
    SYMBOLIC_SOLVE("symbolic_solve"),
    FSOLVE("fsolve");

    private final String schemaValue;

    Method(String schemaValue) {
      this.schemaValue = schemaValue;
    }

    @JsonValue
    public String getSchemaValue() {
      return schemaValue;
    }

    @JsonCreator
    public static Method fromSchemaValue(String value) {
      for (Method method : values()) {
        if (method.schemaValue.equals(value)) {
          return method;
        }
      }
      throw new IllegalArgumentException("Unknown solver method: " + value);
    }
  }

  private final Method method;
  private final double tolerance;
  private final TimeSpan timeSpan;

  @JsonCreator
  public SolverConfig(
      @JsonProperty(value = "method", required = true) Method method,
      @JsonProperty(value = "tolerance", required = true) double tolerance,
      @JsonProperty(value = "timeSpan", required = true) TimeSpan timeSpan) {
    this.method = Objects.requireNonNull(method);
    this.tolerance = tolerance;
    this.timeSpan = Objects.requireNonNull(timeSpan);
  }

  public static Builder builder() {
    return new Builder();
  }

  public static class Builder {
    private Method method;
    private Double tolerance;
    private TimeSpan timeSpan;

    public Builder method(Method m) {
      this.method = m;
      return this;
    }

    public Builder tolerance(double tol) {
      this.tolerance = tol;
      return this;
    }

    public Builder timeSpan(TimeSpan span) {
      this.timeSpan = span;
      return this;
    }

    public SolverConfig build() {
      Objects.requireNonNull(method, "method is required");
      Objects.requireNonNull(tolerance, "tolerance is required");
      Objects.requireNonNull(timeSpan, "timeSpan is required");
      return new SolverConfig(method, tolerance, timeSpan);
    }
  }

  public Method getMethod() { return method; }
  public double getTolerance() { return tolerance; }
  public TimeSpan getTimeSpan() { return timeSpan; }

  @JsonInclude(JsonInclude.Include.NON_ABSENT)
  public static class TimeSpan {
    private final double start;
    private final double end;
    private final Optional<Integer> numPoints;

    @JsonCreator
    public TimeSpan(
        @JsonProperty(value = "start", required = true) double start,
        @JsonProperty(value = "end", required = true) double end,
        @JsonProperty("numPoints") Optional<Integer> numPoints) {
      this.start = start;
      this.end = end;
      this.numPoints = numPoints == null ? Optional.empty() : numPoints;
    }

    public double getStart() { return start; }
    public double getEnd() { return end; }
    public Optional<Integer> getNumPoints() { return numPoints; }
  }
}
