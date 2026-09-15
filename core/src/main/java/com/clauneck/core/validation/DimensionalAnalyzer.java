package com.clauneck.core.validation;

import com.clauneck.core.model.Equation;
import com.clauneck.core.model.Model;
import com.clauneck.core.model.Quantity;
import com.clauneck.core.units.Dimension;
import com.clauneck.core.units.UnitRegistry;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Validates model dimensional consistency.
 * Ensures all quantities have defined dimensions, all units parse correctly,
 * and (simplified) all equations are dimensionally balanced.
 */
public class DimensionalAnalyzer {
  private final UnitRegistry unitRegistry;

  public DimensionalAnalyzer(UnitRegistry unitRegistry) {
    this.unitRegistry = unitRegistry;
  }

  /**
   * Analyze and validate a model for dimensional consistency.
   * Returns a ValidationResult with any errors found.
   */
  public ValidationResult validate(Model model) {
    List<String> errors = new ArrayList<>();
    List<String> warnings = new ArrayList<>();

    // 1. Check all quantities have parseable units and dimensions
    for (Quantity q : model.getQuantities()) {
      Optional<Dimension> dim = unitRegistry.parseDimension(q.getSiUnit());
      if (dim.isEmpty()) {
        errors.add("Quantity '" + q.getName() + "': unparseable unit '" + q.getSiUnit() + "'");
      } else if (!dim.get().isConsistentWith(q.getDimension())) {
        errors.add("Quantity '" + q.getName() + "': unit '" + q.getSiUnit()
            + "' does not match its declared dimension");
      }
    }

    // 2. Check that initial conditions reference known quantities
    for (String quantityName : model.getInitialConditions().keySet()) {
      if (model.getQuantity(quantityName).isEmpty()) {
        errors.add("Initial condition for unknown quantity: " + quantityName);
      }
    }

    // 3. Basic consistency check for equation references
    // (Full symbolic dimensional checking is deferred to the Python engine)
    for (Equation eq : model.getEquations()) {
      if (eq.getLhs().isEmpty() || eq.getRhs().isEmpty()) {
        errors.add("Equation has empty lhs or rhs");
        continue;
      }

      Optional<Dimension> lhsDimension = resolveQuantityDimension(model, eq.getLhs());
      Optional<Dimension> rhsDimension = resolveQuantityDimension(model, eq.getRhs());
      if (lhsDimension.isPresent() && rhsDimension.isPresent()
          && !lhsDimension.get().isConsistentWith(rhsDimension.get())) {
        errors.add("Equation '" + eq.getLhs() + " = " + eq.getRhs()
            + "' has inconsistent dimensions");
      }
    }

    boolean isValid = errors.isEmpty();
    return new ValidationResult(isValid, errors, warnings);
  }

  private Optional<Dimension> resolveQuantityDimension(Model model, String term) {
    return model.getQuantity(term.trim())
        .flatMap(quantity -> unitRegistry.parseDimension(quantity.getSiUnit()));
  }

  public static class ValidationResult {
    private final boolean valid;
    private final List<String> errors;
    private final List<String> warnings;

    public ValidationResult(boolean valid, List<String> errors, List<String> warnings) {
      this.valid = valid;
      this.errors = new ArrayList<>(errors);
      this.warnings = new ArrayList<>(warnings);
    }

    public boolean isValid() { return valid; }
    public List<String> getErrors() { return new ArrayList<>(errors); }
    public List<String> getWarnings() { return new ArrayList<>(warnings); }

    @Override
    public String toString() {
      if (valid) return "ValidationResult: VALID";
      return String.format("ValidationResult: INVALID\n  Errors: %s\n  Warnings: %s",
          errors, warnings);
    }
  }
}
