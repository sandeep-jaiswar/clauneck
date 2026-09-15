package com.clauneck.core.units;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Global registry of known units for dimension analysis.
 * Parses unit strings (e.g., "m/s", "kg", "rad") and maps them to Dimension objects.
 */
public class UnitRegistry {
  private final Map<String, Unit> units = new HashMap<>();

  public UnitRegistry() {
    registerBaseUnits();
    registerDerivedUnits();
  }

  private void registerBaseUnits() {
    units.put("m", Unit.METER);
    units.put("kg", Unit.KILOGRAM);
    units.put("s", Unit.SECOND);
    units.put("A", Unit.AMPERE);
    units.put("K", Unit.KELVIN);
    units.put("mol", Unit.MOLE);
    units.put("cd", Unit.CANDELA);
    units.put("dimensionless", Unit.DIMENSIONLESS);
  }

  private void registerDerivedUnits() {
    units.put("rad", Unit.RADIAN);
    units.put("Hz", Unit.HERTZ);
    units.put("N", Unit.NEWTON);
    units.put("Pa", Unit.PASCAL);
    units.put("J", Unit.JOULE);
  }

  /**
   * Parse a unit string like "m/s", "kg*m/s^2", etc.
   * Simple parser: assumes format "unit1 * unit2 / unit3^2"
   */
  public Optional<Dimension> parseDimension(String unitString) {
    if (unitString == null || unitString.isEmpty()) {
      return Optional.empty();
    }

    if ("dimensionless".equals(unitString)) {
      return Optional.of(Dimension.DIMENSIONLESS);
    }

    try {
      // Simple tokenizer: split on / and *
      String[] parts = unitString.split("/");
      Dimension result = Dimension.DIMENSIONLESS;

      // Numerator
      if (parts.length > 0) {
        String[] numeratorTerms = parts[0].split("\\*");
        for (String term : numeratorTerms) {
          Dimension d = parseSingleTerm(term.trim());
          result = result.multiply(d);
        }
      }

      // Denominator
      if (parts.length > 1) {
        for (int i = 1; i < parts.length; i++) {
          String[] denominatorTerms = parts[i].split("\\*");
          for (String term : denominatorTerms) {
            Dimension d = parseSingleTerm(term.trim());
            result = result.divide(d);
          }
        }
      }

      return Optional.of(result);
    } catch (Exception e) {
      return Optional.empty();
    }
  }

  /**
   * Parse a single term like "m", "s^2", "kg".
   */
  private Dimension parseSingleTerm(String term) throws IllegalArgumentException {
    if (term.isEmpty()) {
      return Dimension.DIMENSIONLESS;
    }

    // Handle exponents like "s^2"
    int caretIndex = term.indexOf('^');
    String unitName;
    double power = 1.0;

    if (caretIndex > 0) {
      unitName = term.substring(0, caretIndex);
      power = Double.parseDouble(term.substring(caretIndex + 1));
    } else {
      unitName = term;
    }

    Unit unit = units.get(unitName);
    if (unit == null) {
      throw new IllegalArgumentException("Unknown unit: " + unitName);
    }

    return unit.getDimension().power(power);
  }

  public Optional<Unit> getUnit(String symbol) {
    return Optional.ofNullable(units.get(symbol));
  }

  public void registerUnit(Unit unit) {
    units.put(unit.getSymbol(), unit);
  }
}
