package com.clauneck.web.dto;

import java.util.Map;

public class PrototypeRequest {

    /** Natural language query, 1-1000 chars. Validated manually in PrototypeController. */
    private String query;

    /** Optional power-user overrides, e.g. {"mass": 1.0}. Not applied in this slice. */
    private Map<String, Double> parameterOverrides;

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }

    public Map<String, Double> getParameterOverrides() {
        return parameterOverrides;
    }

    public void setParameterOverrides(Map<String, Double> parameterOverrides) {
        this.parameterOverrides = parameterOverrides;
    }
}
