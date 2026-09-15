package com.clauneck.core.units;

import static org.junit.Assert.*;
import java.util.Optional;
import org.junit.Before;
import org.junit.Test;

public class UnitRegistryTest {

  private UnitRegistry registry;

  @Before
  public void setUp() {
    registry = new UnitRegistry();
  }

  @Test
  public void testParseSimpleUnit() {
    Optional<Dimension> dim = registry.parseDimension("m");
    assertTrue(dim.isPresent());
    assertEquals(1.0, dim.get().getLength(), 0.0);
  }

  @Test
  public void testParseDerivedUnit() {
    Optional<Dimension> dim = registry.parseDimension("m/s");
    assertTrue(dim.isPresent());
    assertEquals(1.0, dim.get().getLength(), 0.0);
    assertEquals(-1.0, dim.get().getTime(), 0.0);
  }

  @Test
  public void testParseComplexUnit() {
    Optional<Dimension> dim = registry.parseDimension("kg*m/s^2");
    assertTrue(dim.isPresent());
    assertEquals(1.0, dim.get().getMass(), 0.0);
    assertEquals(1.0, dim.get().getLength(), 0.0);
    assertEquals(-2.0, dim.get().getTime(), 0.0);
  }

  @Test
  public void testParseDimensionless() {
    Optional<Dimension> dim = registry.parseDimension("dimensionless");
    assertTrue(dim.isPresent());
    assertEquals(0.0, dim.get().getLength(), 0.0);
    assertEquals(0.0, dim.get().getMass(), 0.0);
  }

  @Test
  public void testParseInvalidUnit() {
    Optional<Dimension> dim = registry.parseDimension("invalid_unit");
    assertFalse(dim.isPresent());
  }

  @Test
  public void testGetRegisteredUnit() {
    Optional<Unit> unit = registry.getUnit("m");
    assertTrue(unit.isPresent());
    assertEquals("m", unit.get().getSymbol());
    assertEquals("meter", unit.get().getName());
  }

  @Test
  public void testRegisterCustomUnit() {
    Dimension customDim = Dimension.LENGTH_DIMENSION;
    Unit customUnit = new Unit("cm", "centimeter", customDim, 0.01);
    registry.registerUnit(customUnit);

    Optional<Unit> retrieved = registry.getUnit("cm");
    assertTrue(retrieved.isPresent());
    assertEquals("cm", retrieved.get().getSymbol());
  }
}
