package com.clauneck.core.validation;

import static org.junit.Assert.*;
import com.clauneck.core.model.Equation;
import com.clauneck.core.model.Model;
import com.clauneck.core.model.Quantity;
import com.clauneck.core.units.Dimension;
import com.clauneck.core.units.UnitRegistry;
import java.util.Optional;
import org.junit.Before;
import org.junit.Test;

public class DimensionalAnalyzerTest {

  private DimensionalAnalyzer analyzer;
  private UnitRegistry unitRegistry;

  @Before
  public void setUp() {
    unitRegistry = new UnitRegistry();
    analyzer = new DimensionalAnalyzer(unitRegistry);
  }

  @Test
  public void testValidModelWithCorrectUnits() {
    Model model = Model.builder("projectile", "physics.mechanics")
        .description("Simple projectile motion")
        .quantity(Quantity.builder("v0")
            .value(20)
            .siUnit("m/s")
            .dimension(Dimension.VELOCITY)
            .description("Initial velocity")
            .build())
        .quantity(Quantity.builder("mass")
            .value(0.5)
            .siUnit("kg")
            .dimension(Dimension.MASS_DIMENSION)
            .description("Mass of object")
            .build())
        .quantity(Quantity.builder("g")
            .value(9.81)
            .siUnit("m/s^2")
            .dimension(Dimension.ACCELERATION)
            .description("Gravitational acceleration")
            .build())
        .equation(Equation.builder()
            .lhs("d2x/dt2")
            .rhs("0")
            .type(Equation.Type.ODE)
            .description("Horizontal acceleration")
            .build())
        .initialCondition("v0", 20)
        .build();

    DimensionalAnalyzer.ValidationResult result = analyzer.validate(model);
    assertTrue("Model should be valid: " + result.getErrors(), result.isValid());
  }

  @Test
  public void testModelWithInvalidUnit() {
    Model model = Model.builder("bad", "physics.mechanics")
        .quantity(Quantity.builder("v")
            .value(10)
            .siUnit("invalid_unit_xyz")
            .dimension(Dimension.VELOCITY)
            .build())
        .build();

    DimensionalAnalyzer.ValidationResult result = analyzer.validate(model);
    assertFalse(result.isValid());
    assertTrue(result.getErrors().stream()
        .anyMatch(e -> e.contains("unparseable unit")));
  }

  @Test
  public void testModelWithUnknownInitialCondition() {
    Model model = Model.builder("bad", "physics.mechanics")
        .quantity(Quantity.builder("x")
            .siUnit("m")
            .dimension(Dimension.LENGTH_DIMENSION)
            .unknown()
            .build())
        .initialCondition("nonexistent_quantity", 100)
        .build();

    DimensionalAnalyzer.ValidationResult result = analyzer.validate(model);
    assertFalse(result.isValid());
    assertTrue(result.getErrors().stream()
        .anyMatch(e -> e.contains("unknown quantity")));
  }
}
