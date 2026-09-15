package com.clauneck.core.units;

import java.util.Objects;

/**
 * Represents a single SI unit with its dimensional analysis.
 * Stores the conversion factor to base SI units.
 */
public class Unit {
  private final String symbol;
  private final String name;
  private final Dimension dimension;
  private final double toSiBase; // conversion factor to base SI unit

  public Unit(String symbol, String name, Dimension dimension, double toSiBase) {
    this.symbol = Objects.requireNonNull(symbol);
    this.name = Objects.requireNonNull(name);
    this.dimension = Objects.requireNonNull(dimension);
    this.toSiBase = toSiBase;
  }

  /**
   * Standard SI base units.
   */
  public static final Unit METER = new Unit("m", "meter", Dimension.LENGTH_DIMENSION, 1.0);
  public static final Unit KILOGRAM = new Unit("kg", "kilogram", Dimension.MASS_DIMENSION, 1.0);
  public static final Unit SECOND = new Unit("s", "second", Dimension.TIME_DIMENSION, 1.0);
  public static final Unit AMPERE = new Unit("A", "ampere", Dimension.CURRENT_DIMENSION, 1.0);
  public static final Unit KELVIN = new Unit("K", "kelvin", Dimension.TEMPERATURE_DIMENSION, 1.0);
  public static final Unit MOLE = new Unit("mol", "mole", Dimension.AMOUNT_DIMENSION, 1.0);
  public static final Unit CANDELA = new Unit("cd", "candela", Dimension.LUMINOUS_DIMENSION, 1.0);

  /**
   * Common derived units.
   */
  public static final Unit DIMENSIONLESS = new Unit("dimensionless", "dimensionless",
      Dimension.DIMENSIONLESS, 1.0);
  public static final Unit RADIAN = new Unit("rad", "radian", Dimension.DIMENSIONLESS, 1.0);
  public static final Unit HERTZ = new Unit("Hz", "hertz", Dimension.TIME_DIMENSION.power(-1), 1.0);
  public static final Unit NEWTON = new Unit("N", "newton",
      Dimension.MASS_DIMENSION.multiply(Dimension.ACCELERATION), 1.0);
  public static final Unit PASCAL = new Unit("Pa", "pascal",
      new Dimension(-1, 1, -2, 0, 0, 0, 0), 1.0); // M/(L*T²)
  public static final Unit JOULE = new Unit("J", "joule",
      new Dimension(2, 1, -2, 0, 0, 0, 0), 1.0); // L²*M/T²

  public String getSymbol() { return symbol; }
  public String getName() { return name; }
  public Dimension getDimension() { return dimension; }
  public double getToSiBase() { return toSiBase; }

  @Override
  public boolean equals(Object o) {
    if (this == o) return true;
    if (o == null || getClass() != o.getClass()) return false;
    Unit unit = (Unit) o;
    return symbol.equals(unit.symbol) && dimension.equals(unit.dimension);
  }

  @Override
  public int hashCode() {
    return Objects.hash(symbol, dimension);
  }

  @Override
  public String toString() {
    return symbol;
  }
}
