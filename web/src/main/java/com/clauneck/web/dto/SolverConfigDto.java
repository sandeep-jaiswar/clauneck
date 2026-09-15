package com.clauneck.web.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * "method" is a raw String rather than an enum — schema/engine values
 * ("RK45","solve_ivp","odeint",...) don't map cleanly onto Java enum
 * constant naming, and the engine is the source of truth for what's valid.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class SolverConfigDto {

    private String method = "RK45";
    private double tolerance = 1e-6;
    private TimeSpanDto timeSpan;

    public String getMethod() {
        return method;
    }

    public void setMethod(String method) {
        this.method = method;
    }

    public double getTolerance() {
        return tolerance;
    }

    public void setTolerance(double tolerance) {
        this.tolerance = tolerance;
    }

    public TimeSpanDto getTimeSpan() {
        return timeSpan;
    }

    public void setTimeSpan(TimeSpanDto timeSpan) {
        this.timeSpan = timeSpan;
    }
}
