package com.clauneck.web.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class DimensionVector {

    private double length;
    private double mass;
    private double time;
    private double electricCurrent;
    private double temperature;
    private double amountOfSubstance;
    private double luminousIntensity;

    public double getLength() {
        return length;
    }

    public void setLength(double length) {
        this.length = length;
    }

    public double getMass() {
        return mass;
    }

    public void setMass(double mass) {
        this.mass = mass;
    }

    public double getTime() {
        return time;
    }

    public void setTime(double time) {
        this.time = time;
    }

    public double getElectricCurrent() {
        return electricCurrent;
    }

    public void setElectricCurrent(double electricCurrent) {
        this.electricCurrent = electricCurrent;
    }

    public double getTemperature() {
        return temperature;
    }

    public void setTemperature(double temperature) {
        this.temperature = temperature;
    }

    public double getAmountOfSubstance() {
        return amountOfSubstance;
    }

    public void setAmountOfSubstance(double amountOfSubstance) {
        this.amountOfSubstance = amountOfSubstance;
    }

    public double getLuminousIntensity() {
        return luminousIntensity;
    }

    public void setLuminousIntensity(double luminousIntensity) {
        this.luminousIntensity = luminousIntensity;
    }
}
