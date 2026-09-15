package com.clauneck.core.units;

import static org.junit.Assert.*;
import org.junit.Test;

public class DimensionTest {

  @Test
  public void testDimensionless() {
    assertEquals(0.0, Dimension.DIMENSIONLESS.getLength(), 0.0);
    assertEquals(0.0, Dimension.DIMENSIONLESS.getMass(), 0.0);
    assertEquals(0.0, Dimension.DIMENSIONLESS.getTime(), 0.0);
  }

  @Test
  public void testVelocityDimension() {
    // m/s = L * T^-1
    Dimension velocity = Dimension.LENGTH_DIMENSION.divide(Dimension.TIME_DIMENSION);
    assertEquals(1.0, velocity.getLength(), 0.0);
    assertEquals(-1.0, velocity.getTime(), 0.0);
  }

  @Test
  public void testAccelerationDimension() {
    // m/s^2 = L * T^-2
    Dimension accel = Dimension.ACCELERATION;
    assertEquals(1.0, accel.getLength(), 0.0);
    assertEquals(-2.0, accel.getTime(), 0.0);
  }

  @Test
  public void testForceDimension() {
    // N = kg * m / s^2 = M * L * T^-2
    Dimension force = Dimension.MASS_DIMENSION
        .multiply(Dimension.ACCELERATION);
    assertEquals(1.0, force.getMass(), 0.0);
    assertEquals(1.0, force.getLength(), 0.0);
    assertEquals(-2.0, force.getTime(), 0.0);
  }

  @Test
  public void testMultiplication() {
    Dimension result = Dimension.LENGTH_DIMENSION.multiply(Dimension.MASS_DIMENSION);
    assertEquals(1.0, result.getLength(), 0.0);
    assertEquals(1.0, result.getMass(), 0.0);
  }

  @Test
  public void testDivision() {
    Dimension velocity = Dimension.LENGTH_DIMENSION.divide(Dimension.TIME_DIMENSION);
    assertEquals(1.0, velocity.getLength(), 0.0);
    assertEquals(-1.0, velocity.getTime(), 0.0);
  }

  @Test
  public void testPower() {
    Dimension areaPerTime = Dimension.LENGTH_DIMENSION.power(2)
        .divide(Dimension.TIME_DIMENSION);
    assertEquals(2.0, areaPerTime.getLength(), 0.0);
    assertEquals(-1.0, areaPerTime.getTime(), 0.0);
  }

  @Test
  public void testConsistency() {
    Dimension v1 = Dimension.LENGTH_DIMENSION.divide(Dimension.TIME_DIMENSION);
    Dimension v2 = Dimension.VELOCITY;
    assertTrue(v1.isConsistentWith(v2));
  }

  @Test
  public void testInconsistency() {
    assertFalse(Dimension.LENGTH_DIMENSION.isConsistentWith(Dimension.TIME_DIMENSION));
  }
}
