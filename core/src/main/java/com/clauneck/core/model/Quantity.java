package com.clauneck.core.model;

import com.clauneck.core.units.Dimension;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * A quantity in a scientific model: a variable, constant, or unknown.
 */
public class Quantity {
  private final String name;
  private final Optional<Object> value;
  private final String siUnit;
  private final Dimension dimension;
  private final boolean isKnown;
  private final Optional<String> description;

  @JsonCreator
  public Quantity(
      @JsonProperty(value = "name", required = true) String name,
      @JsonProperty("value") Optional<Object> value,
      @JsonProperty(value = "siUnit", required = true) String siUnit,
      @JsonProperty("dimensionVector") Dimension dimension,
      @JsonProperty(value = "isKnown", required = true) boolean isKnown,
      @JsonProperty("description") Optional<String> description) {
    this.name = Objects.requireNonNull(name);
    this.value = value == null ? Optional.empty() : value;
    this.siUnit = Objects.requireNonNull(siUnit);
    this.dimension = dimension == null ? Dimension.DIMENSIONLESS : dimension;
    this.isKnown = isKnown;
    this.description = description == null ? Optional.empty() : description;
    if (isKnown != this.value.isPresent()) {
      throw new IllegalArgumentException("isKnown must be true exactly when value is present");
    }
  }

  public static Builder builder(String name) {
    return new Builder(name);
  }

  public static class Builder {
    private final String name;
    private Optional<Object> value = Optional.empty();
    private String siUnit = "dimensionless";
    private Dimension dimension = Dimension.DIMENSIONLESS;
    private boolean isKnown = false;
    private Optional<String> description = Optional.empty();

    public Builder(String name) {
      this.name = name;
    }

    public Builder value(double v) {
      this.value = Optional.of(v);
      this.isKnown = true;
      return this;
    }

    public Builder value(List<?> values) {
      this.value = Optional.of(List.copyOf(values));
      this.isKnown = true;
      return this;
    }

    public Builder siUnit(String unit) {
      this.siUnit = unit;
      return this;
    }

    public Builder dimension(Dimension d) {
      this.dimension = d;
      return this;
    }

    public Builder unknown() {
      this.value = Optional.empty();
      this.isKnown = false;
      return this;
    }

    public Builder description(String desc) {
      this.description = Optional.of(desc);
      return this;
    }

    public Quantity build() {
      return new Quantity(name, value, siUnit, dimension, isKnown, description);
    }
  }

  public String getName() { return name; }
  public Optional<Object> getValue() { return value; }
  public String getSiUnit() { return siUnit; }
  @JsonProperty("dimensionVector")
  public Dimension getDimension() { return dimension; }
  @JsonProperty("isKnown")
  public boolean isKnown() { return isKnown; }
  public Optional<String> getDescription() { return description; }

  @Override
  public String toString() {
    String valueStr = value.isPresent() ? String.valueOf(value.get()) : "unknown";
    return String.format("%s = %s %s", name, valueStr, siUnit);
  }
}
