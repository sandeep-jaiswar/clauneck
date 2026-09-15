package com.clauneck.core.model;

import java.util.Objects;
import java.util.Optional;

/**
 * Configuration for the numerical solver.
 */
public class SolverConfig {
  public enum Method { RK45, RK23, DOP853, SOLVE_IVP, ODEINT, SYMBOLIC_SOLVE, FSOLVE }

  private final Method method;
  private final double tolerance;
  private final int maxSteps;
  private final Optional<TimeSpan> timeSpan;

  public static final SolverConfig DEFAULT = new SolverConfig(
      Method.RK45, 1e-6, 10000, Optional.empty());

  public SolverConfig(Method method, double tolerance, int maxSteps, Optional<TimeSpan> timeSpan) {
    this.method = Objects.requireNonNull(method);
    this.tolerance = tolerance;
    this.maxSteps = maxSteps;
    this.timeSpan = Objects.requireNonNull(timeSpan);
  }

  public static Builder builder() {
    return new Builder();
  }

  public static class Builder {
    private Method method = Method.RK45;
    private double tolerance = 1e-6;
    private int maxSteps = 10000;
    private Optional<TimeSpan> timeSpan = Optional.empty();

    public Builder method(Method m) {
      this.method = m;
      return this;
    }

    public Builder tolerance(double tol) {
      this.tolerance = tol;
      return this;
    }

    public Builder maxSteps(int steps) {
      this.maxSteps = steps;
      return this;
    }

    public Builder timeSpan(TimeSpan span) {
      this.timeSpan = Optional.of(span);
      return this;
    }

    public SolverConfig build() {
      return new SolverConfig(method, tolerance, maxSteps, timeSpan);
    }
  }

  public Method getMethod() { return method; }
  public double getTolerance() { return tolerance; }
  public int getMaxSteps() { return maxSteps; }
  public Optional<TimeSpan> getTimeSpan() { return timeSpan; }

  public static class TimeSpan {
    private final double start;
    private final double end;
    private final Optional<Integer> numPoints;

    public TimeSpan(double start, double end, Optional<Integer> numPoints) {
      this.start = start;
      this.end = end;
      this.numPoints = Objects.requireNonNull(numPoints);
    }

    public double getStart() { return start; }
    public double getEnd() { return end; }
    public Optional<Integer> getNumPoints() { return numPoints; }
  }
}
