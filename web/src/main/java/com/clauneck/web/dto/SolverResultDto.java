package com.clauneck.web.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.List;
import java.util.Map;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class SolverResultDto {

    private boolean success;
    private String message;
    private Map<String, List<Double>> trajectory;
    private Map<String, Double> summary;
    private String error;

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public Map<String, List<Double>> getTrajectory() {
        return trajectory;
    }

    public void setTrajectory(Map<String, List<Double>> trajectory) {
        this.trajectory = trajectory;
    }

    public Map<String, Double> getSummary() {
        return summary;
    }

    public void setSummary(Map<String, Double> summary) {
        this.summary = summary;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}
