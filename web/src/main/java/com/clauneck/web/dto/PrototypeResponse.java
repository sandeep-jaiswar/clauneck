package com.clauneck.web.dto;

public class PrototypeResponse {

    private ScientificModelDto model;
    private SolverResultDto result;
    private String message;

    public PrototypeResponse() {
    }

    public PrototypeResponse(ScientificModelDto model, SolverResultDto result, String message) {
        this.model = model;
        this.result = result;
        this.message = message;
    }

    public ScientificModelDto getModel() {
        return model;
    }

    public void setModel(ScientificModelDto model) {
        this.model = model;
    }

    public SolverResultDto getResult() {
        return result;
    }

    public void setResult(SolverResultDto result) {
        this.result = result;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
