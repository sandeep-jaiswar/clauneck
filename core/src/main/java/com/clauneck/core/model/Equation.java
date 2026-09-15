package com.clauneck.core.model;

import java.util.Objects;
import java.util.Optional;

/**
 * A single equation or constraint in a model.
 */
public class Equation {
  public enum Type { ALGEBRAIC, ODE, PDE, CONSTRAINT }

  private final String lhs; // left-hand side symbolic expression
  private final String rhs; // right-hand side symbolic expression
  private final Type type;
  private final Optional<String> description;

  public Equation(String lhs, String rhs, Type type, Optional<String> description) {
    this.lhs = Objects.requireNonNull(lhs);
    this.rhs = Objects.requireNonNull(rhs);
    this.type = Objects.requireNonNull(type);
    this.description = Objects.requireNonNull(description);
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
