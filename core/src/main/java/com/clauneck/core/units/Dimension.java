package com.clauneck.core.units;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Arrays;
import java.util.Objects;

/**
 * Fundamental dimension vector: [L, M, T, I, Θ, N, J]
 * Represents the dimensional exponents of a physical quantity.
 */
@JsonInclude(JsonInclude.Include.NON_DEFAULT)
public class Dimension {
  private static final int NUM_DIMENSIONS = 7;
  private final double[] exponents; // [length, mass, time, current, temperature, amount, luminous]

  private static final int LENGTH = 0;
  private static final int MASS = 1;
  private static final int TIME = 2;
  private static final int CURRENT = 3;
  private static final int TEMPERATURE = 4;
  private static final int AMOUNT = 5;
  private static final int LUMINOUS = 6;

  public static final Dimension DIMENSIONLESS = new Dimension(0, 0, 0, 0, 0, 0, 0);
  public static final Dimension LENGTH_DIMENSION = new Dimension(1, 0, 0, 0, 0, 0, 0);
  public static final Dimension MASS_DIMENSION = new Dimension(0, 1, 0, 0, 0, 0, 0);
  public static final Dimension TIME_DIMENSION = new Dimension(0, 0, 1, 0, 0, 0, 0);
  public static final Dimension CURRENT_DIMENSION = new Dimension(0, 0, 0, 1, 0, 0, 0);
  public static final Dimension TEMPERATURE_DIMENSION = new Dimension(0, 0, 0, 0, 1, 0, 0);
  public static final Dimension AMOUNT_DIMENSION = new Dimension(0, 0, 0, 0, 0, 1, 0);
  public static final Dimension LUMINOUS_DIMENSION = new Dimension(0, 0, 0, 0, 0, 0, 1);
  public static final Dimension VELOCITY = new Dimension(1, 0, -1, 0, 0, 0, 0); // L/T
  public static final Dimension ACCELERATION = new Dimension(1, 0, -2, 0, 0, 0, 0); // L/T²

  @JsonCreator
  public Dimension(
      @JsonProperty("length") double length,
      @JsonProperty("mass") double mass,
      @JsonProperty("time") double time,
      @JsonProperty("electricCurrent") double current,
      @JsonProperty("temperature") double temperature,
      @JsonProperty("amountOfSubstance") double amount,
      @JsonProperty("luminousIntensity") double luminous) {
    this.exponents = new double[] { length, mass, time, current, temperature, amount, luminous };
  }

  /**
   * Multiply two dimensions (add their exponents).
   */
  public Dimension multiply(Dimension other) {
    double[] result = new double[NUM_DIMENSIONS];
    for (int i = 0; i < NUM_DIMENSIONS; i++) {
      result[i] = this.exponents[i] + other.exponents[i];
    }
    return new Dimension(result[LENGTH], result[MASS], result[TIME], result[CURRENT],
        result[TEMPERATURE], result[AMOUNT], result[LUMINOUS]);
  }

  /**
   * Divide two dimensions (subtract their exponents).
   */
  public Dimension divide(Dimension other) {
    double[] result = new double[NUM_DIMENSIONS];
    for (int i = 0; i < NUM_DIMENSIONS; i++) {
      result[i] = this.exponents[i] - other.exponents[i];
    }
    return new Dimension(result[LENGTH], result[MASS], result[TIME], result[CURRENT],
        result[TEMPERATURE], result[AMOUNT], result[LUMINOUS]);
  }

  /**
   * Raise to a power (multiply exponents by power).
   */
  public Dimension power(double power) {
    double[] result = new double[NUM_DIMENSIONS];
    for (int i = 0; i < NUM_DIMENSIONS; i++) {
      result[i] = this.exponents[i] * power;
    }
    return new Dimension(result[LENGTH], result[MASS], result[TIME], result[CURRENT],
        result[TEMPERATURE], result[AMOUNT], result[LUMINOUS]);
  }

  /**
   * Check if this dimension is consistent with another (all exponents match with tolerance).
   */
  public boolean isConsistentWith(Dimension other) {
    for (int i = 0; i < NUM_DIMENSIONS; i++) {
      if (Math.abs(this.exponents[i] - other.exponents[i]) > 1e-10) {
        return false;
      }
    }
    return true;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    Dimension dimension = (Dimension) o;
    return Arrays.equals(exponents, dimension.exponents);
  }

  @Override
  public int hashCode() {
    return Arrays.hashCode(exponents);
  }

  @Override
  public String toString() {
    return String.format("Dimension[L=%.1f, M=%.1f, T=%.1f, I=%.1f, Θ=%.1f, N=%.1f, J=%.1f]",
        exponents[LENGTH], exponents[MASS], exponents[TIME], exponents[CURRENT],
        exponents[TEMPERATURE], exponents[AMOUNT], exponents[LUMINOUS]);
  }

  public double getLength() { return exponents[LENGTH]; }
  public double getMass() { return exponents[MASS]; }
  public double getTime() { return exponents[TIME]; }
  @JsonProperty("electricCurrent")
  public double getCurrent() { return exponents[CURRENT]; }
  public double getTemperature() { return exponents[TEMPERATURE]; }
  @JsonProperty("amountOfSubstance")
  public double getAmount() { return exponents[AMOUNT]; }
  @JsonProperty("luminousIntensity")
  public double getLuminous() { return exponents[LUMINOUS]; }
}
