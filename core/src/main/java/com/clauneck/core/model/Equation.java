package com.clauneck.core.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonValue;
import java.util.Objects;
import java.util.Optional;

/**
 * A single equation or constraint in a model.
 */
public class Equation {
  public enum Type {
    ALGEBRAIC("algebraic"), ODE("ode"), PDE("pde"), CONSTRAINT("constraint");

    private final String schemaValue;

    Type(String schemaValue) {
      this.schemaValue = schemaValue;
    }

    @JsonValue
    public String getSchemaValue() {
      return schemaValue;
    }

    @JsonCreator
    public static Type fromSchemaValue(String value) {
      for (Type type : values()) {
        if (type.schemaValue.equals(value)) {
          return type;
        }
      }
      throw new IllegalArgumentException("Unknown equation type: " + value);
    }
  }

  private final String lhs; // left-hand side symbolic expression
  private final String rhs; // right-hand side symbolic expression
  private final Type type;
  private final Optional<String> description;

  @JsonCreator
  public Equation(
      @JsonProperty(value = "lhs", required = true) String lhs,
      @JsonProperty(value = "rhs", required = true) String rhs,
      @JsonProperty("type") Type type,
      @JsonProperty("description") Optional<String> description) {
    this.lhs = Objects.requireNonNull(lhs);
    this.rhs = Objects.requireNonNull(rhs);
    this.type = type == null ? Type.ALGEBRAIC : type;
    this.description = description == null ? Optional.empty() : description;
  }

  public static Builder builder() {
    return new Builder();
  }

  public static class Builder {
    private String lhs;
    private String rhs;
    private Type type = Type.ALGEBRAIC;
    private Optional<String> description = Optional.empty();

    public Builder lhs(String lhs) {
      this.lhs = lhs;
      return this;
    }

    public Builder rhs(String rhs) {
      this.rhs = rhs;
      return this;
    }

    public Builder type(Type t) {
      this.type = t;
      return this;
    }

    public Builder description(String desc) {
      this.description = Optional.of(desc);
      return this;
    }

    public Equation build() {
      Objects.requireNonNull(lhs, "lhs is required");
      Objects.requireNonNull(rhs, "rhs is required");
      return new Equation(lhs, rhs, type, description);
    }
  }

  public String getLhs() { return lhs; }
  public String getRhs() { return rhs; }
  public Type getType() { return type; }
  public Optional<String> getDescription() { return description; }

  @Override
  public String toString() {
    return String.format("%s = %s (%s)", lhs, rhs, type);
  }
}
