package com.clauneck.web.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class TimeSpanDto {

    private double start;
    private double end;
    private Integer numPoints;

    public double getStart() {
        return start;
    }

    public void setStart(double start) {
        this.start = start;
    }

    public double getEnd() {
        return end;
    }

    public void setEnd(double end) {
        this.end = end;
    }

    public Integer getNumPoints() {
        return numPoints;
    }

    public void setNumPoints(Integer numPoints) {
        this.numPoints = numPoints;
    }
}
